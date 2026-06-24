"""
FastAPI application factory for the API Gateway / BFF Service.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.adapters.inbound.gateway_router import router as gateway_router
from app.adapters.inbound.health_router import router as health_router
from app.core.exceptions import GatewayError
from app.infrastructure.config import get_settings
from app.infrastructure.logging import configure_logging, get_logger
from app.infrastructure.middleware import (
    AccessLogMiddleware,
    CorrelationIdMiddleware,
    RequestSizeLimitMiddleware,
)
from app.infrastructure.tracing import configure_tracing

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup → yield → shutdown."""
    settings = get_settings()
    configure_logging(settings.log_level)
    configure_tracing(
        service_name=settings.otel_service_name,
        otlp_endpoint=settings.otel_exporter_otlp_endpoint,
    )
    logger.info(
        "gateway_starting",
        extra={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
        },
    )
    yield
    logger.info("gateway_shutdown")


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="API Gateway / BFF Service",
        description=(
            "Public-facing API Gateway that routes requests to internal services, "
            "enforces rate limits, validates headers, and publishes access logs."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom middleware (applied last-registered = outermost) ───────────────
    app.add_middleware(AccessLogMiddleware)
    app.add_middleware(CorrelationIdMiddleware)
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_bytes=settings.max_request_body_bytes,
    )

    # ── Exception handlers ────────────────────────────────────────────────────
    @app.exception_handler(GatewayError)
    async def gateway_error_handler(request: Request, exc: GatewayError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message},
        )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(gateway_router)

    return app


app = create_app()
