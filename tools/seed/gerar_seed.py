"""Gera os dados de homologação da Benefy (CSVs) e o script de carga do Postgres.

Uso, na raiz do repositório:
    python tools/seed/gerar_seed.py

Semente fixa: rodar de novo gera exatamente os mesmos dados.
Tudo é sintético. Nomes, CPFs e CNPJs são inventados (com dígito verificador
válido só para servirem de dado de teste).
"""

from __future__ import annotations

import csv
import heapq
import json
import random
import unicodedata
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PASTA_SEED = RAIZ / "database" / "seed"
ARQ_CARGA = RAIZ / "database" / "init" / "02_carga.sql"
ARQ_WORK_ITEMS = Path(__file__).resolve().parent / "work_items.json"

SP = timezone(timedelta(hours=-3))
CORTE = datetime(2026, 10, 16, 23, 59, 59, tzinfo=SP)  # "hoje" no banco de homologação
MESES_OPERACAO = [date(2026, 8, 1), date(2026, 9, 1), date(2026, 10, 1)]

rng = random.Random(20261017)

# ---------------------------------------------------------------------------
# Tabelas de saída (a ordem aqui é a ordem de carga, respeitando as FKs)
# ---------------------------------------------------------------------------

COLUNAS = {
    "rh.departamentos": ["id", "nome", "centro_custo", "gestor_id"],
    "rh.cargos": ["id", "titulo", "trilha", "nivel", "faixa_min_centavos", "faixa_max_centavos"],
    "rh.funcionarios": ["id", "matricula", "nome", "email", "cpf", "data_nascimento",
                        "data_admissao", "data_desligamento", "departamento_id", "cargo_id",
                        "gestor_id", "salario_base_centavos", "modelo_trabalho", "cidade", "uf",
                        "status"],
    "rh.squads": ["id", "nome", "slug", "linguagem_principal", "tech_lead_id",
                  "product_owner_id", "engineering_manager_id"],
    "rh.squad_membros": ["squad_id", "funcionario_id", "papel"],
    "rh.ferias": ["id", "funcionario_id", "inicio", "fim", "status"],
    "rh.avaliacoes_desempenho": ["id", "funcionario_id", "ciclo", "avaliador_id", "nota",
                                 "comentario"],
    "rh.folha_pagamento": ["id", "funcionario_id", "competencia", "salario_base_centavos",
                           "bonus_centavos", "beneficios_centavos", "encargos_centavos",
                           "custo_total_centavos"],
    "comercial.planos": ["codigo", "nome", "mensalidade_por_colaborador_centavos", "descricao"],
    "beneficios.tipos_carteira": ["codigo", "nome", "descricao"],
    "comercial.empresas_clientes": ["id", "razao_social", "cnpj", "setor", "porte", "cidade",
                                    "uf", "plano_codigo", "fallback_livre",
                                    "limite_diario_centavos", "status", "cliente_desde",
                                    "executivo_conta_id"],
    "comercial.empresa_carteiras": ["empresa_id", "carteira_codigo", "habilitada",
                                    "credito_mensal_padrao_centavos"],
    "beneficios.mcc": ["codigo", "descricao", "carteira_codigo", "bloqueado"],
    "beneficios.estabelecimentos": ["id", "nome", "cnpj", "mcc", "cidade", "uf", "parceiro"],
    "beneficios.colaboradores": ["id", "empresa_id", "nome", "cpf", "email", "telefone",
                                 "data_nascimento", "data_desligamento", "status", "criado_em"],
    "beneficios.cartoes": ["id", "colaborador_id", "final_cartao", "status", "emitido_em",
                           "validade", "bloqueado_em"],
    "beneficios.pedidos_credito": ["id", "empresa_id", "competencia", "data_credito", "status",
                                   "valor_total_centavos"],
    "beneficios.pedido_credito_itens": ["pedido_id", "colaborador_id", "carteira_codigo",
                                        "valor_centavos"],
    "beneficios.transacoes": ["id", "colaborador_id", "cartao_id", "estabelecimento_id", "mcc",
                              "valor_centavos", "data_hora", "status", "motivo_negacao"],
    "beneficios.estornos": ["id", "transacao_id", "valor_centavos", "data_hora",
                            "solicitado_por"],
    "beneficios.lancamentos": ["id", "colaborador_id", "carteira_codigo", "tipo",
                               "valor_centavos", "origem_tipo", "origem_id", "data_hora"],
    "beneficios.carteiras": ["colaborador_id", "carteira_codigo", "saldo_centavos",
                             "atualizado_em"],
    "financeiro.fornecedores": ["id", "nome", "categoria"],
    "financeiro.despesas": ["id", "fornecedor_id", "centro_custo", "competencia",
                            "valor_centavos", "descricao"],
    "financeiro.faturas": ["id", "empresa_id", "competencia", "valor_creditos_centavos",
                           "valor_mensalidade_centavos", "valor_total_centavos", "vencimento",
                           "status", "pago_em"],
    "atendimento.tickets": ["id", "aberto_em", "canal", "solicitante_tipo", "colaborador_id",
                            "empresa_id", "categoria", "prioridade", "status", "assunto",
                            "descricao", "atendente_id", "resolvido_em", "nota_satisfacao"],
    "engenharia.servicos": ["nome", "squad_id", "linguagem", "repositorio", "criticidade",
                            "situacao", "descricao"],
    "engenharia.work_items": ["id", "tipo", "squad_slug", "titulo", "descricao",
                              "criterios_aceite", "estado", "autor_id", "responsavel_id",
                              "criado_em"],
    "engenharia.incidentes": ["id", "titulo", "severidade", "servico", "inicio", "fim",
                              "status", "resumo", "causa_raiz"],
}
LINHAS: dict[str, list[list]] = {t: [] for t in COLUNAS}


def add(tabela: str, *valores) -> None:
    LINHAS[tabela].append(list(valores))


# ---------------------------------------------------------------------------
# Utilitários
# ---------------------------------------------------------------------------

NOMES = [
    "Ana", "Bruno", "Camila", "Diego", "Eduarda", "Felipe", "Gabriela", "Henrique", "Isabela",
    "João", "Larissa", "Marcelo", "Natália", "Paulo", "Patrícia", "Rafaela", "Sabrina", "Thiago",
    "Vanessa", "William", "Yasmin", "Leonardo", "Mariana", "Caio", "Beatriz", "Carlos",
    "Daniela", "Emerson", "Fábio", "Giovana", "Heloísa", "Igor", "Jéssica", "Kaique", "Letícia",
    "Matheus", "Nicole", "Pedro", "Renata", "Samuel", "Tatiane", "Vinícius", "Alice", "Arthur",
    "Bianca", "Cecília", "Davi", "Elisa", "Gustavo", "Helena", "Júlia", "Lucas", "Luana",
    "Murilo", "Priscila", "Ricardo", "Simone", "Tiago", "Valéria", "Wagner",
]
SOBRENOMES = [
    "Silva", "Souza", "Oliveira", "Santos", "Pereira", "Costa", "Rodrigues", "Almeida",
    "Nascimento", "Lima", "Araújo", "Fernandes", "Carvalho", "Gomes", "Martins", "Rocha",
    "Ribeiro", "Alves", "Monteiro", "Mendes", "Barros", "Freitas", "Barbosa", "Pinto", "Moura",
    "Cavalcanti", "Dias", "Castro", "Campos", "Cardoso", "Teixeira", "Moreira", "Nogueira",
    "Correia", "Batista", "Vieira", "Sato", "Tanaka", "Yamamoto", "Nakamura", "Ferraz", "Prado",
]
PALAVRAS = [
    "Horizonte", "Vale Verde", "Atlântico", "Primavera", "Ipê", "Aurora", "Serra Mar",
    "Bandeirantes", "Nova Era", "Monte Azul", "Rio Claro", "Sol Nascente", "Cristal", "Pioneira",
    "Andorinha", "Delta", "Órion", "Vitória", "Estrela", "Jacarandá", "Boa Vista", "Paineira",
    "Alvorada", "Granito", "Coqueiral", "Mirante", "Itapuã", "Seriema", "Jatobá", "Cerrado",
    "Maré Alta", "Pinheiral", "Laranjeiras", "Quaresmeira", "Esmeralda", "Bom Jardim",
]
CIDADES = [
    ("São Paulo", "SP", 40), ("Campinas", "SP", 6), ("Santo André", "SP", 4),
    ("Guarulhos", "SP", 4), ("Sorocaba", "SP", 3), ("Ribeirão Preto", "SP", 3),
    ("Rio de Janeiro", "RJ", 8), ("Belo Horizonte", "MG", 6), ("Curitiba", "PR", 5),
    ("Porto Alegre", "RS", 4), ("Florianópolis", "SC", 3), ("Recife", "PE", 3),
    ("Salvador", "BA", 3), ("Goiânia", "GO", 2), ("Fortaleza", "CE", 2),
]
CIDADES_REMOTO = [("Campinas", "SP"), ("Curitiba", "PR"), ("Belo Horizonte", "MG"),
                  ("Recife", "PE"), ("Florianópolis", "SC"), ("Porto Alegre", "RS"),
                  ("Rio de Janeiro", "RJ"), ("Fortaleza", "CE")]

_cpfs: set[str] = set()
_cnpjs: set[str] = set()


def cpf() -> str:
    while True:
        base = [rng.randint(0, 9) for _ in range(9)]
        for inicio in (10, 11):
            soma = sum(d * p for d, p in zip(base, range(inicio, 1, -1)))
            resto = soma % 11
            base.append(0 if resto < 2 else 11 - resto)
        d = "".join(map(str, base))
        valor = f"{d[:3]}.{d[3:6]}.{d[6:9]}-{d[9:]}"
        if valor not in _cpfs and len(set(d)) > 1:
            _cpfs.add(valor)
            return valor


def cnpj() -> str:
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    while True:
        base = [rng.randint(0, 9) for _ in range(8)] + [0, 0, 0, 1]
        for pesos in (pesos1, [6] + pesos1):
            resto = sum(d * p for d, p in zip(base, pesos)) % 11
            base.append(0 if resto < 2 else 11 - resto)
        d = "".join(map(str, base))
        valor = f"{d[:2]}.{d[2:5]}.{d[5:8]}/{d[8:12]}-{d[12:]}"
        if valor not in _cnpjs:
            _cnpjs.add(valor)
            return valor


def sem_acento(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def nome_pessoa() -> str:
    s1, s2 = rng.sample(SOBRENOMES, 2)
    return f"{rng.choice(NOMES)} {s1} {s2}"


def telefone() -> str:
    ddd = rng.choice(["11", "11", "11", "19", "21", "31", "41", "51", "81"])
    return f"({ddd}) 9{rng.randint(1000, 9999)}-{rng.randint(1000, 9999)}"


def data_entre(inicio: date, fim: date) -> date:
    return inicio + timedelta(days=rng.randint(0, (fim - inicio).days))


def data_admissao_aleatoria() -> date:
    # A empresa cresceu muito nos últimos anos: viesa para datas recentes
    inicio, fim = date(2019, 6, 1), date(2026, 9, 15)
    return inicio + timedelta(days=int((fim - inicio).days * rng.random() ** 0.6))


def cidade_ponderada() -> tuple[str, str]:
    cidade, uf, _ = rng.choices(CIDADES, weights=[c[2] for c in CIDADES])[0]
    return cidade, uf


def arred(valor_reais: float, passo: int = 50) -> int:
    """Arredonda um valor em reais para o passo e devolve em centavos."""
    return int(round(valor_reais / passo) * passo) * 100


def ultimo_dia(mes: date) -> date:
    proximo = date(mes.year + mes.month // 12, mes.month % 12 + 1, 1)
    return proximo - timedelta(days=1)


def meses(inicio: date, fim: date) -> list[date]:
    lista, atual = [], inicio
    while atual <= fim:
        lista.append(atual)
        atual = date(atual.year + atual.month // 12, atual.month % 12 + 1, 1)
    return lista


# ---------------------------------------------------------------------------
# RH
# ---------------------------------------------------------------------------

CARGOS = [
    ("CEO", "Executiva", "C-Level", 75000, 95000),
    ("CTO", "Executiva", "C-Level", 70000, 90000),
    ("CFO", "Executiva", "C-Level", 68000, 88000),
    ("Diretor(a) Jurídico(a) e de Compliance", "Executiva", "C-Level", 60000, 80000),
    ("Head", "Gestão", "Head", 40000, 58000),
    ("CISO", "Gestão", "Head", 40000, 58000),
    ("Engineering Manager", "Gestão", "Gerente", 28000, 38000),
    ("Gerente", "Gestão", "Gerente", 18000, 27000),
    ("Coordenador(a)", "Gestão", "Coordenação", 11000, 16000),
    ("Supervisor(a) de Atendimento", "Atendimento", "Supervisão", 6000, 8500),
    ("AI Orchestrator", "Engenharia", "Especialista", 30000, 40000),
    ("Arquiteto(a) de Software", "Engenharia", "Staff", 26000, 34000),
    ("Tech Lead", "Engenharia", "Liderança técnica", 22000, 30000),
    ("Engenheiro(a) de Software Júnior", "Engenharia", "Júnior", 6500, 9500),
    ("Engenheiro(a) de Software Pleno", "Engenharia", "Pleno", 10000, 15000),
    ("Engenheiro(a) de Software Sênior", "Engenharia", "Sênior", 16000, 23000),
    ("AI Engineer Júnior", "Engenharia", "Júnior", 7000, 10000),
    ("AI Engineer Sênior", "Engenharia", "Sênior", 18000, 25000),
    ("Engenheiro(a) de Plataforma Sênior", "Engenharia", "Sênior", 17000, 24000),
    ("Analista de QA Pleno", "Engenharia", "Pleno", 8000, 12000),
    ("Engenheiro(a) de Dados Pleno", "Dados", "Pleno", 11000, 16000),
    ("Cientista de Dados Sênior", "Dados", "Sênior", 17000, 24000),
    ("Analista de Dados Pleno", "Dados", "Pleno", 9000, 13000),
    ("Product Manager Sênior", "Produto", "Sênior", 18000, 26000),
    ("Product Owner", "Produto", "Pleno", 12000, 18000),
    ("Product Designer Pleno", "Produto", "Pleno", 9000, 14000),
    ("Engenheiro(a) de Segurança Sênior", "Segurança", "Sênior", 18000, 25000),
    ("Analista de Segurança Pleno", "Segurança", "Pleno", 10000, 15000),
    ("Encarregado(a) de Dados (DPO)", "Jurídico", "Especialista", 20000, 27000),
    ("Advogado(a) Pleno", "Jurídico", "Pleno", 9000, 14000),
    ("Analista de Compliance Pleno", "Jurídico", "Pleno", 7000, 11000),
    ("Controller", "Financeiro", "Especialista", 15000, 21000),
    ("Analista Financeiro Pleno", "Financeiro", "Pleno", 6000, 9000),
    ("Executivo(a) de Contas", "Comercial", "Pleno", 8000, 14000),
    ("SDR", "Comercial", "Júnior", 3500, 5000),
    ("Customer Success Manager", "Atendimento", "Pleno", 7000, 11000),
    ("Analista de Atendimento Júnior", "Atendimento", "Júnior", 2800, 3600),
    ("Analista de Atendimento Pleno", "Atendimento", "Pleno", 3800, 5000),
    ("Analista de Operações Pleno", "Operações", "Pleno", 4500, 7000),
    ("Analista de RH Pleno", "Pessoas", "Pleno", 5500, 8000),
    ("Business Partner de RH", "Pessoas", "Sênior", 9000, 13000),
    ("Analista de Marketing Pleno", "Marketing", "Pleno", 6000, 9000),
    ("Designer Gráfico Pleno", "Marketing", "Pleno", 6000, 9000),
    ("Assistente Administrativo", "Administrativo", "Júnior", 3000, 4200),
    ("Assistente Executivo(a)", "Administrativo", "Pleno", 6000, 9000),
]
CARGO = {c[0]: (i, c[3], c[4]) for i, c in enumerate(CARGOS, start=1)}

DEPTOS = [
    (1, "Diretoria Executiva", "CC-DIR"), (2, "Tecnologia", "CC-TEC"), (3, "Dados", "CC-DAD"),
    (4, "Produto", "CC-PRO"), (5, "Segurança da Informação", "CC-SEG"),
    (6, "Jurídico e Compliance", "CC-JUR"), (7, "Financeiro", "CC-FIN"),
    (8, "Comercial", "CC-COM"), (9, "Atendimento e Customer Success", "CC-ATD"),
    (10, "Operações", "CC-OPE"), (11, "Pessoas", "CC-PES"), (12, "Marketing", "CC-MKT"),
    (13, "Administrativo e Facilities", "CC-ADM"),
]
DEPTO_TECNICO = {2, 3, 4, 5}

funcs: list[dict] = []
func_por_nome: dict[str, int] = {}
_nomes_func: set[str] = set()
_emails: set[str] = set()
gestor_depto: dict[int, int] = {}


def F(nome: str | None, depto: int, cargo: str, gestor: int | None, adm: date | None = None,
      salario_reais: int | None = None, cidade: tuple[str, str] | None = None,
      modelo: str | None = None) -> int:
    fid = len(funcs) + 1
    gerado = nome is None
    while nome is None or (gerado and nome in _nomes_func):
        nome = nome_pessoa()
    _nomes_func.add(nome)
    cargo_id, minimo, maximo = CARGO[cargo]
    if salario_reais is None:
        salario = arred(rng.randint(minimo, maximo))
    else:
        salario = salario_reais * 100
    partes = sem_acento(nome).lower().split()
    email = f"{partes[0]}.{partes[-1]}@benefy.com.br"
    n = 2
    while email in _emails:
        email = f"{partes[0]}.{partes[-1]}{n}@benefy.com.br"
        n += 1
    _emails.add(email)
    if modelo is None:
        if depto == 9:
            modelo = "PRESENCIAL" if rng.random() < 0.6 else "HIBRIDO"
        elif depto in DEPTO_TECNICO and rng.random() < 0.35:
            modelo = "REMOTO"
        else:
            modelo = "HIBRIDO"
    if cidade is None:
        cidade = rng.choice(CIDADES_REMOTO) if modelo == "REMOTO" else ("São Paulo", "SP")
    funcs.append({
        "id": fid, "matricula": f"B{fid:05d}", "nome": nome, "email": email, "cpf": cpf(),
        "nascimento": data_entre(date(1968, 1, 1), date(2003, 12, 31)),
        "admissao": adm or data_admissao_aleatoria(), "desligamento": None, "depto": depto,
        "cargo": cargo, "cargo_id": cargo_id, "gestor": gestor, "salario": salario,
        "modelo": modelo, "cidade": cidade[0], "uf": cidade[1], "status": "ATIVO",
    })
    func_por_nome[nome] = fid
    return fid


def gerar_rh() -> dict:
    # Diretoria
    marina = F("Marina Okada", 1, "CEO", None, date(2019, 3, 11), 92000)
    rafael = F("Rafael Duarte", 2, "CTO", marina, date(2019, 3, 11), 88000)
    helena = F("Helena Prado", 7, "CFO", marina, date(2021, 6, 1), 80000)
    sandra = F("Sandra Lemos", 6, "Diretor(a) Jurídico(a) e de Compliance", marina,
               date(2020, 9, 14), 72000)
    for _ in range(2):
        F(None, 1, "Assistente Executivo(a)", marina)
    gestor_depto.update({1: marina, 6: sandra, 7: helena})

    # Tecnologia
    paulo = F("Paulo Sampaio", 2, "Head", rafael, date(2020, 2, 3), 54000)
    debora = F("Débora Lins", 2, "AI Orchestrator", rafael, date(2026, 3, 2), 37000)
    gestor_depto[2] = rafael
    for _ in range(2):
        F(None, 2, "Arquiteto(a) de Software", paulo)
    ems = [F(None, 2, "Engineering Manager", paulo) for _ in range(4)]

    # Produto (POs são usados pelos squads)
    juliana = F("Juliana Ramos", 4, "Head", marina, date(2020, 4, 6), 50000)
    gestor_depto[4] = juliana
    pos_nomeados = {n: F(n, 4, "Product Owner", juliana) for n in
                    ("Bianca Teixeira", "Fernanda Alves", "Rodrigo Mendes")}
    pos_genericos = [F(None, 4, "Product Owner", juliana) for _ in range(4)]
    for _ in range(3):
        F(None, 4, "Product Manager Sênior", juliana)
    for _ in range(11):
        F(None, 4, "Product Designer Pleno", juliana)

    squads_spec = [
        (1, "Carteira & Saldo", "carteira-saldo", "Python", "Lucas Ferreira", "Bianca Teixeira", 8, 1, 0),
        (2, "Autorização", "autorizacao", "Python", None, "*", 10, 1, 0),
        (3, "Cartões", "cartoes", "Java", "Ana Beatriz Costa", "*", 7, 1, 1),
        (4, "Faturamento & Legado", "faturamento", "Java", None, "*", 7, 1, 1),
        (5, "Portal RH", "portal-rh", "TypeScript", None, "Fernanda Alves", 8, 1, 2),
        (6, "App do Colaborador", "app-colaborador", "Kotlin e Swift", None, "Rodrigo Mendes", 13, 2, 2),
        (7, "Antifraude", "antifraude", "Python", "Igor Santana", "*", 6, 1, 3),
        (8, "Plataforma", "plataforma", "Terraform e Python", None, None, 8, 0, 3),
    ]
    membros_squad: list[tuple[int, int, str]] = []
    for sid, nome, slug, ling, tl_nome, po_nome, n_eng, n_qa, em_idx in squads_spec:
        em = ems[em_idx]
        tl = F(tl_nome, 2, "Tech Lead", em)
        if po_nome == "*":
            po = pos_genericos.pop()
        elif po_nome:
            po = pos_nomeados[po_nome]
        else:
            po = None
        add("rh.squads", sid, nome, slug, ling, tl, po, em)
        membros_squad.append((sid, tl, "Tech Lead"))
        if po:
            membros_squad.append((sid, po, "Product Owner"))
        for i in range(n_eng):
            if slug == "plataforma" and i < 4:
                cargo = "Engenheiro(a) de Plataforma Sênior"
            else:
                cargo = rng.choices(
                    ["Engenheiro(a) de Software Júnior", "Engenheiro(a) de Software Pleno",
                     "Engenheiro(a) de Software Sênior"], weights=[25, 45, 30])[0]
            membros_squad.append((sid, F(None, 2, cargo, em), "Engenharia"))
        for _ in range(n_qa):
            membros_squad.append((sid, F(None, 2, "Analista de QA Pleno", em), "QA"))

    andre = F("André Matsuda", 2, "AI Engineer Sênior", debora, date(2024, 2, 5), 23500)
    gustavo = F("Gustavo Henrique Silva", 2, "AI Engineer Júnior", debora, date(2026, 10, 19), 8500)
    add("rh.squads", 9, "Plataforma de IA", "plataforma-ia", "Python", andre, None, debora)
    membros_squad += [(9, debora, "AI Orchestrator"), (9, andre, "Tech Lead"),
                      (9, gustavo, "AI Engineer")]

    # Dados
    tiago = F("Tiago Moraes", 3, "Head", rafael, date(2021, 8, 2), 49000)
    gestor_depto[3] = tiago
    for cargo, n in (("Cientista de Dados Sênior", 4), ("Engenheiro(a) de Dados Pleno", 5),
                     ("Analista de Dados Pleno", 5)):
        for _ in range(n):
            F(None, 3, cargo, tiago)

    # Segurança e Jurídico
    carla = F("Carla Nunes", 5, "CISO", sandra, date(2022, 4, 4), 52000)
    gestor_depto[5] = carla
    for cargo, n in (("Engenheiro(a) de Segurança Sênior", 3), ("Analista de Segurança Pleno", 4)):
        for _ in range(n):
            F(None, 5, cargo, carla)
    F("Otávio Reis", 6, "Encarregado(a) de Dados (DPO)", sandra, date(2023, 1, 9), 25000)
    for cargo, n in (("Advogado(a) Pleno", 4), ("Analista de Compliance Pleno", 3)):
        for _ in range(n):
            F(None, 6, cargo, sandra)

    # Financeiro
    controller = F(None, 7, "Controller", helena)
    coords_fin = [F(None, 7, "Coordenador(a)", helena) for _ in range(2)]
    for _ in range(10):
        F(None, 7, "Analista Financeiro Pleno", rng.choice(coords_fin + [controller]))

    # Comercial
    renato = F("Renato Guimarães", 8, "Head", marina, date(2020, 5, 4), 52000)
    gestor_depto[8] = renato
    gerentes = [F("Marcos Vieira", 8, "Gerente", renato, date(2021, 3, 1))]
    gerentes += [F(None, 8, "Gerente", renato) for _ in range(2)]
    executivos = [F(None, 8, "Executivo(a) de Contas", rng.choice(gerentes)) for _ in range(30)]
    for _ in range(20):
        F(None, 8, "SDR", rng.choice(gerentes))

    # Atendimento e CS
    patricia = F("Patrícia Lopes", 9, "Head", marina, date(2020, 7, 6), 44000)
    gestor_depto[9] = patricia
    coords = [F(None, 9, "Coordenador(a)", patricia) for _ in range(2)]
    supervisores = [F(None, 9, "Supervisor(a) de Atendimento", rng.choice(coords))
                    for _ in range(8)]
    atendentes = []
    for cargo, n in (("Analista de Atendimento Júnior", 45), ("Analista de Atendimento Pleno", 30)):
        for _ in range(n):
            atendentes.append(F(None, 9, cargo, rng.choice(supervisores)))
    for _ in range(10):
        F(None, 9, "Customer Success Manager", rng.choice(coords))

    # Operações, Pessoas, Marketing, Administrativo
    sergio = F("Sérgio Batista", 10, "Head", helena, date(2020, 1, 13), 45000)
    gestor_depto[10] = sergio
    coords_op = [F(None, 10, "Coordenador(a)", sergio) for _ in range(2)]
    for _ in range(19):
        F(None, 10, "Analista de Operações Pleno", rng.choice(coords_op))
    claudia = F("Cláudia Freitas", 11, "Head", marina, date(2021, 2, 1), 43000)
    gestor_depto[11] = claudia
    for cargo, n in (("Business Partner de RH", 3), ("Analista de RH Pleno", 8)):
        for _ in range(n):
            F(None, 11, cargo, claudia)
    eduardo = F("Eduardo Pires", 12, "Head", marina, date(2022, 8, 1), 42000)
    gestor_depto[12] = eduardo
    for cargo, n in (("Analista de Marketing Pleno", 11), ("Designer Gráfico Pleno", 6)):
        for _ in range(n):
            F(None, 12, cargo, eduardo)
    coord_adm = F(None, 13, "Coordenador(a)", helena)
    gestor_depto[13] = coord_adm
    for _ in range(5):
        F(None, 13, "Assistente Administrativo", coord_adm)

    # Gente que já saiu da empresa
    for _ in range(23):
        depto = rng.choice([2, 2, 4, 8, 8, 9, 9, 9, 10, 12])
        cargo = {2: "Engenheiro(a) de Software Pleno", 4: "Product Designer Pleno",
                 8: "SDR", 9: "Analista de Atendimento Júnior",
                 10: "Analista de Operações Pleno", 12: "Analista de Marketing Pleno"}[depto]
        fid = F(None, depto, cargo, gestor_depto[depto], data_entre(date(2020, 1, 1), date(2024, 12, 31)))
        f = funcs[fid - 1]
        f["status"] = "DESLIGADO"
        f["desligamento"] = data_entre(date(2025, 6, 1), date(2026, 9, 30))

    # Inconsistência real da base: 2 desligados que continuam como membros de squad
    candidatos = [m for m in membros_squad if m[2] == "Engenharia"]
    for _, fid, _ in rng.sample(candidatos, 2):
        funcs[fid - 1]["status"] = "DESLIGADO"
        funcs[fid - 1]["desligamento"] = data_entre(date(2026, 7, 1), date(2026, 9, 30))

    # Afastados (licença)
    for fid in rng.sample(atendentes, 4):
        funcs[fid - 1]["status"] = "AFASTADO"

    # Inconsistência real da base: salários acima do teto da faixa
    for fid in rng.sample(executivos, 3):
        funcs[fid - 1]["salario"] = arred(rng.randint(16000, 17500))
    seniors = [f["id"] for f in funcs if f["cargo"] == "Engenheiro(a) de Software Sênior"
               and f["status"] == "ATIVO"]
    for fid in rng.sample(seniors, 2):
        funcs[fid - 1]["salario"] = arred(rng.randint(24500, 26000))

    # Admissão nunca antes da fundação nem depois do desligamento
    for f in funcs:
        if f["desligamento"] and f["admissao"] >= f["desligamento"]:
            f["admissao"] = f["desligamento"] - timedelta(days=rng.randint(200, 900))
        f["admissao"] = max(f["admissao"], date(2019, 3, 11))

    for d in DEPTOS:
        add("rh.departamentos", d[0], d[1], d[2], None)
    for i, c in enumerate(CARGOS, start=1):
        add("rh.cargos", i, c[0], c[1], c[2], c[3] * 100, c[4] * 100)
    for f in funcs:
        add("rh.funcionarios", f["id"], f["matricula"], f["nome"], f["email"], f["cpf"],
            f["nascimento"], f["admissao"], f["desligamento"], f["depto"], f["cargo_id"],
            f["gestor"], f["salario"], f["modelo"], f["cidade"], f["uf"], f["status"])
    for sid, fid, papel in membros_squad:
        add("rh.squad_membros", sid, fid, papel)

    gerar_ferias_avaliacoes_folha()
    return {"atendentes": atendentes, "executivos": executivos}


def ativo_em(f: dict, dia: date) -> bool:
    return f["admissao"] <= dia and (f["desligamento"] is None or f["desligamento"] >= dia)


def gerar_ferias_avaliacoes_folha() -> None:
    fid_ferias = 1
    for f in funcs:
        if f["status"] == "DESLIGADO" or f["admissao"] > date(2025, 9, 30):
            continue
        dias = rng.choice([15, 20, 30])
        inicio = data_entre(date(2025, 11, 3), date(2026, 9, 1))
        add("rh.ferias", fid_ferias, f["id"], inicio, inicio + timedelta(days=dias - 1), "GOZADA")
        fid_ferias += 1
        sorteio = rng.random()
        if sorteio < 0.22:
            inicio = data_entre(date(2026, 11, 3), date(2027, 2, 15))
            status = "CANCELADA" if sorteio < 0.02 else "PROGRAMADA"
            add("rh.ferias", fid_ferias, f["id"], inicio,
                inicio + timedelta(days=rng.choice([10, 15, 20]) - 1), status)
            fid_ferias += 1

    comentarios = {
        1: "Entregas abaixo do esperado. Plano de desenvolvimento aberto.",
        2: "Precisa evoluir em autonomia e qualidade das entregas.",
        3: "Atende ao esperado para o cargo.",
        4: "Supera o esperado em várias entregas. Boa referência para o time.",
        5: "Desempenho excepcional. Candidato(a) a promoção.",
    }
    ciclos = [("2025-S1", date(2025, 6, 30)), ("2025-S2", date(2025, 12, 31)),
              ("2026-S1", date(2026, 6, 30))]
    aid = 1
    for f in funcs:
        for ciclo, fim in ciclos:
            if not ativo_em(f, fim) or (fim - f["admissao"]).days < 90 or f["gestor"] is None:
                continue
            nota = rng.choices([1, 2, 3, 4, 5], weights=[3, 10, 50, 29, 8])[0]
            add("rh.avaliacoes_desempenho", aid, f["id"], ciclo, f["gestor"], nota, comentarios[nota])
            aid += 1

    folha_id = 1
    comerciais = {"Executivo(a) de Contas", "SDR"}
    for comp in meses(date(2025, 11, 1), date(2026, 9, 1)):
        for f in funcs:
            if not ativo_em(f, ultimo_dia(comp)) or f["admissao"] > ultimo_dia(comp):
                continue
            if f["desligamento"] and f["desligamento"] < comp:
                continue
            base = f["salario"] if comp >= date(2026, 3, 1) else int(f["salario"] / 1.055 / 100) * 100
            bonus = 0
            if f["cargo"] in comerciais:
                bonus = int(base * rng.uniform(0.05, 0.6) / 100) * 100
            if comp == date(2026, 2, 1):  # PLR paga em fevereiro
                bonus += int(base * rng.choice([0.8, 1.0, 1.0, 1.2, 1.5]) / 100) * 100
            beneficios = 238000 if f["depto"] != 1 else 410000
            encargos = int((base + bonus) * 0.358)
            add("rh.folha_pagamento", folha_id, f["id"], comp, base, bonus, beneficios, encargos,
                base + bonus + beneficios + encargos)
            folha_id += 1


# ---------------------------------------------------------------------------
# Comercial e catálogo de benefícios
# ---------------------------------------------------------------------------

CARTEIRAS = ["REFEICAO", "ALIMENTACAO", "MOBILIDADE", "SAUDE", "CULTURA", "LIVRE"]
TIPOS_CARTEIRA = [
    ("REFEICAO", "Refeição (VR)", "Refeições prontas em restaurantes e lanchonetes"),
    ("ALIMENTACAO", "Alimentação (VA)", "Compras de alimentos em mercados"),
    ("MOBILIDADE", "Mobilidade", "Transporte público, aplicativos e combustível"),
    ("SAUDE", "Saúde", "Farmácias, consultas e serviços de saúde"),
    ("CULTURA", "Cultura", "Livros, cinema, teatro e shows"),
    ("LIVRE", "Saldo Livre", "Uso livre, exceto MCCs bloqueados"),
]
MCCS = [
    ("4111", "Transporte urbano (metrô, trem)", "MOBILIDADE"),
    ("4121", "Táxi e aplicativos de transporte", "MOBILIDADE"),
    ("4131", "Ônibus", "MOBILIDADE"),
    ("5311", "Lojas de departamento", None),
    ("5411", "Supermercados", "ALIMENTACAO"),
    ("5422", "Açougues", "ALIMENTACAO"),
    ("5441", "Docerias", "ALIMENTACAO"),
    ("5451", "Laticínios", "ALIMENTACAO"),
    ("5462", "Padarias", "ALIMENTACAO"),
    ("5499", "Mercearias e conveniência de alimentos", "ALIMENTACAO"),
    ("5541", "Postos de combustível", "MOBILIDADE"),
    ("5542", "Bombas de combustível automáticas", "MOBILIDADE"),
    ("5651", "Vestuário", None),
    ("5732", "Eletrônicos", None),
    ("5812", "Restaurantes", "REFEICAO"),
    ("5813", "Bares e casas noturnas", None),
    ("5814", "Fast food e lanchonetes", "REFEICAO"),
    ("5912", "Farmácias", "SAUDE"),
    ("5942", "Livrarias", "CULTURA"),
    ("5995", "Pet shops", None),
    ("5999", "Varejo diverso", None),
    ("7832", "Cinemas", "CULTURA"),
    ("7922", "Teatros e shows", "CULTURA"),
    ("7995", "Apostas e jogos de azar", None),
    ("8011", "Médicos", "SAUDE"),
    ("8021", "Dentistas", "SAUDE"),
    ("8099", "Outros serviços de saúde", "SAUDE"),
]
MCC_CARTEIRA = {m[0]: (m[2] or "LIVRE") for m in MCCS}
MCC_BLOQUEADO = {"7995"}

PLANOS = [
    ("ESSENCIAL", "Essencial", 0, "VR e VA. Sem mensalidade: a receita vem da taxa dos estabelecimentos."),
    ("FLEX", "Flex", 990, "Multibenefícios: todas as carteiras, incluindo Saldo Livre."),
    ("FLEX_PLUS", "Flex Plus", 1490, "Flex + relatórios avançados, premiações e gestor de conta dedicado."),
]
MENSALIDADE = {p[0]: p[2] for p in PLANOS}

SETORES = [
    ("Varejo", ["Supermercados", "Lojas", "Comercial", "Magazine"]),
    ("Saúde", ["Hospital", "Clínicas", "Laboratório"]),
    ("Indústria", ["Indústria", "Metalúrgica", "Alimentos", "Têxtil"]),
    ("Tecnologia", ["Tecnologia", "Software", "Sistemas", "Digital"]),
    ("Logística", ["Transportes", "Logística", "Expresso"]),
    ("Educação", ["Colégio", "Instituto Educacional", "Escola"]),
    ("Construção", ["Construtora", "Engenharia", "Incorporadora"]),
    ("Serviços", ["Serviços", "Facilities", "Consultoria"]),
    ("Agronegócio", ["Agro", "Cooperativa", "Agropecuária"]),
]
MUNICIPIOS_FICTICIOS = ["Santa Aurora", "Vila Serena", "Campo Alto", "Rio Manso", "Pedra Branca"]


def gerar_comercial(executivos: list[int]) -> list[dict]:
    for p in PLANOS:
        add("comercial.planos", *p)
    for t in TIPOS_CARTEIRA:
        add("beneficios.tipos_carteira", *t)

    referencia = [
        ("Grupo Varella Comércio S.A.", "Varejo", "GRANDE", ("São Paulo", "SP"), "FLEX_PLUS", True, 150000, 900, set()),
        ("Nexo Saúde Hospitais Ltda.", "Saúde", "GRANDE", ("São Paulo", "SP"), "FLEX", False, 150000, 400, set()),
        ("Cervejaria Alto Paraná Ltda.", "Indústria", "MEDIA", ("Curitiba", "PR"), "FLEX", False, 100000, 150, {"CULTURA"}),
        ("Lumina Tech Software Ltda.", "Tecnologia", "PEQUENA", ("Florianópolis", "SC"), "FLEX", True, 300000, 60, set()),
        ("Prefeitura Municipal de Itaquara", "Setor público", "GRANDE", ("Itaquara", "SP"), "ESSENCIAL", False, 80000, 200, set()),
    ]
    empresas = []
    nomes_usados = set()
    for i in range(1, 151):
        if i <= 5:
            razao, setor, porte, cidade, plano, fallback, limite, n_colab, desabilitar = referencia[i - 1]
        else:
            if rng.random() < 0.04 and MUNICIPIOS_FICTICIOS:
                setor = "Setor público"
                razao = f"Prefeitura Municipal de {MUNICIPIOS_FICTICIOS.pop()}"
            else:
                setor, prefixos = rng.choice(SETORES)
                razao = None
                while razao is None or razao in nomes_usados:
                    sufixo = rng.choice(["Ltda.", "Ltda.", "S.A.", "Eireli"])
                    razao = f"{rng.choice(prefixos)} {rng.choice(PALAVRAS)} {sufixo}"
            porte = rng.choices(["PEQUENA", "MEDIA", "GRANDE"], weights=[55, 35, 10])[0]
            n_colab = {"PEQUENA": rng.randint(8, 25), "MEDIA": rng.randint(26, 60),
                       "GRANDE": rng.randint(61, 110)}[porte]
            cidade = cidade_ponderada()
            plano = rng.choices(["ESSENCIAL", "FLEX", "FLEX_PLUS"], weights=[30, 55, 15])[0]
            fallback = plano != "ESSENCIAL" and rng.random() < 0.45
            limite = rng.choice([150000] * 6 + [100000, 200000, 300000, 80000])
            desabilitar = set()
            if plano != "ESSENCIAL":
                if rng.random() < 0.15:
                    desabilitar.add("CULTURA")
                if rng.random() < 0.10:
                    desabilitar.add("MOBILIDADE")
        nomes_usados.add(razao)
        emp_id = f"EMP-{i:04d}"
        habilitadas = {"REFEICAO", "ALIMENTACAO"} if plano == "ESSENCIAL" else set(CARTEIRAS)
        habilitadas -= desabilitar
        creditos = {
            "REFEICAO": arred(rng.randint(600, 1300), 10),
            "ALIMENTACAO": arred(rng.randint(300, 900), 10),
            "MOBILIDADE": arred(rng.randint(150, 400), 10),
            "SAUDE": arred(rng.randint(80, 200), 10),
            "CULTURA": arred(rng.randint(50, 150), 10),
            "LIVRE": arred(rng.choice([100, 150, 200, 300, 400]), 10),
        }
        empresas.append({
            "id": emp_id, "razao": razao, "setor": setor, "porte": porte, "cidade": cidade,
            "plano": plano, "fallback": fallback, "limite": limite, "n_colab": n_colab,
            "habilitadas": habilitadas, "creditos": creditos, "status": "ATIVA",
            "desde": date(2019, 9, 2) if i == 1 else data_entre(date(2019, 9, 1), date(2026, 6, 30)),
        })

    for e in rng.sample(empresas[5:], 8)[:4]:
        e["status"] = "SUSPENSA"
    for e in [x for x in rng.sample(empresas[5:], 12) if x["status"] == "ATIVA"][:4]:
        e["status"] = "CANCELADA"

    for e in empresas:
        add("comercial.empresas_clientes", e["id"], e["razao"], cnpj(), e["setor"], e["porte"],
            e["cidade"][0], e["cidade"][1], e["plano"], e["fallback"], e["limite"], e["status"],
            e["desde"], rng.choice(executivos))
        for c in CARTEIRAS:
            hab = c in e["habilitadas"]
            add("comercial.empresa_carteiras", e["id"], c, hab, e["creditos"][c] if hab else 0)
    return empresas


NOMES_LOJA = {
    "5812": ["Restaurante {p}", "Cantina {p}", "Bistrô {p}", "Churrascaria {p}", "Cozinha {p}"],
    "5814": ["Lanchonete {p}", "Burger {p}", "Pastelaria {p}", "Açaí {p}"],
    "5411": ["Supermercado {p}", "Mercado {p}", "Atacadão {p}"],
    "5422": ["Açougue {p}", "Casa de Carnes {p}"],
    "5441": ["Doceria {p}", "Confeitaria {p}"],
    "5451": ["Laticínios {p}", "Queijaria {p}"],
    "5462": ["Padaria {p}", "Panificadora {p}"],
    "5499": ["Empório {p}", "Mercearia {p}", "Hortifruti {p}"],
    "4111": ["Metrô Linha {p}", "Trens Metropolitanos {p}"],
    "4121": ["VaiJá Mobilidade {p}", "Táxi {p}"],
    "4131": ["Viação {p}", "Expresso {p}"],
    "5541": ["Posto {p}", "Auto Posto {p}"],
    "5542": ["Bomba Rápida {p}"],
    "5912": ["Farmácia {p}", "Drogaria {p}"],
    "8011": ["Clínica {p}", "Consultório {p}"],
    "8021": ["Odonto {p}", "Clínica Odontológica {p}"],
    "8099": ["Laboratório {p}", "Centro de Fisioterapia {p}"],
    "5942": ["Livraria {p}"],
    "7832": ["Cine {p}"],
    "7922": ["Teatro {p}", "Casa de Shows {p}"],
    "5311": ["Magazine {p}", "Lojas {p}"],
    "5651": ["Moda {p}", "Boutique {p}"],
    "5732": ["Eletrônicos {p}", "Tech Store {p}"],
    "5995": ["Pet Shop {p}"],
    "5999": ["Bazar {p}", "Utilidades {p}"],
    "5813": ["Bar {p}", "Boteco {p}"],
    "7995": ["Bet {p}", "Aposta {p}"],
}
QTD_LOJAS = {"5812": 220, "5814": 110, "5411": 90, "5422": 25, "5441": 20, "5451": 10,
             "5462": 60, "5499": 30, "4111": 3, "4121": 4, "4131": 8, "5541": 50, "5542": 10,
             "5912": 60, "8011": 25, "8021": 20, "8099": 15, "5942": 12, "7832": 10, "7922": 8,
             "5311": 15, "5651": 40, "5732": 15, "5995": 20, "5999": 30, "5813": 40, "7995": 3}


def gerar_estabelecimentos() -> dict[str, list[str]]:
    for codigo, desc, carteira in MCCS:
        add("beneficios.mcc", codigo, desc, carteira, codigo in MCC_BLOQUEADO)
    por_mcc: dict[str, list[str]] = {}
    seq = 1
    usados = set()
    for mcc, qtd in QTD_LOJAS.items():
        for _ in range(qtd):
            nome = None
            while nome is None or nome in usados:
                nome = rng.choice(NOMES_LOJA[mcc]).format(p=rng.choice(PALAVRAS))
                if nome in usados:
                    nome = f"{nome} {rng.choice(['II', 'Centro', 'Shopping', 'Express', 'Jardins', 'Vila Nova'])}"
            usados.add(nome)
            est_id = f"EST-{seq:05d}"
            cidade = ("Online", "SP") if mcc == "7995" else cidade_ponderada()
            parceiro = mcc in ("5812", "5814") and rng.random() < 0.15
            add("beneficios.estabelecimentos", est_id, nome, cnpj(), mcc, cidade[0], cidade[1], parceiro)
            por_mcc.setdefault(mcc, []).append(est_id)
            seq += 1
    return por_mcc


# ---------------------------------------------------------------------------
# Operação: colaboradores, créditos, transações, extrato
# ---------------------------------------------------------------------------

CATEGORIAS = {
    # categoria: (mccs, valor mínimo, valor máximo em reais, peso)
    "REFEICAO": (["5812", "5812", "5812", "5814", "5814"], 18, 95, 50),
    "ALIMENTACAO": (["5411"] * 5 + ["5422", "5441", "5451", "5462", "5462", "5499"], 15, 420, 18),
    "MOBILIDADE": (["4111", "4121", "4121", "4131", "5541", "5541", "5542"], 5, 250, 10),
    "SAUDE": (["5912"] * 4 + ["8011", "8021", "8099"], 15, 220, 6),
    "CULTURA": (["5942", "7832", "7832", "7922"], 25, 160, 3),
    "LIVRE": (["5311", "5651", "5732", "5995", "5999", "5813"], 20, 450, 12),
    "APOSTA": (["7995"], 20, 200, 1),
}
CAT_NOMES = list(CATEGORIAS)
CAT_PESOS = [CATEGORIAS[c][3] for c in CAT_NOMES]


class Operacao:
    def __init__(self, empresas: list[dict], lojas: dict[str, list[str]]):
        self.empresas = empresas
        self.lojas = lojas
        self.colabs: list[dict] = []
        self.seq_trx = 1
        self.seq_lanc = 1
        self.seq_estorno = 1
        self.lancamentos: list[list] = []
        self.apostas_aprovadas_legado = 0
        self.negadas: list[dict] = []
        self.estornos_feitos: list[dict] = []
        self.colabs_saldo_divergente: list[dict] = []

    # --- cadastro -----------------------------------------------------------
    def gerar_colaboradores(self) -> None:
        seq_c = 1
        for e in self.empresas:
            inicio_cadastro = max(e["desde"], date(2025, 1, 1))
            for _ in range(e["n_colab"]):
                nome = nome_pessoa()
                partes = sem_acento(nome).lower().split()
                criado = data_entre(inicio_cadastro, date(2026, 7, 31))
                if rng.random() < 0.05:
                    criado = data_entre(date(2026, 8, 2), date(2026, 10, 10))
                c = {
                    "id": f"COL-{seq_c:06d}", "empresa": e, "nome": nome, "cpf": cpf(),
                    "email": f"{partes[0]}.{partes[-1]}{rng.randint(1, 99)}@exemplo.com.br"
                    if rng.random() < 0.75 else None,
                    "telefone": telefone() if rng.random() < 0.7 else None,
                    "nascimento": data_entre(date(1962, 1, 1), date(2006, 6, 30)),
                    "criado": datetime.combine(criado, time(rng.randint(8, 18), rng.randint(0, 59)), SP),
                    "desligamento": None,
                }
                if criado < date(2026, 9, 1) and rng.random() < 0.03:
                    c["desligamento"] = data_entre(max(criado + timedelta(days=20), date(2026, 8, 5)),
                                                   date(2026, 10, 10))
                self.colabs.append(c)
                seq_c += 1

        # Inconsistência real da base: mesma pessoa cadastrada duas vezes na mesma empresa
        varella = [c for c in self.colabs if c["empresa"]["id"] == "EMP-0001"]
        for original in rng.sample(varella, 3):
            dup = dict(original)
            dup["id"] = f"COL-{seq_c:06d}"
            dup["nome"] = original["nome"].upper()
            dup["email"] = None
            dup["criado"] = original["criado"] + timedelta(days=rng.randint(30, 90))
            if dup["criado"] > datetime(2026, 7, 31, tzinfo=SP):
                dup["criado"] = datetime(2026, 7, 20, 10, 0, tzinfo=SP)
            self.colabs.append(dup)
            seq_c += 1

        seq_cartao = 1
        for c in self.colabs:
            emitido = (c["criado"] + timedelta(days=rng.randint(2, 6))).date()
            cartao = {"id": f"CRT-{seq_cartao:06d}", "final": f"{rng.randint(0, 9999):04d}",
                      "status": "ATIVO", "emitido": emitido, "bloqueado_em": None}
            seq_cartao += 1
            c["cartoes"] = [cartao]
            c["bloqueio_em"] = None
            sorteio = rng.random()
            if sorteio < 0.025:
                t = datetime.combine(data_entre(date(2026, 8, 10), date(2026, 10, 15)),
                                     time(rng.randint(7, 22), rng.randint(0, 59)), SP)
                cartao["status"], cartao["bloqueado_em"] = "BLOQUEADO", t
                c["bloqueio_em"] = t
            elif sorteio < 0.035:
                # Perdeu o cartão e pediu segunda via
                t = datetime.combine(data_entre(date(2026, 8, 10), date(2026, 10, 5)),
                                     time(rng.randint(7, 22), rng.randint(0, 59)), SP)
                cartao["status"], cartao["bloqueado_em"] = "CANCELADO", t
                novo = {"id": f"CRT-{seq_cartao:06d}", "final": f"{rng.randint(0, 9999):04d}",
                        "status": "ATIVO", "emitido": (t + timedelta(days=3)).date(),
                        "bloqueado_em": None, "ativo_desde": t + timedelta(days=3)}
                seq_cartao += 1
                c["cartoes"].append(novo)

        for c in self.colabs:
            add("beneficios.colaboradores", c["id"], c["empresa"]["id"], c["nome"], c["cpf"],
                c["email"], c["telefone"], c["nascimento"], c["desligamento"],
                "DESLIGADO" if c["desligamento"] else "ATIVO", c["criado"])
            for k in c["cartoes"]:
                add("beneficios.cartoes", k["id"], c["id"], k["final"], k["status"], k["emitido"],
                    date(k["emitido"].year + 5, k["emitido"].month, 1), k["bloqueado_em"])

    # --- simulação ------------------------------------------------------------
    def lancar(self, c: dict, carteira: str, tipo: str, valor: int, origem_tipo: str,
               origem_id: str, quando: datetime) -> None:
        self.lancamentos.append([self.seq_lanc, c["id"], carteira, tipo, valor, origem_tipo,
                                 origem_id, quando])
        self.seq_lanc += 1

    def cartao_em(self, c: dict, quando: datetime) -> tuple[dict, bool]:
        """Devolve o cartão que o colaborador usaria e se ele está ativo."""
        cartoes = c["cartoes"]
        if len(cartoes) == 2:
            novo = cartoes[1]
            if quando >= novo["ativo_desde"]:
                return novo, True
            antigo = cartoes[0]
            return antigo, quando < antigo["bloqueado_em"]
        k = cartoes[0]
        return k, k["bloqueado_em"] is None or quando < k["bloqueado_em"]

    def simular(self) -> None:
        pedidos: dict[tuple[str, date], dict] = {}
        for e in self.empresas:
            for mes in MESES_OPERACAO + [date(2026, 11, 1)]:
                if e["status"] == "CANCELADA" and mes > date(2026, 8, 1):
                    continue
                if mes == date(2026, 11, 1) and e["status"] != "ATIVA":
                    continue
                if mes == date(2026, 11, 1):
                    status = "PENDENTE"
                elif e["status"] == "SUSPENSA" and mes == date(2026, 10, 1):
                    status = "PENDENTE"
                else:
                    status = "CREDITADO"
                pid = f"PED-{mes:%Y%m}-{e['id'][4:]}"
                pedidos[(e["id"], mes)] = {"id": pid, "empresa": e, "mes": mes, "status": status,
                                           "total": 0, "colabs": 0}

        for c in self.colabs:
            self.simular_colaborador(c, pedidos)

        for p in pedidos.values():
            add("beneficios.pedidos_credito", p["id"], p["empresa"]["id"], p["mes"], p["mes"],
                p["status"], p["total"])
        self.pedidos = pedidos

        # Incidente INC-2026-019: eventos de lançamento perdidos na DLQ.
        # O saldo foi debitado, mas o lançamento do extrato nunca foi gravado.
        janela_ini = datetime(2026, 10, 6, 14, 2, tzinfo=SP)
        janela_fim = datetime(2026, 10, 6, 15, 41, tzinfo=SP)
        na_janela = [lanc for lanc in self.lancamentos
                     if lanc[3] == "DEBITO" and janela_ini <= lanc[7] <= janela_fim]
        por_colab = {}
        for lanc in na_janela:
            por_colab.setdefault(lanc[1], lanc)
        perdidos = rng.sample(list(por_colab.values()), min(14, len(por_colab)))
        ids_perdidos = {lanc[0] for lanc in perdidos}
        self.lancamentos = [lanc for lanc in self.lancamentos if lanc[0] not in ids_perdidos]
        mapa = {c["id"]: c for c in self.colabs}
        self.colabs_saldo_divergente = [(mapa[lanc[1]], lanc) for lanc in perdidos]

        LINHAS["beneficios.lancamentos"] = self.lancamentos

    def simular_colaborador(self, c: dict, pedidos: dict) -> None:
        e = c["empresa"]
        saldo = {k: 0 for k in CARTEIRAS}
        gasto_dia: dict[date, int] = {}
        eventos: list = []
        ordem = 0

        def push(quando: datetime, tipo: str, dados) -> None:
            nonlocal ordem
            heapq.heappush(eventos, (quando, ordem, tipo, dados))
            ordem += 1

        for mes in MESES_OPERACAO + [date(2026, 11, 1)]:
            p = pedidos.get((e["id"], mes))
            if p is None:
                continue
            dia1 = datetime.combine(mes, time(6, 0), SP)
            if c["criado"] > dia1 or (c["desligamento"] and c["desligamento"] <= mes):
                continue
            p["colabs"] += 1
            for carteira in CARTEIRAS:
                if carteira in e["habilitadas"]:
                    valor = e["creditos"][carteira]
                    add("beneficios.pedido_credito_itens", p["id"], c["id"], carteira, valor)
                    p["total"] += valor
                    if p["status"] == "CREDITADO":
                        push(dia1, "credito", (carteira, valor, p["id"]))

        # Compras
        inicio_compras = max(c["criado"], datetime(2026, 8, 1, 6, 30, tzinfo=SP))
        for mes in MESES_OPERACAO:
            ultimo = 16 if mes.month == 10 else ultimo_dia(mes).day
            n = rng.randint(6, 16) * ultimo // 31
            for _ in range(n):
                cat = rng.choices(CAT_NOMES, weights=CAT_PESOS)[0]
                if cat != "APOSTA" and cat not in e["habilitadas"] and rng.random() < 0.85:
                    cat = "REFEICAO"
                mccs, vmin, vmax, _ = CATEGORIAS[cat]
                mcc = rng.choice(mccs)
                valor = int(rng.triangular(vmin * 100, vmax * 100, vmin * 100 + (vmax - vmin) * 25))
                if cat == "REFEICAO":
                    if e["id"] == "EMP-0002" and rng.random() < 0.3:
                        hora = rng.choice([0, 1, 2, 3, 4, 23])
                    else:
                        hora = rng.randint(11, 13) if rng.random() < 0.8 else rng.randint(18, 21)
                elif cat == "MOBILIDADE":
                    hora = rng.randint(6, 21)
                else:
                    hora = rng.randint(9, 21)
                quando = datetime.combine(date(mes.year, mes.month, rng.randint(1, ultimo)),
                                          time(hora, rng.randint(0, 59), rng.randint(0, 59)), SP)
                if quando < inicio_compras or quando > CORTE:
                    continue
                if c["desligamento"] and quando.date() > c["desligamento"] + timedelta(days=90):
                    continue
                push(quando, "compra", (mcc, valor))

        negadas_cartao = 0
        ultimo_evento = c["criado"]
        while eventos:
            quando, _, tipo, dados = heapq.heappop(eventos)
            ultimo_evento = quando
            if tipo == "credito":
                carteira, valor, pid = dados
                saldo[carteira] += valor
                self.lancar(c, carteira, "CREDITO", valor, "PEDIDO_CREDITO", pid, quando)
            elif tipo == "estorno":
                trx_id, debitos = dados
                eid = f"ETN-{self.seq_estorno:06d}"
                self.seq_estorno += 1
                total = sum(v for _, v in debitos)
                add("beneficios.estornos", eid, trx_id, total, quando, "ESTABELECIMENTO")
                for carteira, v in debitos:
                    saldo[carteira] += v
                    self.lancar(c, carteira, "ESTORNO", v, "ESTORNO", eid, quando)
                self.estornos_feitos.append({"colab": c, "quando": quando, "valor": total})
            else:
                mcc, valor = dados
                cartao, cartao_ativo = self.cartao_em(c, quando)
                if not cartao_ativo:
                    negadas_cartao += 1
                    if negadas_cartao > 2:
                        continue
                status, motivo, debitos = self.autorizar(c, mcc, valor, quando, saldo, gasto_dia,
                                                         cartao_ativo)
                trx_id = f"TRX-{self.seq_trx:07d}"
                self.seq_trx += 1
                loja = rng.choice(self.lojas[mcc])
                add("beneficios.transacoes", trx_id, c["id"], cartao["id"], loja, mcc, valor,
                    quando, status, motivo)
                if status == "NEGADA":
                    self.negadas.append({"colab": c, "trx": trx_id, "motivo": motivo,
                                         "quando": quando, "valor": valor, "mcc": mcc})
                    continue
                for carteira, v in debitos:
                    saldo[carteira] -= v
                    self.lancar(c, carteira, "DEBITO", v, "TRANSACAO", trx_id, quando)
                dia = quando.date()
                gasto_dia[dia] = gasto_dia.get(dia, 0) + valor
                if mcc not in MCC_BLOQUEADO and rng.random() < 0.012:
                    t = quando + timedelta(days=rng.randint(1, 10), hours=rng.randint(0, 8))
                    if t <= CORTE:
                        push(t, "estorno", (trx_id, debitos))

        for carteira in CARTEIRAS:
            add("beneficios.carteiras", c["id"], carteira, saldo[carteira], ultimo_evento)

    def autorizar(self, c, mcc, valor, quando, saldo, gasto_dia, cartao_ativo):
        e = c["empresa"]
        if not cartao_ativo:
            return "NEGADA", "CARTAO_INATIVO", []
        if mcc in MCC_BLOQUEADO:
            # Bug real: o autorizador legado aprovou algumas apostas em agosto
            if (quando.month == 8 and self.apostas_aprovadas_legado < 4
                    and "LIVRE" in e["habilitadas"] and saldo["LIVRE"] >= valor):
                self.apostas_aprovadas_legado += 1
                return "APROVADA", None, [("LIVRE", valor)]
            return "NEGADA", "MCC_BLOQUEADO", []
        carteira = MCC_CARTEIRA[mcc]
        if carteira not in e["habilitadas"]:
            return "NEGADA", "SEM_CARTEIRA_COMPATIVEL", []
        if saldo[carteira] >= valor:
            debitos = [(carteira, valor)]
        elif (carteira != "LIVRE" and e["fallback"] and "LIVRE" in e["habilitadas"]
              and saldo[carteira] + saldo["LIVRE"] >= valor):
            debitos = [(carteira, saldo[carteira])] if saldo[carteira] > 0 else []
            debitos.append(("LIVRE", valor - saldo[carteira]))
        else:
            return "NEGADA", "SALDO_INSUFICIENTE", []
        if gasto_dia.get(quando.date(), 0) + valor > e["limite"]:
            return "NEGADA", "LIMITE_DIARIO_EXCEDIDO", []
        return "APROVADA", None, debitos


# ---------------------------------------------------------------------------
# Financeiro
# ---------------------------------------------------------------------------

FORNECEDORES = [
    (1, "Amazon Web Services", "Cloud", "CC-TEC", 340000, 398000, "Infraestrutura AWS (conta consolidada, sem tags por squad)"),
    (2, "Anthropic", "IA", "CC-TEC", 6200, 47500, "Claude (Team e API), uso de engenharia"),
    (3, "GitHub", "Ferramentas de desenvolvimento", "CC-TEC", 9800, 12400, "GitHub Copilot Business"),
    (4, "Microsoft", "Ferramentas de desenvolvimento", "CC-TEC", 6100, 6900, "Azure DevOps (Boards, Repos, Pipelines)"),
    (5, "SonarSource", "Qualidade e segurança", "CC-SEG", 8700, 8700, "SonarQube Enterprise"),
    (6, "Veracode", "Qualidade e segurança", "CC-SEG", 21500, 21500, "Veracode SAST e SCA"),
    (7, "Mastercard", "Processamento", "CC-OPE", 610000, 705000, "Taxas de bandeira"),
    (8, "Processa Cartões S.A.", "Processamento", "CC-OPE", 280000, 320000, "Processamento e emissão de cartões"),
    (9, "Zendesk", "Atendimento", "CC-ATD", 34000, 37000, "Plataforma de atendimento"),
    (10, "Salesforce", "Comercial", "CC-COM", 46000, 48500, "CRM Sales Cloud"),
    (11, "Slack", "Colaboração", "CC-ADM", 8900, 9600, "Slack Business+"),
    (12, "Google Workspace", "Colaboração", "CC-ADM", 13800, 14900, "E-mail e documentos"),
    (13, "Condomínio Torre Aurora", "Infraestrutura física", "CC-ADM", 182000, 182000, "Aluguel e condomínio do escritório"),
    (14, "Plastik Cartões Ltda.", "Produção de cartões", "CC-OPE", 52000, 61000, "Plásticos e envio de cartões"),
]


def gerar_financeiro(op: Operacao) -> None:
    did = 1
    competencias = meses(date(2025, 11, 1), date(2026, 10, 1))
    for fid, nome, cat, cc, inicio, fim, desc in FORNECEDORES:
        add("financeiro.fornecedores", fid, nome, cat)
        for i, comp in enumerate(competencias):
            frac = i / (len(competencias) - 1)
            if nome == "Anthropic":
                base = inicio + (fim - inicio) * (frac ** 1.8)
                if comp >= date(2026, 3, 1):
                    base *= 1.15
            else:
                base = inicio + (fim - inicio) * frac
            valor = int(base * rng.uniform(0.97, 1.03) * 100)
            add("financeiro.despesas", did, fid, cc, comp, valor, desc)
            did += 1

    for p in op.pedidos.values():
        e, mes = p["empresa"], p["mes"]
        mensalidade = p["colabs"] * MENSALIDADE[e["plano"]]
        vencimento = mes - timedelta(days=6)
        if mes == date(2026, 11, 1):
            status, pago = "EM_ABERTO", None
        elif e["status"] == "SUSPENSA" and mes == date(2026, 10, 1):
            status, pago = "VENCIDA", None
        else:
            status = "PAGA"
            pago = vencimento + timedelta(days=rng.randint(1, 6)) if rng.random() < 0.05 \
                else vencimento - timedelta(days=rng.randint(0, 5))
        add("financeiro.faturas", f"FAT-{mes:%Y%m}-{e['id'][4:]}", e["id"], mes, p["total"],
            mensalidade, p["total"] + mensalidade, vencimento, status, pago)


# ---------------------------------------------------------------------------
# Atendimento
# ---------------------------------------------------------------------------

def gerar_atendimento(op: Operacao, atendentes: list[int]) -> None:
    tickets = []
    ativos = [a for a in atendentes if funcs[a - 1]["status"] == "ATIVO"]

    def pii(c: dict) -> str:
        sorteio = rng.random()
        if sorteio < 0.07:
            return f" Meu CPF é {c['cpf']}."
        if sorteio < 0.11:
            return f" CPF {c['cpf']}, telefone {c['telefone'] or telefone()}."
        if sorteio < 0.14:
            return f" Pode me ligar no {c['telefone'] or telefone()}."
        return ""

    motivos_texto = {
        "SALDO_INSUFICIENTE": "Tentei pagar e deu saldo insuficiente, mas eu tinha saldo no cartão.",
        "SEM_CARTEIRA_COMPATIVEL": "Minha compra foi recusada e não entendi o motivo.",
        "LIMITE_DIARIO_EXCEDIDO": "Compra negada por limite. Que limite é esse?",
        "CARTAO_INATIVO": "Meu cartão não passa em lugar nenhum.",
        "MCC_BLOQUEADO": "Não consegui usar o Saldo Livre num site.",
    }
    for n in rng.sample(op.negadas, min(900, len(op.negadas))):
        c = n["colab"]
        tickets.append(dict(
            aberto=n["quando"] + timedelta(minutes=rng.randint(5, 600)), solicitante="COLABORADOR",
            colab=c, empresa=c["empresa"]["id"], categoria="COMPRA_NEGADA", prioridade="MEDIA",
            assunto="Compra recusada",
            descricao=f"{motivos_texto[n['motivo']]} Valor R$ {n['valor'] / 100:.2f}.{pii(c)}"))

    for c, lanc in op.colabs_saldo_divergente:
        tickets.append(dict(
            aberto=lanc[7] + timedelta(days=rng.randint(1, 8), hours=rng.randint(0, 10)),
            solicitante="COLABORADOR", colab=c, empresa=c["empresa"]["id"],
            categoria="SALDO_DIVERGENTE", prioridade="ALTA", assunto="Saldo não bate com o extrato",
            descricao=(f"O saldo da carteira {lanc[2]} no app está R$ {lanc[4] / 100:.2f} menor do que a "
                       f"soma do extrato. Já conferi várias vezes.{pii(c)}"),
            forcar_status=rng.choice(["ABERTO", "EM_ANDAMENTO", "EM_ANDAMENTO"])))
    for c in rng.sample(op.colabs, 40):
        tickets.append(dict(
            aberto=datetime.combine(data_entre(date(2026, 8, 3), date(2026, 10, 14)),
                                    time(rng.randint(8, 21), rng.randint(0, 59)), SP),
            solicitante="COLABORADOR", colab=c, empresa=c["empresa"]["id"],
            categoria="SALDO_DIVERGENTE", prioridade="ALTA", assunto="Saldo errado",
            descricao=f"Acho que meu saldo está errado, sumiu dinheiro do VR.{pii(c)}",
            forcar_status="FECHADO"))

    for c in op.colabs:
        k = c["cartoes"][0]
        if k["bloqueado_em"]:
            categoria = "SEGUNDA_VIA" if len(c["cartoes"]) == 2 else "CARTAO_BLOQUEADO"
            texto = ("Perdi meu cartão, preciso de outro." if categoria == "SEGUNDA_VIA"
                     else "Bloquearam meu cartão sem eu pedir. Preciso desbloquear.")
            tickets.append(dict(
                aberto=k["bloqueado_em"] + timedelta(minutes=rng.randint(10, 300)),
                solicitante="COLABORADOR", colab=c, empresa=c["empresa"]["id"],
                categoria=categoria, prioridade="ALTA", assunto=texto.split(",")[0].split(".")[0],
                descricao=f"{texto}{pii(c)}"))

    for est in rng.sample(op.estornos_feitos, len(op.estornos_feitos) // 2):
        c = est["colab"]
        tickets.append(dict(
            aberto=est["quando"] - timedelta(days=rng.randint(1, 3)), solicitante="COLABORADOR",
            colab=c, empresa=c["empresa"]["id"], categoria="ESTORNO", prioridade="MEDIA",
            assunto="Pedido de estorno",
            descricao=f"Cancelei uma compra de R$ {est['valor'] / 100:.2f} e quero o dinheiro de volta.{pii(c)}"))

    duvidas = [
        ("DUVIDA_CARTEIRA", "Posso usar o VR no mercado?", "Quero saber se posso usar o saldo de refeição no supermercado."),
        ("DUVIDA_CARTEIRA", "Como funciona o Saldo Livre", "Não entendi onde posso usar o Saldo Livre."),
        ("DUVIDA_CARTEIRA", "Quando cai o crédito?", "Que dia cai o crédito do mês?"),
        ("APP_ERRO", "App fecha sozinho", "O app fecha quando abro o extrato."),
        ("APP_ERRO", "Não consigo entrar no app", "Fica carregando e não entra."),
    ]
    for _ in range(1100):
        c = rng.choice(op.colabs)
        cat, assunto, texto = rng.choice(duvidas)
        tickets.append(dict(
            aberto=datetime.combine(data_entre(date(2026, 8, 1), date(2026, 10, 16)),
                                    time(rng.randint(7, 22), rng.randint(0, 59)), SP),
            solicitante="COLABORADOR", colab=c, empresa=c["empresa"]["id"], categoria=cat,
            prioridade="BAIXA", assunto=assunto, descricao=f"{texto}{pii(c)}"))

    empresariais = [
        ("PEDIDO_CREDITO", "MEDIA", "Pedido de crédito não processado", "Subimos o pedido do mês e ainda aparece como pendente."),
        ("PEDIDO_CREDITO", "MEDIA", "Erro na planilha de crédito", "A planilha de créditos dá erro na linha 37 e não diz o motivo."),
        ("FATURA", "MEDIA", "Segunda via de boleto", "Preciso da segunda via da fatura deste mês."),
        ("FATURA", "ALTA", "Fatura com valor errado", "A mensalidade veio cobrando colaboradores que já foram desligados."),
        ("CADASTRO_COLABORADOR", "BAIXA", "Incluir colaboradores", "Precisamos incluir 12 novos colaboradores."),
        ("CADASTRO_COLABORADOR", "MEDIA", "Desligamento", "Como desligo um colaborador sem perder o saldo dele?"),
        ("RELATORIO", "BAIXA", "Relatório de uso", "Preciso do relatório de uso por carteira do trimestre."),
    ]
    for _ in range(600):
        e = rng.choice(op.empresas)
        cat, prio, assunto, texto = rng.choice(empresariais)
        tickets.append(dict(
            aberto=datetime.combine(data_entre(date(2026, 8, 1), date(2026, 10, 16)),
                                    time(rng.randint(8, 18), rng.randint(0, 59)), SP),
            solicitante="EMPRESA", colab=None, empresa=e["id"], categoria=cat, prioridade=prio,
            assunto=assunto, descricao=texto))
    for _ in range(220):
        cat, assunto, texto = rng.choice([
            ("CREDENCIAMENTO", "Quero aceitar Benefy", "Como faço para minha loja aceitar o cartão?"),
            ("REPASSE", "Repasse atrasado", "O repasse das vendas da semana passada não caiu."),
            ("REPASSE", "Taxa cobrada", "A taxa cobrada nas vendas veio diferente do contrato."),
        ])
        tickets.append(dict(
            aberto=datetime.combine(data_entre(date(2026, 8, 1), date(2026, 10, 16)),
                                    time(rng.randint(8, 18), rng.randint(0, 59)), SP),
            solicitante="ESTABELECIMENTO", colab=None, empresa=None, categoria=cat,
            prioridade="MEDIA", assunto=assunto, descricao=texto))

    tickets = [t for t in tickets if t["aberto"] <= CORTE]
    tickets.sort(key=lambda t: t["aberto"])
    horas_sla = {"BAIXA": 72, "MEDIA": 48, "ALTA": 24, "CRITICA": 4}
    for i, t in enumerate(tickets, start=1):
        idade = (CORTE - t["aberto"]).total_seconds() / 3600
        status = t.get("forcar_status")
        if status is None:
            if idade > 120:
                status = rng.choice(["RESOLVIDO", "FECHADO", "FECHADO"])
            else:
                status = rng.choice(["ABERTO", "EM_ANDAMENTO", "RESOLVIDO"])
        resolvido = None
        if status in ("RESOLVIDO", "FECHADO"):
            resolvido = t["aberto"] + timedelta(hours=rng.uniform(0.5, horas_sla[t["prioridade"]] * 1.4))
            if resolvido > CORTE:
                resolvido = CORTE - timedelta(minutes=rng.randint(5, 60))
        nota = rng.choices([1, 2, 3, 4, 5], weights=[8, 7, 15, 30, 40])[0] \
            if status == "FECHADO" and rng.random() < 0.7 else None
        if t["solicitante"] == "COLABORADOR":
            canal = rng.choices(["APP", "CHAT", "TELEFONE", "EMAIL"], weights=[40, 30, 20, 10])[0]
        else:
            canal = rng.choice(["EMAIL", "TELEFONE"])
        add("atendimento.tickets", f"TCK-{i:06d}", t["aberto"], canal, t["solicitante"],
            t["colab"]["id"] if t["colab"] else None, t["empresa"], t["categoria"],
            t["prioridade"], status, t["assunto"], t["descricao"],
            None if status == "ABERTO" else rng.choice(ativos), resolvido, nota)


# ---------------------------------------------------------------------------
# Engenharia
# ---------------------------------------------------------------------------

SERVICOS = [
    ("saldo-service", 1, "Python", "benefy/saldo-service", "CRITICA", "PRODUCAO", "Saldo das carteiras, débito, crédito e estorno"),
    ("extrato-service", 1, "Python", "benefy/extrato-service", "ALTA", "PRODUCAO", "Lançamentos e extrato das carteiras"),
    ("autorizador-service", 2, "Python", "benefy/autorizador-service", "CRITICA", "PRODUCAO", "Autorização de compras em tempo real"),
    ("cartoes-service", 3, "Java", "benefy/cartoes-service", "ALTA", "PRODUCAO", "Ciclo de vida dos cartões"),
    ("emissao-service", 3, "Java", "benefy/emissao-service", "MEDIA", "PRODUCAO", "Emissão e envio de cartões físicos"),
    ("faturamento-service", 4, "Java", "benefy/faturamento-service", "ALTA", "MIGRANDO", "Faturas das empresas clientes"),
    ("monolito-benefy", 4, "Java", "benefy/monolito", "ALTA", "LEGADO", "Relatórios, faturamento antigo e telas internas"),
    ("portal-rh", 5, "TypeScript", "benefy/portal-rh", "ALTA", "PRODUCAO", "Portal web das empresas clientes"),
    ("pedidos-credito-service", 5, "TypeScript", "benefy/pedidos-credito-service", "ALTA", "PRODUCAO", "Pedidos de crédito das empresas"),
    ("bff-app", 6, "Kotlin", "benefy/bff-app", "ALTA", "PRODUCAO", "Backend for frontend do app"),
    ("app-colaborador", 6, "Kotlin e Swift", "benefy/app-colaborador", "ALTA", "PRODUCAO", "Apps Android e iOS"),
    ("motor-regras-fraude", 7, "Python", "benefy/motor-regras-fraude", "ALTA", "PRODUCAO", "Regras de detecção de fraude"),
    ("infra-terraform", 8, "Terraform", "benefy/infra", "CRITICA", "PRODUCAO", "Infraestrutura AWS como código"),
    ("pipelines-templates", 8, "YAML", "benefy/pipelines-templates", "MEDIA", "PRODUCAO", "Templates de pipeline do Azure DevOps"),
]

INCIDENTES = [
    ("INC-2025-031", "Dados de colaboradores enviados a chatbot de IA público", "SEV2", "extrato-service",
     datetime(2025, 3, 10, 15, 20, tzinfo=SP), datetime(2025, 3, 24, 18, 0, tzinfo=SP), "RESOLVIDO",
     "Dev colou 214 linhas de log com CPF e nome em um chatbot público ao investigar um bug.",
     "Logs sem mascaramento de dados pessoais e ausência de política de uso de IA."),
    ("INC-2026-007", "Lentidão na autorização no dia 1", "SEV2", "autorizador-service",
     datetime(2026, 4, 1, 11, 48, tzinfo=SP), datetime(2026, 4, 1, 13, 5, tzinfo=SP), "RESOLVIDO",
     "Tempo de resposta acima de 3s no pico do almoço do dia de crédito. 4% das compras com timeout.",
     "Pool de conexões do banco subdimensionado para o pico do dia 1."),
    ("INC-2026-015", "Quality gate do SonarQube indisponível", "SEV3", "pipelines-templates",
     datetime(2026, 7, 22, 9, 10, tzinfo=SP), datetime(2026, 7, 22, 16, 40, tzinfo=SP), "RESOLVIDO",
     "Pipelines ficaram travados aguardando o Sonar. Três squads fizeram merge com o gate desligado.",
     "Certificado do servidor SonarQube expirou."),
    ("INC-2026-019", "Fila de lançamentos indisponível", "SEV2", "saldo-service",
     datetime(2026, 10, 6, 14, 2, tzinfo=SP), datetime(2026, 10, 6, 15, 41, tzinfo=SP), "EM_INVESTIGACAO",
     "A fila de lançamentos ficou indisponível por cerca de 1h40. As mensagens foram para a DLQ e foram "
     "reprocessadas no dia seguinte. Atendimento relata reclamações de saldo que não bate com o extrato.",
     None),
    ("INC-2026-021", "Falha no login do app iOS", "SEV2", "app-colaborador",
     datetime(2026, 9, 14, 8, 30, tzinfo=SP), datetime(2026, 9, 14, 12, 15, tzinfo=SP), "RESOLVIDO",
     "Após atualização, usuários de iOS não conseguiam fazer login.",
     "Mudança no fluxo de autenticação sem teste em dispositivo físico."),
]


def gerar_engenharia() -> None:
    for s in SERVICOS:
        add("engenharia.servicos", *s)
    itens = json.loads(ARQ_WORK_ITEMS.read_text(encoding="utf-8"))
    for it in itens:
        criado = datetime.combine(data_entre(date(2026, 9, 1), date(2026, 10, 15)),
                                  time(rng.randint(9, 18), rng.randint(0, 59)), SP)
        tipo = "BUG" if it["id"] in ("BNF-110", "BNF-117") else "HISTORIA"
        add("engenharia.work_items", it["id"], tipo, it["squad"], it["titulo"],
            it["descricao"].strip(), (it["criterios_aceite"] or "").strip(), it["estado"],
            func_por_nome.get(it["autor"]), None, criado)
    for inc in INCIDENTES:
        add("engenharia.incidentes", *inc)


# ---------------------------------------------------------------------------
# Escrita
# ---------------------------------------------------------------------------

def formatar(v):
    if isinstance(v, datetime):
        return v.isoformat()
    if isinstance(v, date):
        return v.isoformat()
    return v


def escrever() -> None:
    PASTA_SEED.mkdir(parents=True, exist_ok=True)
    copias = []
    for tabela, colunas in COLUNAS.items():
        arquivo = PASTA_SEED / f"{tabela}.csv"
        with arquivo.open("w", newline="", encoding="utf-8") as f:
            # QUOTE_NOTNULL: None sai sem aspas (vira NULL no Postgres) e "" sai como string vazia
            w = csv.writer(f, quoting=csv.QUOTE_NOTNULL)
            w.writerow(colunas)
            for linha in LINHAS[tabela]:
                w.writerow([formatar(v) for v in linha])
        copias.append(f"\\copy {tabela} ({', '.join(colunas)}) FROM '/seed/{tabela}.csv' "
                      f"WITH (FORMAT csv, HEADER true)")
        print(f"{tabela:34} {len(LINHAS[tabela]):>8} linhas")

    gestores = "\n".join(f"UPDATE rh.departamentos SET gestor_id = {g} WHERE id = {d};"
                         for d, g in sorted(gestor_depto.items()))
    ARQ_CARGA.write_text(
        "-- Gerado por tools/seed/gerar_seed.py. Não edite à mão.\n"
        "\\set ON_ERROR_STOP on\n"
        "BEGIN;\n" + "\n".join(copias) + "\n" + gestores + "\nCOMMIT;\n",
        encoding="utf-8")


def main() -> None:
    pessoas = gerar_rh()
    empresas = gerar_comercial(pessoas["executivos"])
    lojas = gerar_estabelecimentos()
    op = Operacao(empresas, lojas)
    op.gerar_colaboradores()
    op.simular()
    gerar_financeiro(op)
    gerar_atendimento(op, pessoas["atendentes"])
    gerar_engenharia()
    escrever()


if __name__ == "__main__":
    main()
