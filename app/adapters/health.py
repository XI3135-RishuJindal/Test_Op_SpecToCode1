"""Health-check blueprint."""

from flask import Blueprint, jsonify
from typing import Tuple

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check() -> Tuple[object, int]:
    """Return service liveness status."""
    return jsonify({"status": "ok", "service": "authentication-service"}), 200
