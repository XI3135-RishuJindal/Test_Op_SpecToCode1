## Prerequisites

- [ ] [XS] Confirm access to application source code repository (read/write permissions)
- [ ] [XS] Install Python 3.10.x (verify with `python --version`)
- [ ] [XS] Install Flask 3.x (verify with `pip freeze | grep Flask==3`)
- [ ] [XS] Install SQLAlchemy 2.x (verify with `pip freeze | grep SQLAlchemy==2`)
- [ ] [XS] Verify presence of requirements.txt or pyproject.toml for dependency tracking

## Phase 1 — Preparation

- [ ] [S] Create `upgrade/flask3-sqlalchemy2/` working branch from latest main
- [ ] [S] Audit requirements.txt and/or pyproject.toml for Flask and SQLAlchemy versions
- [ ] [XS] Capture current `pytest`/unit test run baseline output to `upgrade/flask3-sqlalchemy2/test-baseline.log`
- [ ] [S] Ensure GitHub Actions (or other CI) jobs execute pytest/unit tests on PRs to the working branch

## Phase 2 — Core Upgrade

- [ ] [XS] Upgrade Flask version to 3.x in requirements.txt or pyproject.toml
- [ ] [XS] Upgrade SQLAlchemy version to 2.x in requirements.txt or pyproject.toml
- [ ] [M] Refactor all imports of `flask.ext.sqlalchemy` to `flask_sqlalchemy` in `app/__init__.py` and model modules
- [ ] [L] Refactor all usage of legacy `db.session.query(Model)` to new SQLAlchemy 2.x style in `app/models.py`, `app/routes.py`
- [ ] [M] Update all uses of Flask deprecated methods (e.g., `app.json_encoder`, `request.json`) in `app/__init__.py`, `app/routes.py`
- [ ] [M] Update model declarations and relationships for SQLAlchemy 2.x breaking changes in `app/models.py`
- [ ] [S] Refactor custom CLI commands using deprecated Flask-Script patterns in `manage.py`
- [ ] [XS] Remove deprecated usage of `db.Model.query.get()` in `app/models.py`
- [ ] [XS] Migrate any usage of removed `flask.Request.json` to `request.get_json()` in `app/routes.py`
- [ ] [S] Update all `session.commit()` error handling to conform to SQLAlchemy 2.x patterns in `app/services.py`

## Phase 3 — Testing & Validation

- [ ] [XS] Run all unit and integration tests using `pytest` and collect results in `upgrade/flask3-sqlalchemy2/`
- [ ] [S] Manually verify CRUD API endpoints for major data models using HTTP requests
- [ ] [XS] Compare test output with baseline for regression detection
- [ ] [S] Ensure new/changed code paths are covered by the test suite (>=90% coverage)
- [ ] [XS] Document and raise issues for any failing or unstable tests in the branch

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add Flask 3.x and SQLAlchemy 2.x upgrade notes to `CHANGELOG.md`
- [ ] [XS] Update `README.md` to reflect new minimum dependency versions
- [ ] [S] Review and update application runbook/recovery steps for any changed CLI/DB workflows
- [ ] [XS] Tag PRs for staged deployment in accordance with project release practices
- [ ] [XS] Set up basic post-upgrade monitoring for 500 errors in logs for one week post-release