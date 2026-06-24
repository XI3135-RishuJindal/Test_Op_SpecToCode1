"""
Inbound HTTP adapter — gateway / proxy router.

Routes:
  POST /api/v1/auth/register   → identity service
  POST /api/v1/auth/verify     → identity service
  ANY  /api/v1/{path:path}     → generic upstream proxy
"""
from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request, Response

from app.application.gateway_service import GatewayService
from app.core.exceptions import (
    GatewayError,
    RateLimitExceededError,
    RequestTooLargeError,
)
from app.core.models import CorrelationContext, ProxyRequest
from app.infrastructure.dependencies import get_gateway_service
from app.infrastructure.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1", tags=["gateway"])


def _build_context(
    x_correlation_id: Optional[str],
    x_idempotency_key: Optional[str],
) -> CorrelationContext:
    import uuid

    cid = x_correlation_id or str(uuid.uuid4())
    return CorrelationContext(correlation_id=cid, idempotency_key=x_idempotency_key)


@router.post(
    "/auth/register",
    summary="Register a new user account",
    status_code=201,
)
async def register(
    request: Request,
    x_correlation_id: Optional[str] = Header(default=None),
    x_idempotency_key: Optional[str] = Header(default=None),
    service: GatewayService = Depends(get_gateway_service),
) -> Response:
    return await _proxy(
        request=request,
        path="/auth/register",
        x_correlation_id=x_correlation_id,
        x_idempotency_key=x_idempotency_key,
        service=service,
    )


@router.post(
    "/auth/verify",
    summary="Verify an email address",
    status_code=200,
)
async def verify_email(
    request: Request,
    x_correlation_id: Optional[str] = Header(default=None),
    x_idempotency_key: Optional[str] = Header(default=None),
    service: GatewayService = Depends(get_gateway_service),
) -> Response:
    return await _proxy(
        request=request,
        path="/auth/verify",
        x_correlation_id=x_correlation_id,
        x_idempotency_key=x_idempotency_key,
        service=service,
    )


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    summary="Generic upstream proxy",
    include_in_schema=False,
)
async def generic_proxy(
    path: str,
    request: Request,
    x_correlation_id: Optional[str] = Header(default=None),
    x_idempotency_key: Optional[str] = Header(default=None),
    service: GatewayService = Depends(get_gateway_service),
) -> Response:
    return await _proxy(
        request=request,
        path=f"/{path}",
        x_correlation_id=x_correlation_id,
        x_idempotency_key=x_idempotency_key,
        service=service,
    )


async def _proxy(
    *,
    request: Request,
    path: str,
    x_correlation_id: Optional[str],
    x_idempotency_key: Optional[str],
    service: GatewayService,
) -> Response:
    """Shared proxy logic: build context, forward, return response."""
    start = time.monotonic()
    context = _build_context(x_correlation_id, x_idempotency_key)

    try:
        body: bytes = await request.body()
        proxy_req = ProxyRequest(
            method=request.method,
            path=path,
            headers=dict(request.headers),
            body=body or None,
            context=context,
        )
        proxy_resp = await service.forward(proxy_req)
    except RateLimitExceededError as exc:
        raise HTTPException(status_code=429, detail=exc.message)
    except RequestTooLargeError as exc:
        raise HTTPException(status_code=413, detail=exc.message)
    except GatewayError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    finally:
        duration_ms = (time.monotonic() - start) * 1000
        logger.info(
            "proxy_request",
            extra={
                "method": request.method,
                "path": path,
                "correlation_id": context.correlation_id,
                "duration_ms": round(duration_ms, 2),
            },
        )

    return Response(
        content=proxy_resp.body,
        status_code=proxy_resp.status_code,
        headers={
            k: v
            for k, v in proxy_resp.headers.items()
            if k.lower() not in ("content-length", "transfer-encoding")
        },
        media_type=proxy_resp.headers.get("content-type", "application/json"),
    )
