# Benefy

Repositório central da **Benefy Tecnologia em Benefícios S.A.**: documentação institucional, padrões de engenharia, ambiente de homologação e código dos serviços.

A Benefy oferece às empresas um cartão único de benefícios corporativos. O RH distribui o saldo em carteiras (refeição, alimentação, mobilidade, saúde, cultura e saldo livre), e o colaborador usa o cartão ou o app em qualquer estabelecimento da rede Mastercard.

## Ambiente de homologação

Pré-requisitos: Python 3.12 e Docker Desktop.

```powershell
python tools/seed/gerar_seed.py
docker compose up -d
```

| Recurso | Endereço |
|---|---|
| PostgreSQL | `postgresql://benefy:benefy_dev@localhost:5433/benefy` |
| Adminer | http://localhost:8081 |

As credenciais acima valem apenas para o ambiente local. Detalhes de schemas, tabelas e consultas em [Banco de dados](docs/dados/banco-de-dados.md).

A base de homologação usa dados sintéticos, mas segue a mesma classificação da produção: CPF, nome e telefone são dados **Restritos** e não saem do ambiente. Ver [Segurança e compliance](docs/empresa/06-seguranca-e-compliance.md).

## Documentação

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
| Onboarding | [Squad Plataforma de IA](docs/onboarding/primeiro-dia.md) |
| Termos | [Glossário](docs/empresa/07-glossario.md) |

## Estrutura

```
benefy/
├── .github/            CI (quality gate), templates de PR e issue, CODEOWNERS
├── docs/               documentação institucional, por área
├── database/
│   ├── init/           schema, carga e índices do Postgres (executados na criação do container)
│   └── seed/           CSVs gerados localmente (não versionados)
├── tools/
│   ├── seed/           gerador dos dados de homologação
│   ├── ci/             verificações usadas pelo pipeline
│   └── novo_servico.py cria um serviço a partir do template
├── templates/          template padrão de serviço Python
├── services/           um diretório por serviço, com README e testes
└── docker-compose.yml  Postgres e Adminer
```

## Como contribuir

O fluxo completo está em [Padrões de engenharia](docs/empresa/05-padroes-de-engenharia.md). Em resumo:

- **GitFlow:** `main` reflete produção e `develop` é a branch de integração. O trabalho sai de `feature/BNF-123-descricao-curta`. Não há push direto em `main` ou `develop`.
- **Serviço novo:** sempre a partir do template, com `python tools/novo_servico.py <nome-do-servico>`.
- **Commits:** Conventional Commits com o ID da história, por exemplo `feat(saldo): debita carteira com fallback para saldo livre [BNF-104]`.
- **Pull requests:** pelo menos uma aprovação humana. Agentes de IA podem abrir PRs e comentar, mas nunca aprovam nem fazem merge.
- **Quality gate:** cobertura de código novo de pelo menos 80%, nenhum bug ou vulnerabilidade nova e SAST (Semgrep e Bandit) sem achados de severidade alta ou crítica.
- **Dados:** nenhum dado pessoal em código, teste, log ou fixture.

## Base de homologação

Período: 1º de agosto a 16 de outubro de 2026.

| Área | Volume |
|---|---|
| Funcionários da Benefy | 371 ativos, 13 departamentos, 9 squads |
| Empresas clientes | 150 |
| Colaboradores com cartão | 6.104 |
| Estabelecimentos | 953 |
| Transações | 155 mil |
| Lançamentos de extrato | 220 mil |
| Tickets de atendimento | 3,9 mil |
| Folha de pagamento | 11 meses |
| Despesas com fornecedores | 12 meses |
