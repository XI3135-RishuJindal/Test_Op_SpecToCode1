"""Health check HTTP router."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from src.application.health_service import HealthService
from src.dependencies import get_health_service

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Liveness / readiness probe",
    response_description="Gateway health status",
)
async def health_check(
    service: HealthService = Depends(get_health_service),
) -> dict[str, Any]:
    """Return the current health status of the API Gateway.

    - **status**: ``"ok"`` when all sub-systems are healthy, ``"degraded"`` otherwise.
    - **service**: Service name identifier.
    - **details**: Per-sub-system breakdown.
    """
    return await service.check()
