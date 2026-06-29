"""Tests for the /health endpoint."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Acceptance tests for the health check endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """GET /health must return HTTP 200."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, client: TestClient) -> None:
        """GET /health must return a JSON body."""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)

    def test_health_status_field_present(self, client: TestClient) -> None:
        """Response must contain a 'status' field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data

    def test_health_status_is_ok(self, client: TestClient) -> None:
        """Status must be 'ok' when all sub-systems are healthy."""
        response = client.get("/health")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_service_field(self, client: TestClient) -> None:
        """Response must identify the service."""
        response = client.get("/health")
        data = response.json()
        assert data.get("service") == "api-gateway-service"

    def test_health_details_field(self, client: TestClient) -> None:
        """Response must include a 'details' sub-object."""
        response = client.get("/health")
        data = response.json()
        assert "details" in data
        assert isinstance(data["details"], dict)

    def test_health_content_type(self, client: TestClient) -> None:
        """Response Content-Type must be application/json."""
        response = client.get("/health")
        assert "application/json" in response.headers.get("content-type", "")
