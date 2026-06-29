"""Tests for the routes management REST API."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestRoutesAPI:
    def test_list_routes_empty(self, client: TestClient) -> None:
        response = client.get("/api/v1/routes/")
        assert response.status_code == 200
        assert response.json() == []

    def test_create_route(self, client: TestClient) -> None:
        payload = {
            "name": "Users",
            "path_prefix": "/api/v1/users",
            "upstream_url": "http://users:8080",
            "strip_prefix": True,
            "methods": ["GET", "POST"],
            "tags": ["users"],
        }
        response = client.post("/api/v1/routes/", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Users"
        assert data["path_prefix"] == "/api/v1/users"
        assert "route_id" in data

    def test_get_route_by_id(self, client: TestClient) -> None:
        payload = {
            "name": "Orders",
            "path_prefix": "/api/v1/orders",
            "upstream_url": "http://orders:8080",
        }
        created = client.post("/api/v1/routes/", json=payload).json()
        route_id = created["route_id"]

        response = client.get(f"/api/v1/routes/{route_id}")
        assert response.status_code == 200
        assert response.json()["route_id"] == route_id

    def test_get_nonexistent_route_returns_404(self, client: TestClient) -> None:
        response = client.get("/api/v1/routes/does-not-exist")
        assert response.status_code == 404

    def test_delete_route(self, client: TestClient) -> None:
        payload = {
            "name": "Temp",
            "path_prefix": "/temp",
            "upstream_url": "http://temp:8080",
        }
        created = client.post("/api/v1/routes/", json=payload).json()
        route_id = created["route_id"]

        delete_response = client.delete(f"/api/v1/routes/{route_id}")
        assert delete_response.status_code == 204

        get_response = client.get(f"/api/v1/routes/{route_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_route_returns_404(self, client: TestClient) -> None:
        response = client.delete("/api/v1/routes/ghost")
        assert response.status_code == 404
