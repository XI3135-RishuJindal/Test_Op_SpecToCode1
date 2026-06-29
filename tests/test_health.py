"""Tests for the /health endpoint."""


def test_health_returns_200(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200


def test_health_returns_json_status_ok(client) -> None:
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "ok"


def test_health_returns_service_name(client) -> None:
    response = client.get("/health")
    data = response.get_json()
    assert data["service"] == "authentication-service"
