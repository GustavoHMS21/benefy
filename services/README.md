# services

Código dos serviços da Benefy. Cada serviço fica na sua própria pasta (ex: `services/saldo-service`), com README e testes, e é validado pelo CI a cada PR.

Um serviço novo sempre nasce do template padrão:

```powershell
python tools/novo_servico.py saldo-service
```

O script copia [templates/servico-python](../templates/servico-python) e renomeia o pacote (`saldo_service`). Os serviços entram aqui conforme as demandas do backlog.
