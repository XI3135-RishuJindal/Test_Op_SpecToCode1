"""
Inbound HTTP adapter — health-check router.

Exposes GET /health (liveness) and GET /health/ready (readiness).
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.health_service import HealthService
from app.core.models import HealthStatus
from app.infrastructure.dependencies import get_health_service

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Liveness probe",
    response_model=dict,
    status_code=200,
)
async def liveness(
    service: HealthService = Depends(get_health_service),
) -> dict:
    """Return 200 when the process is alive."""
    result: HealthStatus = await service.check()
    return {"status": result.status, "version": result.version}


@router.get(
    "/health/ready",
    summary="Readiness probe",
    response_model=dict,
    status_code=200,
)
async def readiness(
    service: HealthService = Depends(get_health_service),
) -> dict:
    """Return 200 when the service is ready to accept traffic."""
    result: HealthStatus = await service.check()
    return {"status": result.status, "version": result.version, "details": result.details}
