"""
compat_shim.py

Compatibility and migration helper for the upgrade context provided.

NOTE:
- The provided spec.md/design.md context is documentation-focused and does not enumerate concrete
  legacy names/keys beyond: DATABASE_URL, "create_all at import", and "migrations (Alembic)".
- Per instruction, this shim only uses names present in the provided context and avoids inventing
  project-specific API/class/config names.

This module provides:
- Deprecated API replacements (limited to what is named in context).
- Renamed packages/classes (no concrete names provided in context).
- Config format migration: hardcoded DATABASE_URL -> environment-based config.
- TODO markers where manual intervention is required, citing specific breaking changes.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, Mapping, MutableMapping, Optional


# ----------------------------
# Config migration helpers
# ----------------------------

@dataclass(frozen=True)
class ConfigMigrationResult:
    new_config: Dict[str, Any]
    notes: str


def migrate_config(old_config: Optional[Mapping[str, Any]] = None) -> ConfigMigrationResult:
    """
    Transform legacy configuration to the new configuration model described in the upgrade context.

    Supported migration (from provided context):
    - Externalize configuration and remove hardcoded DATABASE_URL; integrate environment-based config.

    Inputs:
      old_config: previous config mapping (possibly containing DATABASE_URL)

    Output:
      ConfigMigrationResult:
        new_config: migrated configuration mapping
        notes: human-readable notes and TODOs for follow-ups.

    IMPORTANT:
    - The spec/design context does not define the complete new config schema, precedence rules,
      or secrets management mechanism; this function therefore focuses on removing hardcoded
      DATABASE_URL and deferring to env-based configuration.
    """
    src: Dict[str, Any] = dict(old_config or {})
    dst: Dict[str, Any] = {}
    notes_parts = []

    # Breaking change cited in context: "Externalize configuration and remove hardcoded DATABASE_URL"
    if "DATABASE_URL" in src:
        # Remove from config and advise to set via environment.
        legacy_value = src.pop("DATABASE_URL")
        # Preserve for visibility only; callers may choose to drop this completely.
        dst["DATABASE_URL"] = os.environ.get("DATABASE_URL", legacy_value)
        notes_parts.append(
            "Migrated DATABASE_URL to prefer environment variable DATABASE_URL; "
            "legacy hardcoded value retained only as fallback."
        )
        notes_parts.append(
            "TODO (breaking change: externalize configuration): Remove any remaining hardcoded "
            "DATABASE_URL usage in code and rely on env/secrets management."
        )
    else:
        # Still provide an env-resolved value if present.
        env_value = os.environ.get("DATABASE_URL")
        if env_value is not None:
            dst["DATABASE_URL"] = env_value
            notes_parts.append("Loaded DATABASE_URL from environment variable DATABASE_URL.")

    # Carry forward any remaining keys unchanged (context doesn't define a full schema).
    for k, v in src.items():
        dst[k] = v

    # Breaking change cited in context: "Introduce ... migrations (Alembic) instead of create_all at import"
    notes_parts.append(
        "TODO (breaking change: migrations workflow): Replace any 'create_all at import' behavior "
        "with migrations (Alembic). This helper cannot auto-migrate that code path from docs alone."
    )

    # Flask 1.x -> 3.x and SQLAlchemy 1.3 -> 2.x mentioned but without concrete code-level API names.
    notes_parts.append(
        "TODO (breaking change: Flask 1.x -> Flask 3.x): Refactor to modern patterns (app factory, "
        "config via env, WSGI server). Exact code changes depend on your application entrypoints."
    )
    notes_parts.append(
        "TODO (breaking change: SQLAlchemy 1.3 -> SQLAlchemy 2.x): Adopt modern session/engine patterns. "
        "Exact replacements depend on how engines/sessions are currently created and used."
    )

    return ConfigMigrationResult(new_config=dst, notes="\n".join(notes_parts))


# ----------------------------
# Deprecated API replacements
# ----------------------------

def create_all_at_import(*args: Any, **kwargs: Any) -> None:
    """
    Deprecated helper to represent the legacy pattern "create_all at import".

    This function exists as a compatibility shim so legacy import-time side effects can be
    redirected to the new migration workflow.

    The context explicitly calls out that this must be replaced with migrations (Alembic).
    Since Alembic is only mentioned (no concrete API/functions provided), this shim does not
    invoke Alembic directly.

    TODO (breaking change: migrations instead of create_all at import):
      Remove calls to this function and trigger migrations (Alembic) in your operational workflow.
    """
    raise RuntimeError(
        "Legacy 'create_all at import' behavior is not supported after upgrade. "
        "Use migrations (Alembic) instead. "
        "TODO (breaking change: migrations instead of create_all at import): "
        "Replace import-time create_all with an explicit migration workflow."
    )


# ----------------------------
# Renamed packages/classes shims
# ----------------------------
# The provided context does not name any renamed packages/classes beyond tool/framework versions,
# and we must not invent names. Therefore, this section intentionally contains no import aliases.

# TODO (breaking change: Flask 1.x -> Flask 3.x): If your code imports symbols that moved/renamed
# between Flask 1.x and 3.x, add explicit import shims here using only concrete names found in
# your project's codebase and the provided upgrade design/spec context.


# ----------------------------
# Minimal runtime/config access helpers
# ----------------------------

def get_database_url(config: Optional[Mapping[str, Any]] = None) -> Optional[str]:
    """
    Retrieve DATABASE_URL with env precedence, supporting legacy config mappings.

    This is a small compatibility helper aligned with:
    - "Externalize configuration and remove hardcoded DATABASE_URL; integrate ... environment-based config"

    Returns:
      DATABASE_URL value or None if not set anywhere.
    """
    if "DATABASE_URL" in os.environ:
        return os.environ["DATABASE_URL"]
    if config and "DATABASE_URL" in config:
        return str(config["DATABASE_URL"])
    return None


def ensure_env_config(config: Optional[MutableMapping[str, Any]] = None) -> Dict[str, Any]:
    """
    Ensure configuration prefers environment values.

    This helper merges environment-based DATABASE_URL into a config dict.

    NOTE:
    - The context does not define additional config keys, precedence rules, or validation.
      This function therefore only handles DATABASE_URL.
    """
    merged: Dict[str, Any] = dict(config or {})
    if "DATABASE_URL" in os.environ:
        merged["DATABASE_URL"] = os.environ["DATABASE_URL"]
    return merged


__all__ = [
    "ConfigMigrationResult",
    "migrate_config",
    "create_all_at_import",
    "get_database_url",
    "ensure_env_config",
]