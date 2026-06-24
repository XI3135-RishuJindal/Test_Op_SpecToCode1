"""
Tests for the health-check endpoints.

Acceptance criteria:
  - GET /health returns 200 with {"status": "ok", "version": <str>}
  - GET /health/ready returns 200 with status, version, and details
  - Both endpoints echo back the X-Correlation-ID header when supplied
  - Both endpoints generate a X-Correlation-ID header when none is supplied
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_returns_200(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_liveness_body_has_status_ok(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    assert body["status"] == "ok"


@pytest.mark.asyncio
async def test_liveness_body_has_version(client: AsyncClient) -> None:
    response = await client.get("/health")
    body = response.json()
    assert "version" in body
    assert isinstance(body["version"], str)
    assert body["version"] != ""


@pytest.mark.asyncio
async def test_readiness_returns_200(client: AsyncClient) -> None:
    response = await client.get("/health/ready")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_readiness_body_has_details(client: AsyncClient) -> None:
    response = await client.get("/health/ready")
    body = response.json()
    assert "details" in body
    assert isinstance(body["details"], dict)


@pytest.mark.asyncio
async def test_liveness_echoes_correlation_id(client: AsyncClient) -> None:
    cid = "test-correlation-id-abc123"
    response = await client.get("/health", headers={"X-Correlation-ID": cid})
    assert response.headers.get("x-correlation-id") == cid


@pytest.mark.asyncio
async def test_liveness_generates_correlation_id_when_absent(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert "x-correlation-id" in response.headers
    assert response.headers["x-correlation-id"] != ""


@pytest.mark.asyncio
async def test_readiness_echoes_correlation_id(client: AsyncClient) -> None:
    cid = "ready-correlation-xyz"
    response = await client.get("/health/ready", headers={"X-Correlation-ID": cid})
    assert response.headers.get("x-correlation-id") == cid
