"""
Uvicorn entrypoint for the API Gateway / BFF Service.

Run directly:
    python -m app.entrypoint

Or via uvicorn:
    uvicorn app.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations

import uvicorn

from app.infrastructure.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        log_config=None,   # We manage logging ourselves
        access_log=False,  # Handled by AccessLogMiddleware
    )


if __name__ == "__main__":
    main()
