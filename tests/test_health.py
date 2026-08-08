"""Tests for the /health endpoint."""

import json


class TestHealthEndpoint:
    """Acceptance criteria: health check returns 200 with expected payload."""

    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/health")
        assert response.content_type == "application/json"

    def test_health_payload_status_ok(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert data["status"] == "ok"

    def test_health_payload_service_name(self, client):
        response = client.get("/health")
        data = json.loads(response.data)
        assert data["service"] == "authentication-service"
