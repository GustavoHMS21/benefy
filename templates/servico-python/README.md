# servico-python

Template padrão dos serviços Python da Benefy. Um serviço novo é criado a partir dele com:

```powershell
python tools/novo_servico.py <nome-do-servico>
```

O CI valida o próprio template em todo PR, então ele sempre nasce verde.

## Estrutura

```
src/servico/
├── domain/        regras de negócio, sem dependência de HTTP ou banco
├── api/           rotas FastAPI: traduzem HTTP em chamadas ao domínio
└── main.py        criação da aplicação
tests/
├── unit/          testes unitários (pytest)
├── features/      cenários de negócio em Gherkin (# language: pt)
└── bdd/           passos dos cenários (pytest-bdd)
```

## Desenvolvimento local

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"

ruff check .
ruff format --check .
pytest
bandit -r src --severity-level high
```

São os mesmos comandos do job `python` do CI. Se passam localmente, passam no pipeline.

## Executar

```powershell
uvicorn servico.main:app --reload
```

Verificação de saúde em http://localhost:8000/health. Documentação da API em http://localhost:8000/docs.

## Padrões

- Dinheiro em centavos (`int`), nunca `float`.
- Toda regra de negócio tem pelo menos um cenário BDD.
- Testes nomeados pelo comportamento (`test_compra_negada_quando_mcc_bloqueado`).
- Cobertura mínima de 80%, imposta pelo `pytest`.

Detalhes em [Padrões de engenharia](../../docs/empresa/05-padroes-de-engenharia.md).
