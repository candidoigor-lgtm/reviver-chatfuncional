from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_substancias_endpoint():
    response = client.get("/api/substancias")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_indicadores_endpoint():
    response = client.get("/api/resumo/indicadores")
    assert response.status_code == 200
    assert response.json()["dados_ficticios"] is True

def test_resumo_substancias_endpoint():
    response = client.get("/api/resumo/substancias")
    assert response.status_code == 200
    assert isinstance(response.json()["itens"], list)
