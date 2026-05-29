# PLAN: Upgrade Flask 1.x → 3.1 and Adopt Application Factory Pattern

---

## Overview

**Migration Strategy: Feature-Flag Gated / Strangler-Fig**

The migration will proceed in incremental phases, refactoring the application toward the factory pattern while keeping the existing entry point functional until the new structure is fully validated. This avoids a risky big-bang rewrite.

**Justification:**
- The upgrade urgency is rated **medium**, indicating the existing application is functional but accumulating technical debt.
- Flask 1.x → 3.1 spans multiple major versions with several breaking changes (notably the removal of `flask.ext`, changes to `before_first_request`, `flask.json` module restructuring, and Werkzeug 3.x compatibility requirements). These warrant a phased approach rather than a single cutover.
- The application factory pattern refactor is a structural change that touches entry points, extension initialization, and test fixtures — making parallel validation essential before decommissioning the old structure.
- Effort is classified as **moderate**, supporting a phased plan over a bounded timeframe rather than a long-running parallel run.

> **TODO:** Confirm whether the application currently uses a global `app = Flask(__name__)` pattern at module level, and identify all Blueprint registrations and extension initializations before beginning Phase 1.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| **1** | Dependency audit & environment preparation — pin current versions, create a parallel virtual environment, identify all Flask extension compatibility with Flask 3.1 | None | TODO (derive from moderate estimate once person-days are confirmed) |
| **2** | Dependency upgrades — upgrade Flask, Werkzeug, Jinja2, Click, and all Flask extensions to Flask 3.1-compatible versions | Phase 1 complete | TODO |
| **3** | Application factory refactor — introduce `create_app()` factory function, move extension initialization inside factory, update all entry points | Phase 2 complete | TODO |
| **4** | Blueprint and extension wiring — register all Blueprints and extensions inside `create_app()`, remove module-level `app` references | Phase 3 complete | TODO |
| **5** | Test suite migration — update test fixtures to use the factory, replace deprecated test client usage, add regression coverage | Phase 4 complete | TODO |
| **6** | Validation & cutover — run full test suite, performance baseline, remove legacy entry point, update CI/CD | Phase 5 complete | TODO |

> **TODO:** Populate Estimated Effort columns once the upgrade option's person-days breakdown is provided.

---

## Component Changes

### 1. Application Entry Point

**What changes:** The module-level `app = Flask(__name__)` instantiation must be replaced with a `create_app(config=None)` factory function.

**Files affected:**
- `app.py` or `wsgi.py` (primary entry point — **TODO:** confirm filename from codebase)
- Any `run.py` or `manage.py` that references the global `app` object directly

**Structural change:**

```python
# BEFORE (Flask 1.x pattern)
app = Flask(__name__)
app.config.from_object('config.Config')

# AFTER (Flask 3.1 factory pattern)
def create_app(config=None):
    app = Flask(__name__)
    if config is None:
        app.config.from_object('config.Config')
    else:
        app.config.from_object(config)
    # register extensions, blueprints here
    return app
```

**APIs modified:**
- Remove all module-level `app` references that are imported by other modules
- Update `if __name__ == '__main__': app.run()` to call `create_app().run()`

---

### 2. Extension Initialization

**What changes:** Extensions initialized with `ext.init_app(app)` pattern must be moved inside `create_app()`. Any extensions using the deprecated `flask.ext.*` import namespace must be updated to their direct package imports.

**Files affected:**
- `extensions.py` (if present — **TODO:** confirm) or wherever `db`, `login_manager`, `migrate`, etc. are instantiated
- All files importing from `flask.ext.*` (removed in Flask 1.0, must be absent by Flask 3.1)

**Structural change:**

```python
# extensions.py — instantiate without app
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

# create_app() — bind to app
def create_app(config=None):
    app = Flask(__name__)
    ...
    db.init_app(app)
    return app
```

---

### 3. `before_first_request` Removal

**What changes:** `@app.before_first_request` decorator was deprecated in Flask 2.2 and **removed in Flask 2.3+**. Any usage must be replaced.

**Files affected:** **TODO** — search codebase for `before_first_request`

**Migration:** Move logic into `create_app()` directly, or use an `app.with_appcontext` wrapper, or register a CLI command for one-time setup tasks.

---

### 4. Blueprint Registration

**What changes:** All Blueprint `app.register_blueprint()` calls must occur inside `create_app()`.

**Files affected:**
- **TODO:** Identify all Blueprint definition files and their current registration locations

**Structural change:**

```python
def create_app(config=None):
    app = Flask(__name__)
    ...
    from .blueprints.auth import auth_bp
    from .blueprints.main import main_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    return app
```

---

### 5. Configuration Module

**What changes:** Config classes remain largely unchanged, but `SECRET_KEY` and `SESSION_COOKIE_SAMESITE` defaults have changed in Flask 3.x. Review all config keys.

**Files affected:**
- `config.py` or `settings.py` (**TODO:** confirm filename)

**Key config changes for Flask 3.1:**
- `SESSION_COOKIE_SAMESITE` defaults to `"Lax"` — verify this is acceptable
- `PROPAGATE_EXCEPTIONS` behavior updated — review if relied upon
- `JSON_SORT_KEYS`, `JSON_AS_ASCII`, `JSONIFY_PRETTYPRINT_REGULAR` — removed; configure via `app.json` object instead

---

### 6. JSON Handling

**What changes:** `flask.json` module was restructured. `flask.json.provider` is the new interface in Flask 2.2+.

**Files affected:** **TODO** — search for `flask.json`, `jsonify`, `current_app.json_encoder`

**Migration:**
- Replace custom `JSONEncoder` subclasses with `app.json_provider_class` or `app.json.default`
- `flask.json.dumps/loads` still available but behavior may differ

---

### 7. Test Fixtures

**What changes:** Tests using a module-level `app` import must be updated to call `create_app(test_config)`.

**Files affected:**
- `conftest.py`
- All test files importing `app` directly

**Structural change:**

```python
# conftest.py
import pytest
from myapp import create_app

@pytest.fixture()
def app():
    app = create_app({'TESTING': True, 'DATABASE': ':memory:'})
    yield app

@pytest.fixture()
def client(app):
    return app.test_client()
```

---

## Dependency Upgrade Plan

> **TODO:** The tech analysis did not provide specific current version pins or confirmed target versions for all dependencies. The table below reflects known Flask 3.1 ecosystem requirements. **All version numbers must be validated against the project's actual `requirements.txt` / `pyproject.toml` before execution.**

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `flask` | 1.x | 3.1.x | Yes — multiple across 2.x and 3.x | See component changes above; `before_first_request` removed, `flask.ext` removed, JSON provider changed |
| `werkzeug` | TODO | 3.x | Yes — `werkzeug.serving`, routing API changes | Flask 3.1 requires Werkzeug 3.x; review any direct Werkzeug imports |
| `jinja2` | TODO | 3.1.x | Minor | Flask 3.1 requires Jinja2 3.x; `Markup` import moved to `markupsafe` |
| `click` | TODO | 8.x | Minor | Flask 3.1 requires Click 8.x; review custom CLI commands |
| `itsdangerous` | TODO | 2.x | Minor | Required by Flask 3.x; API largely stable |
| `flask-sqlalchemy` | TODO | 3.x | Yes | Flask-SQLAlchemy 3.x drops Python 2, changes `Model` base class, removes `SQLALCHEMY_TRACK_MODIFICATIONS` default |
| `flask-login` | TODO | 0.6.x+ | Minor | Ensure `login_manager.init_app(app)` pattern used |
| `flask-migrate` | TODO | 4.x | Minor | Requires Flask-SQLAlchemy 3.x |
| `flask-wtf` | TODO | 1.x | Minor | CSRF handling updated |
| `pytest-flask` | TODO | Latest compatible | Minor | Update fixtures to factory pattern |

> **TODO:** Run `pip-audit` or `safety check` after upgrading to identify any transitive dependency conflicts.

---

## Infrastructure Changes

> **TODO:** No Docker, Kubernetes, or CI/CD configuration was provided in the context. The following are conditional recommendations — confirm applicability before implementing.

- **Docker base image:** TODO — if a `Dockerfile` exists, verify the Python base image supports the target Python version required by Flask 3.1 (Python 3.8+ minimum; Python 3.10+ recommended). Update `FROM python:3.x-slim` accordingly.
- **WSGI server:** TODO — if using `gunicorn`, confirm the `gunicorn` version is compatible with Flask 3.1/Werkzeug 3.x. The WSGI entry point string (e.g., `myapp:app`) must be updated to `myapp:create_app()` or a dedicated `wsgi.py` that calls `create_app()`.
- **CI/CD pipeline:** TODO — add a lint/test stage that runs against the upgraded dependencies in isolation before merging. Confirm pipeline config file location (`.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`, etc.).
- **Environment variables:** Review all `FLASK_ENV` usages — `FLASK_ENV=development` was deprecated in Flask 2.2 and removed in Flask 2.3. Replace with `FLASK_DEBUG=1`.

---

## Rollback Strategy

### Phase 1 Rollback (Dependency Audit)
- No code changes made in this phase; rollback is N/A.
- Discard the parallel virtual environment.

### Phase 2 Rollback (Dependency Upgrades)
- Restore `requirements.txt` (or `pyproject.toml`) to the pre-upgrade pin file saved at the start of Phase 1.
- Run `pip install -r requirements.txt.bak` to restore the previous environment.
- No application code has changed; the application remains functional on Flask 1.x.

### Phase 3 Rollback (Factory Refactor)
- The factory function should be introduced on a **feature branch**. If validation fails, delete or abandon the branch.
- If merged, revert the commit introducing `create_app()` and restore the module-level `app` instantiation.
- Actionable git command: `git revert <commit-sha>` targeting the factory introduction commit.

### Phase 4 Rollback (Blueprint/Extension Wiring)
- Revert Blueprint registration commits individually: `git revert <commit-sha>` per Blueprint.
- Each Blueprint registration change is independently reversible if committed atomically.

### Phase 5 Rollback (Test Suite Migration)
- Test-only changes; rollback by reverting `conftest.py` and test file changes.
- Does not affect production runtime.

### Phase 6 Rollback (Cutover)
- If the legacy entry point was removed, restore it from version control: `git checkout <pre-cutover-sha> -- wsgi.py` (TODO: confirm filename).
- Redeploy the previous Docker image tag (TODO: confirm image registry and tagging strategy).
- Revert CI/CD pipeline changes to point to the previous entry point.

---

## Testing Strategy

### Test Pyramid

#### Unit Tests
- **Scope:** Individual route handlers, utility functions, model methods, config loading
- **Tool:** `pytest`
- **Factory usage:** Each unit test that requires an app context must use `create_app({'TESTING': True})`
- **Coverage target:** TODO — establish baseline coverage before migration; target no regression below current baseline; aim for ≥80% line coverage post-migration
- **CI gate:** Fail build if coverage drops below established baseline

#### Integration Tests
- **Scope:** Blueprint routes end-to-end, extension interactions (DB, auth), request/response cycle
- **Tool:** `pytest` + `pytest-flask` + Flask's built-in `app.test_client()`
- **Key fixture:** `conftest.py` `client` fixture using `create_app` (see Component Changes §7)
- **CI gate:** All integration tests must pass before merge to main branch

#### Regression Tests
- **Scope:** All existing test cases must pass unchanged (behavior parity with Flask 1.x)
- **Approach:** Run the full existing test suite against the upgraded application before removing any legacy code
- **Tool:** Existing `pytest` suite
- **CI gate:** Zero regression failures permitted before Phase 6 cutover

#### Performance Tests
- **Scope:** Baseline request throughput and latency for critical routes
- **Tool:** TODO — confirm if `locust`, `wrk`, or `ab` is available in the project
- **Baseline:** Capture performance metrics on Flask 1.x before migration; validate no >10% degradation on Flask 3.1
- **CI gate:** TODO — integrate performance gate if CI infrastructure supports it

### Additional Testing Notes
- Run `flask routes` after factory refactor to confirm all routes are registered correctly.
- Test `flask shell` context to confirm `current_app` is available and extensions are bound.
- Validate `TESTING = True` config suppresses error propagation as expected under Flask 3.1 behavior.

---

## Timeline

> **TODO:** The upgrade option did not provide a specific person-days estimate. All durations below are marked TODO and must be populated once the estimate is confirmed.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Dependency audit complete, compatibility matrix documented | Phase 1 | TODO | TODO |
| All dependencies upgraded, application boots on Flask 3.1 | Phase 2 | TODO | TODO |
| `create_app()` factory introduced, existing tests pass | Phase 3 | TODO | TODO |
| All Blueprints and extensions wired inside factory | Phase 4 | TODO | TODO |
| Test suite migrated to factory fixtures, coverage baseline met | Phase 5 | TODO | TODO |
| Legacy entry point removed, CI/CD updated, cutover complete | Phase 6 | TODO | TODO |

---

*Document status: DRAFT — pending confirmation of codebase file structure, current dependency versions, and person-days estimate from upgrade option.*