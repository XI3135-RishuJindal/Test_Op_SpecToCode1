# PLAN: Upgrade Flask 1.x → 3.1 and Adopt Application Factory Pattern

---

## Overview

**Migration Strategy: Feature-Flag Gated / Strangler-Fig**

The migration will proceed in incremental phases rather than a big-bang rewrite. The application factory pattern is introduced alongside the existing app initialization code, with the old entry point kept functional until each phase is validated. This approach is justified because:

- **Risk:** Flask 2.x and 3.x introduced several breaking changes (removed `flask.ext`, changed `before_first_request`, updated `Markup`/`escape` imports, async support changes) that require careful, testable increments.
- **Effort:** The upgrade option is rated **moderate** — a big-bang rewrite would amplify risk disproportionate to the effort saved.
- **Reversibility:** Each phase produces a independently deployable and reversible artifact.

> **TODO:** Exact risk score and person-days estimate were not provided in the upgrade option. Effort estimates below are derived from the moderate classification and standard Flask migration complexity. Revise when formal estimates are available.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Dependency audit & environment setup — pin current versions, create upgrade branch, establish baseline test coverage | None | TODO person-days (moderate baseline) |
| 2 | Upgrade Flask 1.x → 2.3 (intermediate step) and resolve first-wave breaking changes (`flask.ext` removal, `Markup`/`escape` import paths, `before_first_request` deprecation) | Phase 1 complete | TODO |
| 3 | Introduce application factory (`create_app()`) alongside existing init; migrate configuration loading, extensions, and blueprints into factory | Phase 2 stable | TODO |
| 4 | Upgrade Flask 2.3 → 3.1; resolve second-wave breaking changes (removed `before_first_request`, `send_file` changes, CLI changes) | Phase 3 complete | TODO |
| 5 | Cut over all entry points (`wsgi.py`, CLI, test fixtures) to use `create_app()`; remove legacy init code | Phase 4 validated | TODO |
| 6 | Regression, performance, and security validation; update CI/CD gates; documentation | Phase 5 complete | TODO |

> **TODO:** Populate person-days per phase once the formal upgrade option estimate is provided.

---

## Component Changes

### 1. Application Entry Point

**What changes:** The module-level `app = Flask(__name__)` instantiation is replaced by a `create_app(config=None)` factory function.

**Files affected:**
- `app.py` or `application.py` (TODO: confirm actual filename from repo) — primary change target
- `wsgi.py` — update to call `create_app()` instead of importing a module-level `app`
- `run.py` or `manage.py` (if present) — update similarly

**Structural change:**
```python
# BEFORE (Flask 1.x pattern)
app = Flask(__name__)
app.config.from_object('config.ProductionConfig')

# AFTER (factory pattern)
def create_app(config=None):
    app = Flask(__name__)
    if config is None:
        app.config.from_object('config.ProductionConfig')
    else:
        app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    return app
```

### 2. Extensions Initialization

**What changes:** All extension objects (e.g., `db = SQLAlchemy()`, `login_manager = LoginManager()`, `migrate = Migrate()`) must be instantiated without the `app` argument and initialized inside the factory via `extension.init_app(app)`.

**Files affected:**
- `extensions.py` (create this file if it does not exist — TODO: confirm)
- Any file currently doing `db = SQLAlchemy(app)` at module level

### 3. Blueprints Registration

**What changes:** Blueprint imports and `app.register_blueprint()` calls move inside `create_app()`.

**Files affected:**
- `app.py` / `application.py`
- All `routes.py` or `views.py` files that reference the module-level `app` directly (e.g., `@app.route(...)`) — these must use blueprint decorators instead

### 4. `before_first_request` Removal (Flask 2.x → 3.x breaking change)

**What changes:** `@app.before_first_request` was deprecated in Flask 2.2 and **removed in Flask 3.0**. Any usage must be replaced.

**Migration:** Move one-time startup logic into the factory body directly, or use a flag-guarded `@app.before_request` handler.

**Files affected:** TODO — search codebase for `before_first_request`

### 5. `Markup` and `escape` Import Paths

**What changes:** In Flask 3.x, `flask.Markup` and `flask.escape` are removed. They must be imported from `markupsafe` directly.

```python
# BEFORE
from flask import Markup, escape

# AFTER
from markupsafe import Markup, escape
```

**Files affected:** TODO — search codebase for `from flask import Markup` and `from flask import escape`

### 6. Test Fixtures

**What changes:** `pytest` fixtures that reference a module-level `app` object must be updated to call `create_app(test_config)`.

**Files affected:**
- `conftest.py` — update `app` fixture and `client` fixture
- Any test file with `from app import app`

### 7. Configuration Module

**What changes:** Configuration classes remain largely unchanged, but the factory must explicitly load them. Environment-specific config selection logic moves into `create_app()`.

**Files affected:**
- `config.py` — no structural change expected; verify `SECRET_KEY`, `TESTING`, `DEBUG` keys are present

---

## Dependency Upgrade Plan

> **TODO:** The tech analysis did not provide current pinned version numbers for dependencies beyond "Flask 1.x". The table below uses known Flask ecosystem compatibility ranges. **All versions must be verified against the actual `requirements.txt` or `Pipfile` before execution.**

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Flask | 1.x | 3.1 | `before_first_request` removed; `flask.escape`/`flask.Markup` removed; `send_file` `attachment_filename` param renamed to `download_name`; `flask.json` provider API changed | Upgrade via 2.3 as intermediate step; see Phase 2 and 4 |
| Werkzeug | TODO (pinned with Flask 1.x, likely 1.x) | 3.1.x | `werkzeug.utils.send_file` signature changes; `ImmutableMultiDict` changes | Must be upgraded in lockstep with Flask |
| Jinja2 | TODO (likely 2.x) | 3.1.x | `Undefined` behavior changes; `Environment` API minor changes | Upgrade alongside Flask; test all templates |
| MarkupSafe | TODO (likely 1.x) | 3.x | `flask.Markup` and `flask.escape` now delegate here exclusively | Import paths must be updated in application code |
| click | TODO | 8.x | Some CLI decorator changes | Flask 3.x requires click 8.x |
| itsdangerous | TODO | 2.x | `TimedJSONWebSignatureSerializer` removed | Audit any token/signing code |
| Flask-SQLAlchemy | TODO | TODO | `init_app()` pattern required; session scoping changes in 3.x | TODO — verify version compatibility with Flask 3.1 |
| Flask-Login | TODO | TODO | `login_manager.init_app(app)` pattern required | TODO — verify version compatibility |
| Flask-Migrate | TODO | TODO | Must use `init_app()` pattern | TODO — verify version compatibility |

> **TODO:** All "TODO" version cells must be populated from the actual `requirements.txt` / `Pipfile.lock` before Phase 1 begins.

---

## Infrastructure Changes

> **TODO:** No infrastructure context (Docker, Kubernetes, CI/CD, IaC) was provided. The following items are flagged for investigation:

- **Docker base image:** TODO — verify current base image Python version is compatible with Flask 3.1 requirements (Python 3.8+ required; Python 3.10+ recommended). Update `Dockerfile` `FROM` line if needed.
- **WSGI server:** TODO — verify `gunicorn` or `uWSGI` version is compatible with Flask 3.1 / Werkzeug 3.x. `gunicorn >= 21.x` is recommended.
- **CI/CD pipeline:** TODO — add a lint/import-check step that catches `from flask import Markup` and `before_first_request` usage. Update test commands to use `create_app('testing')` invocation pattern.
- **Environment variables:** TODO — confirm `FLASK_APP` environment variable points to the factory function (e.g., `FLASK_APP=app:create_app`) after migration.
- **Kubernetes manifests:** TODO — not derivable from provided context.
- **IaC (Terraform/Pulumi/etc.):** TODO — not derivable from provided context.

---

## Rollback Strategy

Each phase produces a tagged git commit and (TODO) a deployable artifact. Rollback is per-phase.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** | Delete upgrade branch. No production change has occurred. Restore pinned `requirements.txt` from main branch. |
| **Phase 2** | `git revert` commits in upgrade branch back to Phase 1 tag. Reinstall dependencies from Phase 1 `requirements.txt`. Run baseline test suite to confirm green. |
| **Phase 3** | Revert factory introduction commits. The module-level `app` object is still present (it was not removed in Phase 3). Redeploy from Phase 2 tag. |
| **Phase 4** | Revert Flask 3.1 upgrade commits. Reinstall Flask 2.3 and compatible Werkzeug/Jinja2 from Phase 3 `requirements.txt`. Redeploy from Phase 3 tag. |
| **Phase 5** | Revert entry-point cutover. The legacy `app` import path was preserved until this phase; restore it. Redeploy from Phase 4 tag. |
| **Phase 6** | No code changes in Phase 6 (validation only). If a defect is found, roll back to Phase 5 tag. |

**General rollback prerequisites:**
- Each phase must be tagged in git before merging (e.g., `upgrade/flask3-phase-N`).
- `requirements.txt` (or lockfile) must be committed at each phase boundary.
- TODO: Define artifact promotion strategy (container image tags, etc.) once infrastructure context is available.

---

## Testing Strategy

### Test Pyramid

```
         [ Performance ]
        [ Regression / E2E ]
      [ Integration Tests ]
    [ Unit Tests ]          ← widest base
```

### Unit Tests
- **Tool:** `pytest` with `pytest-flask`
- **Scope:** All view functions, utility functions, model methods, config loading
- **Key fixture change:** `conftest.py` must provide an `app` fixture via `create_app('testing')` and a `client` fixture via `app.test_client()`
- **Coverage target:** TODO (establish baseline in Phase 1; target ≥ existing baseline, recommend ≥ 80%)
- **CI gate:** Fail build if coverage drops below baseline

### Integration Tests
- **Tool:** `pytest` + `pytest-flask` + real or in-memory database (TODO: confirm DB stack)
- **Scope:** Blueprint route registration, extension initialization (DB, login, migrate), request/response cycle through factory-created app
- **Key checks:** All routes registered correctly after `create_app()`; extensions accessible via `current_app`; no `RuntimeError: Working outside of application context`

### Regression Tests
- **Tool:** `pytest` (existing test suite must pass without modification after each phase)
- **Scope:** Full existing test suite run against each phase's code
- **CI gate:** Zero regression failures required to advance to next phase

### Performance Tests
- **Tool:** TODO (no performance testing infrastructure specified in context — recommend `locust` or `wrk` if not already present)
- **Scope:** Baseline request throughput and latency captured in Phase 1; re-measured in Phase 6 to confirm no regression introduced by factory overhead (factory overhead is negligible but should be confirmed)
- **CI gate:** TODO

### Specific Test Cases to Add

| Test | Phase | Purpose |
|------|-------|---------|
| `test_create_app_returns_flask_instance` | 3 | Verify factory returns valid `Flask` object |
| `test_create_app_with_test_config` | 3 | Verify `TESTING=True` config is applied |
| `test_extensions_initialized` | 3 | Verify `db`, `login_manager`, etc. are bound to app |
| `test_blueprints_registered` | 3 | Verify all expected URL rules exist |
| `test_no_before_first_request_usage` | 4 | Static analysis / grep check in CI |
| `test_markup_import_from_markupsafe` | 4 | Static analysis / grep check in CI |

---

## Timeline

> **TODO:** Formal person-days were not provided in the upgrade option. The table below uses relative ordering. Populate calendar dates and owners once the team is assigned and estimates are confirmed.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Baseline established, branch created, `requirements.txt` pinned | Phase 1 | TODO | TODO |
| Flask 2.3 upgrade green on CI | Phase 2 | TODO | TODO |
| `create_app()` factory merged, all extensions migrated | Phase 3 | TODO | TODO |
| Flask 3.1 upgrade green on CI | Phase 4 | TODO | TODO |
| All entry points cut over to factory; legacy init removed | Phase 5 | TODO | TODO |
| Regression + performance sign-off; CI gates updated; docs updated | Phase 6 | TODO | TODO |
| **Production deployment** | Post-Phase 6 | TODO | TODO |

---

*Document status: DRAFT — all TODO items must be resolved before Phase 1 begins.*