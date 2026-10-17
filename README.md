# Benefy

Repositório central da **Benefy Tecnologia em Benefícios S.A.**, uma fintech fictícia de benefícios corporativos (vale-refeição, vale-alimentação e multibenefícios).

> A empresa, as pessoas, os números e os dados são fictícios. As regras de negócio são inspiradas no mercado brasileiro, mas simplificadas.

Você é o novo **AI Engineer Júnior** do squad **Plataforma de IA**. Comece pelo [primeiro dia](docs/onboarding/primeiro-dia.md).

## Subir o ambiente

Pré-requisitos: Python 3.12 e Docker Desktop rodando.

```powershell
python tools/seed/gerar_seed.py
docker compose up -d
```

Banco em `postgresql://benefy:benefy_dev@localhost:5433/benefy`. Adminer em http://localhost:8081.

## A empresa

| Área | Documento |
|---|---|
| Visão geral | [Sobre a Benefy](docs/empresa/01-sobre-a-benefy.md) |
| Produto | [Produtos e regras de negócio](docs/empresa/02-produtos-e-regras.md) |
| Pessoas | [Pessoas e squads](docs/empresa/03-pessoas-e-squads.md) |
| Tecnologia | [Arquitetura](docs/empresa/04-arquitetura.md) · [Padrões de engenharia](docs/empresa/05-padroes-de-engenharia.md) |
| Segurança | [Segurança e compliance](docs/empresa/06-seguranca-e-compliance.md) |
| RH | [Manual do colaborador](docs/rh/manual-do-colaborador.md) · [Cargos e salários](docs/rh/cargos-e-salarios.md) · [Benefícios](docs/rh/beneficios-dos-funcionarios.md) |
| Financeiro | [Visão financeira](docs/financeiro/visao-financeira.md) |
| Atendimento | [Operação de atendimento](docs/atendimento/operacao-de-atendimento.md) |
| Dados | [Banco de dados](docs/dados/banco-de-dados.md) |
| Termos | [Glossário](docs/empresa/07-glossario.md) |

## Estrutura

```
benefy/
├── docs/               documentação da empresa, por área
├── database/
│   ├── init/           schema e carga do Postgres (rodam ao subir o container)
│   └── seed/           CSVs gerados (fora do git)
├── tools/seed/         gerador dos dados de homologação
├── services/           código dos serviços (criado conforme as demandas)
└── docker-compose.yml  Postgres + Adminer
```

## No banco hoje

| Área | Volume |
|---|---|
| Funcionários da Benefy | 371 ativos, 13 departamentos, 9 squads |
| Empresas clientes | 150 |
| Colaboradores com cartão | 6.104 |
| Estabelecimentos | 953 |
| Transações (ago a out/2026) | 155 mil |
| Lançamentos de extrato | 220 mil |
| Tickets de atendimento | 3,9 mil |
| Folha de pagamento | 11 meses |
| Despesas com fornecedores | 12 meses |
