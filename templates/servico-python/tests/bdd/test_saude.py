from fastapi.testclient import TestClient
from httpx import Response
from pytest_bdd import given, parsers, scenarios, then, when

from servico.main import app

scenarios("saude.feature")


@given("que o serviço está no ar", target_fixture="cliente")
def cliente() -> TestClient:
    return TestClient(app)


@when("consulto a verificação de saúde", target_fixture="resposta")
def consultar_saude(cliente: TestClient) -> Response:
    return cliente.get("/health")


@then(parsers.parse('recebo o status "{status}"'))
def verificar_status(resposta: Response, status: str) -> None:
    assert resposta.json()["status"] == status
