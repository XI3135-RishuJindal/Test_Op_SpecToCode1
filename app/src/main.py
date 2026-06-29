"""FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.adapters.http.health_router import router as health_router
from src.adapters.http.proxy_router import router as proxy_router
from src.adapters.http.routes_router import router as routes_router
from src.config import get_settings


def create_app() -> FastAPI:
    """Construct and configure the FastAPI application.

    Returns:
        A fully configured :class:`fastapi.FastAPI` instance.
    """
    settings = get_settings()

    app = FastAPI(
        title="API Gateway Service",
        description=(
            "Central API Gateway responsible for routing API requests, "
            "implementing security measures, and monitoring traffic and usage."
        ),
        version=settings.app_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── CORS middleware ───────────────────────────────────────────────────────
    origins = [o.strip() for o in settings.cors_allowed_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=[m.strip() for m in settings.cors_allowed_methods.split(",")],
        allow_headers=[h.strip() for h in settings.cors_allowed_headers.split(",")],
    )

    # ── Routers ───────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(routes_router, prefix="/api/v1")
    app.include_router(proxy_router, prefix="/api/v1")

    return app


# Module-level app instance (used by uvicorn and tests)
app: FastAPI = create_app()
