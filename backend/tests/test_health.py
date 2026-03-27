from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness() -> None:
    response = client.get("/api/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}
