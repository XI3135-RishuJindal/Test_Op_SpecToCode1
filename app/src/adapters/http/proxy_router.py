"""Proxy / forwarding HTTP router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from src.application.proxy_service import ProxyService
from src.dependencies import get_proxy_service

router = APIRouter(prefix="/proxy", tags=["proxy"])


@router.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    summary="Proxy a request to an upstream service",
)
async def proxy_request(
    path: str,
    request: Request,
    service: ProxyService = Depends(get_proxy_service),
) -> Response:
    """Forward the incoming request to the matching upstream service.

    The gateway resolves the best matching route, rewrites the path,
    forwards the request, and streams the upstream response back to the
    caller.
    """
    full_path = f"/{path}"
    body = await request.body()
    headers = dict(request.headers)
    # Remove hop-by-hop headers
    for hop in ("host", "transfer-encoding", "connection"):
        headers.pop(hop, None)

    result = await service.proxy(
        method=request.method,
        path=full_path,
        headers=headers,
        body=body if body else None,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No matching route found for the requested path.",
        )

    upstream_status, upstream_headers, upstream_body = result
    # Strip hop-by-hop headers from upstream response
    for hop in ("transfer-encoding", "connection", "keep-alive"):
        upstream_headers.pop(hop, None)

    return Response(
        content=upstream_body,
        status_code=upstream_status,
        headers=upstream_headers,
    )
