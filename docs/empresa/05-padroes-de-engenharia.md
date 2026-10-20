# Padrões de engenharia

Valem para todos os squads, inclusive para código escrito com ajuda de IA.

## Git: GitFlow

| Branch | Para que | Quem faz merge |
|---|---|---|
| `main` | O que está em produção. Cada merge vira uma tag de versão. | Só via PR de `release/*` ou `hotfix/*` |
| `develop` | Integração do que vai para a próxima versão | Via PR de `feature/*` |
| `feature/BNF-123-descricao-curta` | Uma história do backlog | Dev |
| `release/1.4.0` | Estabilização antes de subir | Tech lead |
| `hotfix/BNF-456-descricao` | Correção urgente em produção | Tech lead |

Regras:
- Ninguém faz push direto em `main` ou `develop`.
- Todo PR precisa de pelo menos 1 aprovação humana.
- **Agentes de IA nunca aprovam nem fazem merge de PR.** Eles podem abrir PRs e comentar.

## Commits

Padrão Conventional Commits, com o ID da história:

```
feat(saldo): debita carteira com fallback para saldo livre [BNF-104]
fix(estorno): impede estorno maior que o valor original [BNF-118]
test(saldo): adiciona cenários de limite diário [BNF-107]
```

Tipos aceitos: `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `ci`.

## Código Python

- Python 3.12, FastAPI, Pydantic.
- Formatação e lint com `ruff`.
- Tipagem em todas as funções públicas.
- Dinheiro sempre em centavos (`int`). Nunca `float`.
- Regras de negócio ficam em `domain/`, isoladas da API. A API só traduz HTTP para chamadas do domínio.

## Testes

- `pytest` para testes unitários.
- `pytest-bdd` para cenários de negócio em Gherkin, escritos em português (`# language: pt`).
- Toda regra do documento de produtos (R1 a R6, fallback, estorno) precisa de pelo menos um cenário BDD.
- Teste nomeado pelo comportamento: `test_compra_negada_quando_mcc_bloqueado`, não `test_1`.

## Quality gate (SonarQube)

O pipeline bloqueia o PR se qualquer item falhar:

| Métrica | Mínimo |
|---|---|
| Cobertura de código novo | 80% |
| Bugs novos | 0 |
| Vulnerabilidades novas | 0 |
| Security hotspots revisados | 100% |
| Duplicação em código novo | até 3% |

SAST (Veracode, no nosso caso Semgrep e Bandit): nenhuma vulnerabilidade de severidade **alta** ou **crítica**.

### Pipeline de CI do repositório central

O gate roda no GitHub Actions ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)) em todo PR contra `develop` e `main`. O check `quality-gate` é obrigatório para o merge.

| Job | O que valida |
|---|---|
| `python (<projeto>)` | Para cada projeto em `services/` e `templates/`: `ruff check`, `ruff format --check`, `pytest` com cobertura mínima de 80% e `bandit` (severidade alta) |
| `sast (semgrep)` | Regras `p/python` e `p/secrets` no repositório inteiro, bloqueando severidade alta |
| `dados-pessoais` | CPF e número de cartão em arquivos versionados ([verificador](../../tools/ci/verificar_dados_pessoais.py)) |
| `quality-gate` | Consolida os jobs acima. É o check exigido pela proteção de branch |

## Pull requests e issues

- Os PRs usam o [template](../../.github/pull_request_template.md), com a checklist da Definition of Done e a declaração de uso de IA, que alimenta as métricas do programa Benefy AI SDLC.
- Histórias e bugs são abertos pelos formulários em `.github/ISSUE_TEMPLATE`. Issue em branco não é aceita.
- Os revisores obrigatórios por caminho ficam em [`CODEOWNERS`](../../.github/CODEOWNERS).

## Definition of Ready (história pronta para entrar na sprint)

- Tem descrição no formato "Como [quem], quero [o quê], para [por quê]".
- Tem critérios de aceite em Gherkin ou lista verificável.
- Diz qual regra de negócio afeta (R1 a R6 etc.).
- Não tem dúvida aberta com o PO.

## Definition of Done

- Código revisado e aprovado por um humano.
- Cenários BDD dos critérios de aceite passando.
- Quality gate verde.
- Documentação atualizada se a API mudou.
- Nenhum dado pessoal real em teste, log ou fixture.
