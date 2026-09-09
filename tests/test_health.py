import pytest
from fastapi.testclient import TestClient


def test_health_returns_200(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_format(client: TestClient):
    response = client.get("/health")
    data = response.json()
    assert "data" in data
    assert "error" in data
    assert data["data"]["status"] == "ok"
    assert data["error"] is None