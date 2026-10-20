"""Bloqueia CPF e número de cartão (PAN) em arquivos versionados.

Executado no CI (job `dados-pessoais`). Só considera CPFs com dígitos
verificadores válidos e PANs que passam no algoritmo de Luhn, para evitar
falso positivo com IDs e telefones. Os valores encontrados são mascarados
na saída: o próprio log do CI não pode expor dado pessoal.

Para um falso positivo comprovado, inclua `dados-pessoais:ignorar` na linha.

Uso: python tools/ci/verificar_dados_pessoais.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

MARCADOR_IGNORAR = "dados-pessoais:ignorar"
TAMANHO_MAXIMO_BYTES = 2_000_000

# Massa sintética de homologação: reproduz de propósito problemas da produção
# (ex: CPF colado em história do backlog). Não é código nem fixture de teste.
CAMINHOS_EXCLUIDOS = ("tools/seed/",)

CPF = re.compile(r"(?<![\d.])(\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})(?![\d-])")
PAN = re.compile(r"(?<!\d)(\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4})(?!\d)")


def cpf_valido(numero: str) -> bool:
    digitos = [int(d) for d in re.sub(r"\D", "", numero)]
    if len(digitos) != 11 or len(set(digitos)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(d * peso for d, peso in zip(digitos[:tamanho], range(tamanho + 1, 1, -1)))
        verificador = (soma * 10) % 11 % 10
        if verificador != digitos[tamanho]:
            return False
    return True


def pan_valido(numero: str) -> bool:
    digitos = [int(d) for d in re.sub(r"\D", "", numero)]
    if len(set(digitos)) == 1:
        return False
    soma = 0
    for posicao, digito in enumerate(reversed(digitos)):
        if posicao % 2 == 1:
            digito *= 2
            if digito > 9:
                digito -= 9
        soma += digito
    return soma % 10 == 0


def mascarar(numero: str) -> str:
    limpo = re.sub(r"\D", "", numero)
    return "*" * (len(limpo) - 2) + limpo[-2:]


def arquivos_versionados() -> list[Path]:
    # Comando fixo, sem entrada externa.
    saida = subprocess.run(  # nosec B603,B607
        ["git", "ls-files", "-z"], capture_output=True, check=True
    ).stdout
    nomes = [nome for nome in saida.decode().split("\0") if nome]
    return [Path(nome) for nome in nomes if not nome.startswith(CAMINHOS_EXCLUIDOS)]


def verificar_arquivo(caminho: Path) -> list[str]:
    if not caminho.is_file() or caminho.stat().st_size > TAMANHO_MAXIMO_BYTES:
        return []
    try:
        linhas = caminho.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []

    achados = []
    for numero_linha, linha in enumerate(linhas, start=1):
        if MARCADOR_IGNORAR in linha:
            continue
        for match in CPF.finditer(linha):
            if cpf_valido(match.group(1)):
                achados.append(f"{caminho}:{numero_linha}: CPF {mascarar(match.group(1))}")
        for match in PAN.finditer(linha):
            if pan_valido(match.group(1)):
                achados.append(f"{caminho}:{numero_linha}: PAN {mascarar(match.group(1))}")
    return achados


def main() -> int:
    achados = [
        achado for arquivo in arquivos_versionados() for achado in verificar_arquivo(arquivo)
    ]
    if not achados:
        print("Nenhum CPF ou PAN encontrado nos arquivos versionados.")
        return 0

    print(f"{len(achados)} possível(is) dado(s) pessoal(is) em arquivos versionados:")
    for achado in achados:
        print(f"  {achado}")
    print(
        "\nRemova o dado ou use um valor inválido (ex: CPF com dígito verificador errado). "
        f"Para falso positivo comprovado, inclua '{MARCADOR_IGNORAR}' na linha."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
