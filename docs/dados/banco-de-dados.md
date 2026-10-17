# Banco de dados de homologação

Cópia sintética da produção, com a operação de **1º de agosto a 16 de outubro de 2026**. Os volumes são menores que os de produção (150 das 2.340 empresas clientes), mas a estrutura e as regras são as mesmas.

## Como subir

Na raiz do repositório:

```powershell
python tools/seed/gerar_seed.py     # gera os CSVs (só na primeira vez ou depois de mudar o gerador)
docker compose up -d                # sobe o Postgres e carrega os dados (leva uns 20 segundos)
```

Para apagar tudo e recarregar do zero:

```powershell
docker compose down -v
docker compose up -d
```

## Como conectar

| Item | Valor |
|---|---|
| Host | `localhost` |
| Porta | `5433` |
| Banco | `benefy` |
| Usuário | `benefy` |
| Senha | `benefy_dev` |
| URL | `postgresql://benefy:benefy_dev@localhost:5433/benefy` |

Formas de acessar:
- **Navegador:** Adminer em http://localhost:8081 (sistema PostgreSQL, servidor `postgres`).
- **Linha de comando:** `docker exec -it benefy-postgres psql -U benefy -d benefy`
- **DBeaver ou extensão do VS Code:** use os dados da tabela acima.
- **Python:** `psycopg` com a URL acima.

## Convenções

- Dinheiro sempre em **centavos** (`bigint`), colunas terminadas em `_centavos`.
- Datas e horas em `timestamptz`, no fuso `America/Sao_Paulo`.
- IDs de negócio com prefixo legível: `EMP-0001`, `COL-000001`, `TRX-0000001`, `TCK-000001`.

## Mapa geral

```mermaid
erDiagram
    EMPRESAS_CLIENTES ||--o{ COLABORADORES : tem
    EMPRESAS_CLIENTES ||--o{ EMPRESA_CARTEIRAS : configura
    EMPRESAS_CLIENTES ||--o{ PEDIDOS_CREDITO : faz
    EMPRESAS_CLIENTES ||--o{ FATURAS : recebe
    COLABORADORES ||--o{ CARTOES : usa
    COLABORADORES ||--o{ CARTEIRAS : possui
    COLABORADORES ||--o{ TRANSACOES : faz
    COLABORADORES ||--o{ LANCAMENTOS : tem
    PEDIDOS_CREDITO ||--o{ PEDIDO_CREDITO_ITENS : contem
    TRANSACOES ||--o{ ESTORNOS : pode_ter
    ESTABELECIMENTOS ||--o{ TRANSACOES : recebe
    MCC ||--o{ ESTABELECIMENTOS : classifica
    COLABORADORES ||--o{ TICKETS : abre
    FUNCIONARIOS ||--o{ TICKETS : atende
    FUNCIONARIOS ||--o{ EMPRESAS_CLIENTES : "é executivo de"
```

## Schemas e tabelas

### `rh`: a própria Benefy

| Tabela | O que guarda |
|---|---|
| `departamentos` | As 13 áreas da empresa, centro de custo e gestor |
| `cargos` | Cargos com trilha, nível e faixa salarial |
| `funcionarios` | Todos os funcionários, ativos e desligados, com gestor, cargo e salário |
| `squads` | Squads de engenharia com tech lead, PO e engineering manager |
| `squad_membros` | Quem está em cada squad e com qual papel |
| `ferias` | Férias gozadas, programadas e canceladas |
| `avaliacoes_desempenho` | Notas semestrais (1 a 5) dadas pelo gestor |
| `folha_pagamento` | Custo mensal de cada funcionário (nov/2025 a set/2026) |

### `comercial`: clientes

| Tabela | O que guarda |
|---|---|
| `planos` | Essencial, Flex e Flex Plus, com a mensalidade por colaborador |
| `empresas_clientes` | As empresas clientes, com plano, fallback, limite diário e executivo de contas |
| `empresa_carteiras` | Quais carteiras cada empresa habilitou e quanto credita por mês |

### `beneficios`: o produto

| Tabela | O que guarda |
|---|---|
| `tipos_carteira` | As 6 carteiras (REFEICAO, ALIMENTACAO, MOBILIDADE, SAUDE, CULTURA, LIVRE) |
| `mcc` | Códigos de ramo, a carteira de cada um (NULL = só Saldo Livre) e se é bloqueado |
| `estabelecimentos` | Lojas onde o cartão é usado |
| `colaboradores` | Quem recebe o cartão (dado pessoal: nome, CPF, e-mail, telefone) |
| `cartoes` | Cartões emitidos, com status e data de bloqueio |
| `carteiras` | Saldo atual de cada carteira de cada colaborador |
| `pedidos_credito` | Pedido mensal de crédito de cada empresa |
| `pedido_credito_itens` | Quanto cada colaborador recebe em cada carteira no pedido |
| `transacoes` | Toda tentativa de compra, aprovada ou negada, com o motivo |
| `estornos` | Estornos de compras aprovadas |
| `lancamentos` | O extrato: cada crédito, débito e estorno, por carteira |

### `financeiro`

| Tabela | O que guarda |
|---|---|
| `fornecedores` | Fornecedores (AWS, Anthropic, GitHub, Mastercard etc.) |
| `despesas` | Despesa mensal por fornecedor e centro de custo (nov/2025 a out/2026) |
| `faturas` | Fatura mensal de cada empresa cliente: créditos + mensalidade |

### `atendimento`

| Tabela | O que guarda |
|---|---|
| `tickets` | Chamados de colaboradores, empresas e estabelecimentos, com categoria, status, atendente e nota de satisfação |

### `engenharia`

| Tabela | O que guarda |
|---|---|
| `servicos` | Os serviços em produção, squad dono, linguagem e criticidade |
| `work_items` | Backlog exportado do Azure Boards |
| `incidentes` | Histórico de incidentes, com severidade e causa raiz |

## Consultas para começar

```sql
-- Quantos colaboradores cada empresa tem
SELECT e.razao_social, count(*) AS colaboradores
FROM beneficios.colaboradores c
JOIN comercial.empresas_clientes e ON e.id = c.empresa_id
GROUP BY e.razao_social
ORDER BY colaboradores DESC
LIMIT 10;

-- Por que as compras são negadas
SELECT motivo_negacao, count(*)
FROM beneficios.transacoes
WHERE status = 'NEGADA'
GROUP BY motivo_negacao
ORDER BY count(*) DESC;

-- Quem é o gestor de quem
SELECT f.nome, c.titulo AS cargo, g.nome AS gestor
FROM rh.funcionarios f
JOIN rh.cargos c ON c.id = f.cargo_id
LEFT JOIN rh.funcionarios g ON g.id = f.gestor_id
WHERE f.departamento_id = 2 AND f.status = 'ATIVO';
```

## Aviso

Como em qualquer empresa de verdade, esta base **não é perfeita**. Pode ter dado inconsistente, cadastro duplicado, informação sensível onde não devia e consulta lenta. Se encontrar algo estranho, avise o seu sênior.
