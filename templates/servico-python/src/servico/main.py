from fastapi import FastAPI

from servico.api import saude

app = FastAPI(title="servico")
app.include_router(saude.router)
