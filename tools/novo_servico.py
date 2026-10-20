"""Cria um serviço em services/ a partir de templates/servico-python.

Uso: python tools/novo_servico.py saldo-service
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
TEMPLATE = RAIZ / "templates" / "servico-python"
NOME_VALIDO = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")
IGNORAR = shutil.ignore_patterns(
    ".venv", "__pycache__", "*.egg-info", ".pytest_cache", ".ruff_cache", ".coverage"
)
EXTENSOES_TEXTO = {".py", ".toml", ".md", ".feature"}


def personalizar(texto: str, nome: str, pacote: str) -> str:
    texto = texto.replace('name = "servico"', f'name = "{nome}"')
    texto = texto.replace('title="servico"', f'title="{nome}"')
    texto = texto.replace("# servico-python", f"# {nome}")
    return re.sub(r"\bservico\b(?!-)", pacote, texto)


def main(argv: list[str]) -> int:
    if len(argv) != 2 or not NOME_VALIDO.fullmatch(argv[1]):
        print("Uso: python tools/novo_servico.py <nome-em-kebab-case>   (ex: saldo-service)")
        return 2

    nome = argv[1]
    pacote = nome.replace("-", "_")
    destino = RAIZ / "services" / nome
    if destino.exists():
        print(f"{destino.relative_to(RAIZ)} já existe.")
        return 1

    shutil.copytree(TEMPLATE, destino, ignore=IGNORAR)
    (destino / "src" / "servico").rename(destino / "src" / pacote)
    for arquivo in destino.rglob("*"):
        if arquivo.is_file() and (
            arquivo.suffix in EXTENSOES_TEXTO or arquivo.name == "Dockerfile"
        ):
            texto = arquivo.read_text(encoding="utf-8")
            arquivo.write_text(personalizar(texto, nome, pacote), encoding="utf-8")

    print(f"Serviço criado em services/{nome} (pacote Python: {pacote}).")
    print("Próximos passos: ajustar o README do serviço e escrever as regras em domain/.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
