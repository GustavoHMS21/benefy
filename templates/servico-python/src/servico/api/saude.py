from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["saude"])


class StatusSaude(BaseModel):
    status: str


@router.get("/health")
def verificar_saude() -> StatusSaude:
    return StatusSaude(status="ok")
