# Tasks: Upgrade Flask 1.x → 3.1 & Adopt Application Factory Pattern

> **Scope:** Flask upgrade from 1.x to 3.1 and refactor to application factory pattern.
> **Option:** Moderate — incremental migration with factory pattern adoption.
> **Note:** Runtime, build tool, and broader dependency details were not provided in the tech analysis. Tasks below are scoped strictly to what is known.

---

## Prerequisites

- [ ] [XS] Confirm Python version compatibility with Flask 3.1 (requires Python ≥ 3.8; verify active interpreter in local and CI environments)
- [ ] [XS] Confirm pip or pip-tools/Poetry/pipenv is available and identify the requirements file (`requirements.txt`, `pyproject.toml`, or `Pipfile`) used to pin Flask
- [ ] [XS] Verify access to the application's source repository and confirm a working branch can be created from `main`/`master`
- [ ] [XS] Confirm test runner (pytest or unittest) is installed and all existing tests pass on the current Flask 1.x baseline before any changes begin

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch (e.g., `upgrade/flask-3.1-factory`) from `main` in the repository
- [ ] [S] Audit direct and transitive dependencies in the requirements file for Flask 1.x-specific pins (e.g., `Werkzeug<2`, `Jinja2<3`, `itsdangerous<2`, `click<8`) and document each conflict
- [ ] [S] Run the existing test suite and capture a baseline report (pass/fail counts, coverage percentage) to use as a regression reference in Phase 3
- [ ] [XS] Search the codebase for all usages of `flask.ext.*` imports (removed in Flask 1.0+) and `flask.json.provider` patterns that changed in Flask 2.2+ to produce a migration hit-list
- [ ] [XS] Search the codebase for direct instantiation of `Flask(__name__)` at module level (outside any function) to identify all files requiring factory refactor
- [ ] [XS] Identify all files that import the module-level `app` object directly (e.g., `from app import app`) to scope the factory pattern ripple effect

---

## Phase 2 — Core Upgrade

> Tasks are ordered by dependency chain: pin dependencies first, then upgrade Flask, then migrate application code.

- [ ] [S] Update Flask pin to `Flask==3.1.*` in the requirements file and update companion pins: `Werkzeug>=3.0`, `Jinja2>=3.1`, `itsdangerous>=2.1`, `click>=8.1`
- [ ] [S] Resolve any remaining transitive dependency conflicts surfaced by `pip install` or the lock-file resolver after updating the Flask pin (do not proceed to code changes until `pip install` succeeds cleanly)
- [ ] [M] Create `app/factory.py` (or `src/<package>/factory.py`) containing a `create_app(config=None)` function that instantiates `Flask(__name__)`, loads configuration, and registers all extensions
- [ ] [M] Move all extension initializations (e.g., `db.init_app(app)`, `login_manager.init_app(app)`, `mail.init_app(app)`) from module-level code into `create_app()` in `app/factory.py`
- [ ] [M] Register all Blueprints inside `create_app()` in `app/factory.py`, removing any module-level `app.register_blueprint()` calls from individual route files
- [ ] [S] Update the application entry point (e.g., `run.py`, `wsgi.py`, or `manage.py`) to call `create_app()` instead of importing a module-level `app` instance
- [ ] [S] Update all files that imported the module-level `app` object (identified in Phase 1) to either receive `app` via `create_app()` or use Flask's `current_app` proxy where appropriate
- [ ] [S] Replace any uses of `app.before_first_request` decorator (removed in Flask 2.3) with equivalent logic inside `create_app()` or a `with app.app_context():` block in `app/factory.py`
- [ ] [XS] Replace any uses of `flask.escape()` (removed in Flask 2.0; moved to `markupsafe.escape`) throughout the codebase
- [ ] [XS] Update any `@app.errorhandler` registrations that live outside Blueprints to be registered inside `create_app()` in `app/factory.py`
- [ ] [S] Update Flask test client usage in the test suite to instantiate the app via `create_app()` and use `app.test_client()` within a proper app context (update `conftest.py` or equivalent test fixtures)

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full test suite against Flask 3.1 and compare pass/fail counts and coverage percentage to the Phase 1 baseline; document any new failures
- [ ] [S] Fix any test failures caused by the factory pattern refactor (e.g., `RuntimeError: Working outside of application context`) in `conftest.py` or individual test files
- [ ] [XS] Manually verify the application starts without error by running `flask run` (or the equivalent entry point) with `create_app()` as the app factory, confirming Flask's `--app` CLI flag resolves correctly
- [ ] [XS] Verify Flask CLI commands (e.g., `flask shell`, any custom `@app.cli.command()` entries) work correctly with the factory-based app in the updated entry point
- [ ] [XS] Confirm no `DeprecationWarning` or `RemovedInFlask30Warning` messages appear in test output or server startup logs

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, or `.gitlab-ci.yml`) to install dependencies from the updated requirements file and confirm the pipeline passes on the feature branch
- [ ] [XS] Update any `FLASK_APP` environment variable references in CI config, Docker files, or `.env.example` to point to the factory function (e.g., `FLASK_APP=app.factory:create_app`)
- [ ] [XS] If a `Dockerfile` exists, verify the `CMD` or `ENTRYPOINT` that invokes Flask or a WSGI server (e.g., gunicorn) references the factory correctly (e.g., `gunicorn "app.factory:create_app()"`)

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add an entry to `CHANGELOG.md` documenting the Flask 1.x → 3.1 upgrade and the adoption of the application factory pattern, including the new `FLASK_APP` value
- [ ] [XS] Update `README.md` (or equivalent developer setup guide) to replace any module-level `FLASK_APP=app.py` instructions with the factory-based invocation (e.g., `FLASK_APP=app.factory:create_app`)
- [ ] [XS] Open a pull request from `upgrade/flask-3.1-factory` to `main`, request review, and confirm CI is green before merging
- [ ] [XS] After merge, monitor application logs and error tracking (if configured) for any runtime errors related to app context or missing configuration that did not surface in tests