"""Routes management HTTP router."""
from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.application.route_management import RouteManagementService
from src.dependencies import get_route_management_service

router = APIRouter(prefix="/routes", tags=["routes"])


# ── Request / Response schemas ────────────────────────────────────────────────

class RouteCreateRequest(BaseModel):
    """Payload for creating a new route."""

    name: str = Field(..., description="Human-readable route name")
    path_prefix: str = Field(..., description="URL path prefix to match")
    upstream_url: str = Field(..., description="Target upstream base URL")
    strip_prefix: bool = Field(True, description="Strip prefix before forwarding")
    methods: list[str] = Field(default_factory=list, description="Allowed HTTP methods (empty = all)")
    tags: list[str] = Field(default_factory=list, description="Metadata tags")


class RouteResponse(BaseModel):
    """Route representation returned by the API."""

    route_id: str
    name: str
    path_prefix: str
    upstream_url: str
    strip_prefix: bool
    methods: list[str]
    enabled: bool
    tags: list[str]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[RouteResponse], summary="List all routes")
async def list_routes(
    service: RouteManagementService = Depends(get_route_management_service),
) -> list[dict[str, Any]]:
    """Return all registered routing rules."""
    routes = await service.list_routes()
    return [
        {
            "route_id": r.route_id,
            "name": r.name,
            "path_prefix": r.path_prefix,
            "upstream_url": r.upstream_url,
            "strip_prefix": r.strip_prefix,
            "methods": list(r.methods),
            "enabled": r.enabled,
            "tags": list(r.tags),
        }
        for r in routes
    ]


@router.post("/", response_model=RouteResponse, status_code=status.HTTP_201_CREATED, summary="Register a route")
async def create_route(
    payload: RouteCreateRequest,
    service: RouteManagementService = Depends(get_route_management_service),
) -> dict[str, Any]:
    """Register a new routing rule."""
    route = await service.add_route(
        name=payload.name,
        path_prefix=payload.path_prefix,
        upstream_url=payload.upstream_url,
        strip_prefix=payload.strip_prefix,
        methods=frozenset(m.upper() for m in payload.methods),
        tags=tuple(payload.tags),
    )
    return {
        "route_id": route.route_id,
        "name": route.name,
        "path_prefix": route.path_prefix,
        "upstream_url": route.upstream_url,
        "strip_prefix": route.strip_prefix,
        "methods": list(route.methods),
        "enabled": route.enabled,
        "tags": list(route.tags),
    }


@router.get("/{route_id}", response_model=RouteResponse, summary="Get a route")
async def get_route(
    route_id: str,
    service: RouteManagementService = Depends(get_route_management_service),
) -> dict[str, Any]:
    """Retrieve a single route by its ID."""
    route = await service.get_route(route_id)
    if route is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
    return {
        "route_id": route.route_id,
        "name": route.name,
        "path_prefix": route.path_prefix,
        "upstream_url": route.upstream_url,
        "strip_prefix": route.strip_prefix,
        "methods": list(route.methods),
        "enabled": route.enabled,
        "tags": list(route.tags),
    }


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a route")
async def delete_route(
    route_id: str,
    service: RouteManagementService = Depends(get_route_management_service),
) -> None:
    """Remove a routing rule by its ID."""
    removed = await service.remove_route(route_id)
    if not removed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
