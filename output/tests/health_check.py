#!/usr/bin/env python3
"""
health_check.py — Docker HEALTHCHECK script for Account Management Service.

Invokes the compiled ACCTHLTH binary and exits 0 (healthy) or 1 (unhealthy).
Used by the Dockerfile HEALTHCHECK instruction.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

BIN_DIR = Path(os.environ.get("BIN_DIR", "/app/bin"))
HEALTH_BINARY = BIN_DIR / "ACCTHLTH"


def run_health_check() -> int:
    """
    Execute ACCTHLTH and return 0 if healthy, 1 otherwise.

    Returns:
        int: 0 for healthy, 1 for unhealthy.
    """
    if not HEALTH_BINARY.exists():
        print(
            f"[HEALTH] ERROR: binary not found at {HEALTH_BINARY}",
            file=sys.stderr,
        )
        return 1

    try:
        result = subprocess.run(
            [str(HEALTH_BINARY)],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        print("[HEALTH] ERROR: health check timed out", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[HEALTH] ERROR: could not execute binary: {exc}", file=sys.stderr)
        return 1

    if result.returncode != 0:
        print(
            f"[HEALTH] UNHEALTHY: exit code {result.returncode}\n{result.stderr}",
            file=sys.stderr,
        )
        return 1

    output = result.stdout
    if "UP" not in output:
        print(
            f"[HEALTH] UNHEALTHY: status not UP in output:\n{output}",
            file=sys.stderr,
        )
        return 1

    print(f"[HEALTH] OK: {output.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(run_health_check())
