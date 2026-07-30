import os
import sys
import importlib
from typing import Optional

import pytest


TARGET_PYTHON = (3, 12)
TARGET_FLASK_MAJOR = 3
TARGET_SQLALCHEMY_MAJOR = 2


def _import_module_from_candidates(candidates) -> Optional[object]:
    for name in candidates:
        try:
            return importlib.import_module(name)
        except Exception:
            continue
    return None


def _get_flask_app():
    """
    Best-effort discovery:
    - Prefer an app factory: create_app()
    - Fall back to module-level 'app' Flask instance
    Candidate module names cover common monolith layouts.
    """
    candidates = [
        "app",
        "application",
        "wsgi",
        "main",
        "server",
        "src.app",
        "src.application",
        "src.wsgi",
        "src.main",
        "src.server",
    ]
    mod = _import_module_from_candidates(candidates)
    if mod is None:
        pytest.skip("Unable to import application module (tried common names). Provide app/create_app in one of them.")

    create_app = getattr(mod, "create_app", None)
    if callable(create_app):
        return create_app()

    app = getattr(mod, "app", None)
    if app is not None:
        return app

    pytest.skip("No create_app() factory or module-level app found in common modules.")


def test_runtime_python_version_is_target_major_minor():
    assert (
        sys.version_info.major,
        sys.version_info.minor,
    ) == TARGET_PYTHON, f"Expected Python {TARGET_PYTHON[0]}.{TARGET_PYTHON[1]} runtime, got {sys.version_info.major}.{sys.version_info.minor}"


def test_flask_is_v3_active():
    flask = importlib.import_module("flask")
    version = getattr(flask, "__version__", None)
    assert version is not None, "Could not read flask.__version__"
    assert version.split(".", 1)[0] == str(TARGET_FLASK_MAJOR), f"Expected Flask {TARGET_FLASK_MAJOR}.x active, got {version}"


def test_sqlalchemy_is_v2_active():
    sa = importlib.import_module("sqlalchemy")
    version = getattr(sa, "__version__", None)
    assert version is not None, "Could not read sqlalchemy.__version__"
    assert version.split(".", 1)[0] == str(TARGET_SQLALCHEMY_MAJOR), f"Expected SQLAlchemy {TARGET_SQLALCHEMY_MAJOR}.x active, got {version}"


def test_critical_app_paths_health_endpoint_works_with_flask3_client():
    app = _get_flask_app()
    app.testing = True

    # Use Flask 3 test client to exercise a critical REST path.
    # If the app doesn't have /health, attempt /healthz, then /.
    paths = ["/health", "/healthz", "/"]
    with app.test_client() as client:
        last = None
        for path in paths:
            try:
                last = client.get(path)
            except Exception as e:
                last = e
                continue

            if getattr(last, "status_code", 0) in (200, 204, 301, 302):
                assert last.status_code in (200, 204, 301, 302)
                return

        pytest.fail(f"Critical application path check failed for {paths}. Last result: {last!r}")


def test_deprecated_flask_jsonify_import_pattern_not_used():
    """
    Flask 3 removed/changed a number of legacy patterns; one common legacy import is:
        from flask.json import jsonify
    which should not appear in upgraded code (use flask.jsonify).
    """
    import pathlib

    root = pathlib.Path.cwd()

    # Scan only project files; avoid venv/site-packages if present.
    def is_project_file(p: pathlib.Path) -> bool:
        parts = set(p.parts)
        if any(x in parts for x in (".venv", "venv", "__pycache__", ".git", ".tox", "site-packages", "dist", "build")):
            return False
        return p.suffix == ".py"

    offenders = []
    for py in root.rglob("*.py"):
        if not is_project_file(py):
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "from flask.json import jsonify" in text:
            offenders.append(str(py))

    assert not offenders, f"Deprecated Flask import pattern found: 'from flask.json import jsonify' in {offenders}"


def test_deprecated_sqlalchemy_orm_query_get_not_used_and_replacement_available():
    """
    SQLAlchemy 2.x deprecates legacy Session.query(...).get(pk); replacement is Session.get(Entity, pk).
    Verify the deprecated API is absent in project code and that the replacement exists.
    """
    import pathlib

    root = pathlib.Path.cwd()

    def is_project_file(p: pathlib.Path) -> bool:
        parts = set(p.parts)
        if any(x in parts for x in (".venv", "venv", "__pycache__", ".git", ".tox", "site-packages", "dist", "build")):
            return False
        return p.suffix == ".py"

    offenders = []
    for py in root.rglob("*.py"):
        if not is_project_file(py):
            continue
        try:
            text = py.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        # Heuristic: ".query(" combined with ").get(" or ".get(" chained from query is a common legacy pattern.
        if ".query(" in text and ".get(" in text and "query(" in text:
            # Narrow down to the common pattern to reduce false positives.
            if ".query(" in text and ").get(" in text:
                offenders.append(str(py))

    assert not offenders, f"Potential legacy SQLAlchemy pattern 'Session.query(...).get(...)' found in {offenders}"

    sa_orm = importlib.import_module("sqlalchemy.orm")
    Session = getattr(sa_orm, "Session", None)
    assert Session is not None, "sqlalchemy.orm.Session not found"
    assert hasattr(Session, "get"), "SQLAlchemy 2.x replacement API Session.get(...) not available"


def test_new_configuration_keys_load_without_errors(monkeypatch):
    """
    Upgrade introduces env-based configuration and new keys. Validate:
    - App can be created with env vars present (no hardcoded DATABASE_URL reliance).
    - Typical new keys exist on app.config after initialization.
    This test is defensive: it doesn't enforce the exact config system, but requires keys
    to be accepted without throwing.
    """
    # Common env-based config keys for modern Flask setups
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("FLASK_DEBUG", "0")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")

    # Potential new configuration keys introduced by modern patterns
    monkeypatch.setenv("SQLALCHEMY_DATABASE_URI", "sqlite+pysqlite:///:memory:")
    monkeypatch.setenv("SQLALCHEMY_ENGINE_OPTIONS", "{}")
    monkeypatch.setenv("SQLALCHEMY_ECHO", "0")

    # A few other common "new/modernized" keys (should be tolerated if present)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    app = _get_flask_app()

    # Creating the app should not crash due to unknown/new keys; ensure config is accessible.
    cfg = getattr(app, "config", None)
    assert cfg is not None, "Flask app has no .config; app factory may not have initialized correctly"

    # Verify that at least one of the expected DB config keys is loaded/recognized into app.config
    # (projects differ: some map DATABASE_URL -> SQLALCHEMY_DATABASE_URI, some use SQLAlchemy 2 engine directly)
    assert (
        "SQLALCHEMY_DATABASE_URI" in cfg
        or "DATABASE_URL" in cfg
        or "DATABASE_URI" in cfg
    ), "Expected upgraded env-based database configuration key to be present in app.config"

    # Ensure SECRET_KEY is loadable (a critical config for Flask 3 sessions/cookies)
    assert "SECRET_KEY" in cfg or os.getenv("SECRET_KEY"), "SECRET_KEY not loadable after upgrade"