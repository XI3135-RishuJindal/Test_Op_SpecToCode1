## Prerequisites
- [ ] [XS] Obtain access to the code repository with sufficient permissions for branch and PR creation
- [ ] [XS] Confirm presence of Flask and SQLAlchemy in requirements.txt or Pipfile
- [ ] [XS] Ensure Python >= 3.8 is available in the development environment
- [ ] [XS] Install Flask (exact version as currently used, or latest compatible version)
- [ ] [XS] Install SQLAlchemy (exact version as currently used, or latest compatible version)
- [ ] [XS] Set up local virtual environment using `venv` or `virtualenv`

## Phase 1 — Preparation
- [ ] [XS] Create `refactor/flask-sqlalchemy-api-compat` feature branch from the latest main branch
- [ ] [S] Audit usage of Flask and SQLAlchemy APIs in all `*.py` modules under `app/`
- [ ] [S] Capture current test baseline by running `pytest` in the root directory (if tests are available)
- [ ] [XS] Add/confirm codeowners for review in `.github/CODEOWNERS` (if applicable)

## Phase 2 — Core Upgrade
- [ ] [M] Refactor all API routes to use current Flask API (update deprecated `@app.route` patterns and import statements) in `app/routes.py`
- [ ] [M] Update SQLAlchemy session and model definitions to align with current SQLAlchemy API in `app/models.py`
- [ ] [S] Replace deprecated Flask-RESTful resource usage with recommended Flask view patterns in `app/api.py`
- [ ] [S] Refactor any custom request/response parsing code to use Flask's updated `request` and `jsonify` APIs in `app/utils.py`

## Phase 3 — Testing & Validation
- [ ] [S] Run full test suite using `pytest` and compare results to captured pre-refactor baseline
- [ ] [S] Add or update tests in `tests/test_routes.py` to cover updated API endpoints
- [ ] [XS] Verify test coverage remains at or above pre-refactor levels using `pytest --cov`
- [ ] [XS] Validate API compatibility with sample client requests via `curl` or Postman collection

## Phase 4 — CI/CD & Infrastructure
N/A — not applicable to this task

## Phase 5 — Documentation & Rollout
- [ ] [XS] Update API usage examples in `README.md` to reflect any breaking changes
- [ ] [XS] Document refactoring details and migration steps in `docs/upgrade-flask-sqlalchemy.md`
- [ ] [XS] Add summary of changes to `CHANGELOG.md`
- [ ] [XS] Notify relevant teams of API updates via project Slack or Teams channel