# Tasks: Upgrade Flask 1.x → 3.1 & Adopt Application Factory Pattern

> **Scope:** Flask upgrade from 1.x to 3.1 and refactor to application factory pattern.
> **Note:** Runtime, build tool, and extended dependency details were not provided in the tech analysis. Tasks below are scoped strictly to what is known. File names reflect common Flask project conventions — adjust to match actual project structure.

---

## Prerequisites

- [ ] [XS] Confirm Python version compatibility with Flask 3.1 (requires Python ≥ 3.8) in local and CI environments
- [ ] [XS] Confirm pip or pip-tools/Poetry is available and identify the exact requirements file (`requirements.txt`, `requirements.in`, or `pyproject.toml`) used to pin Flask
- [ ] [XS] Verify access to the target branch and confirm branch protection rules allow the upgrade PR workflow
- [ ] [XS] Confirm all existing tests can be located and executed locally before any changes are made (establish a green baseline)

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated feature branch (e.g., `upgrade/flask-3.1-factory`) from the main branch for all upgrade work
- [ ] [S] Audit direct and transitive dependencies for Flask 3.1 compatibility in `requirements.txt` (or equivalent), flagging extensions such as `Flask-Login`, `Flask-SQLAlchemy`, `Flask-WTF`, `Flask-Migrate`, and `Flask-CORS` that have known breaking changes between Flask 1.x and 3.x
- [ ] [S] Record the current test suite pass/fail baseline and code coverage percentage before any changes, saving output to `docs/migration/baseline-test-report.txt`
- [ ] [XS] Document all current `app = Flask(__name__)` instantiation sites and global `app` usages across the codebase to scope the factory refactor

---

## Phase 2 — Core Upgrade

- [ ] [S] Bump Flask from `1.x` to `3.1.*` in `requirements.txt` (or `pyproject.toml`) and run `pip install` to surface immediate dependency conflicts
- [ ] [M] Resolve dependency conflicts surfaced in the previous step — update compatible versions of Flask extensions (e.g., `Flask-SQLAlchemy>=3.0`, `Flask-Login>=0.6`, `Flask-WTF>=1.2`) in `requirements.txt`
- [ ] [M] Create `app/factory.py` (or `app/__init__.py`) implementing a `create_app(config_object=None)` application factory function, moving all `app = Flask(__name__)` initialization logic, config loading, and extension initialization into it
- [ ] [M] Migrate extension initialization from module-level `init` calls to the two-step pattern (`db = SQLAlchemy()` at module level; `db.init_app(app)` inside `create_app()`) for each extension in `app/extensions.py` (or equivalent)
- [ ] [S] Update `app/config.py` (or equivalent) to ensure config classes are compatible with `create_app()` accepting a config object or string, removing any direct `app.config.from_object()` calls that depend on a global `app`
- [ ] [M] Refactor all Blueprint registrations to occur inside `create_app()` in `app/factory.py`, removing any top-level `app.register_blueprint()` calls that reference a global `app` instance
- [ ] [S] Update the application entry point (`run.py`, `wsgi.py`, or `manage.py`) to call `create_app()` and assign the result, replacing any direct `from app import app` global imports
- [ ] [S] Replace all remaining usages of `flask.ext.*` imports (removed in Flask 1.0+, but confirm none remain) and update any `@app.before_first_request` decorators (removed in Flask 2.3) to use `with app.app_context():` blocks or `app.before_request` with a guard flag in `app/factory.py`
- [ ] [S] Update all `current_app`, `g`, and `request` context usages to confirm they operate within request or application context — fix any bare module-level accesses that relied on a global `app` in view or service modules
- [ ] [XS] Update `Werkzeug` import paths if used directly (Flask 3.x ships with Werkzeug 3.x; `werkzeug.utils`, `werkzeug.exceptions` paths may have changed) in any files that import from Werkzeug directly

---

## Phase 3 — Testing & Validation

- [ ] [M] Update `tests/conftest.py` to use the `create_app()` factory for the test `app` fixture, replacing any direct `from app import app` imports and ensuring `app.config["TESTING"] = True` is passed via the factory
- [ ] [S] Run the full test suite and compare pass/fail results against the baseline recorded in `docs/migration/baseline-test-report.txt`, resolving any regressions before proceeding
- [ ] [S] Manually verify application startup via `flask run` (or `python wsgi.py`) and exercise critical routes (auth, main views, API endpoints if present) to confirm no runtime context errors
- [ ] [XS] Confirm that `flask shell` launches correctly with the application context provided by the factory (test `current_app` is accessible in the shell)

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (`.github/workflows/*.yml`, `Jenkinsfile`, or equivalent) to install dependencies from the updated `requirements.txt` and confirm the test step invokes the correct test runner command
- [ ] [XS] Update any `Dockerfile` or container build file that pins `flask==1.*` or installs Flask directly, changing the pin to `flask==3.1.*` and rebuilding to verify the image starts correctly

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Add a `CHANGELOG.md` entry (or update the existing one) documenting the Flask 1.x → 3.1 upgrade, the application factory adoption, removed patterns (`before_first_request`, global `app`), and any extension version bumps
- [ ] [XS] Update `README.md` development setup instructions to reflect the new entry point (`create_app()`) and any changed `flask run` or environment variable requirements (e.g., `FLASK_APP=app.factory:create_app`)
- [ ] [S] Review and update any existing runbook or deployment guide that references the old `app.py` global `app` object or Flask 1.x-specific startup commands
- [ ] [XS] Open the upgrade PR against the main branch, request review, and confirm CI is green before merging