## Prerequisites

- [ ] [XS] Install Flask 2.x in development environment
- [ ] [XS] Install SQLAlchemy 1.4.x in development environment
- [ ] [XS] Ensure pip ≥ 21.0 and virtualenv ≥ 20.0 are available in local tooling
- [ ] [XS] Obtain access to existing code repository with write permission

## Phase 1 — Preparation

- [ ] [XS] Create modernization branch `feat/flask-sqlalchemy-refactor` from latest main
- [ ] [S] Audit current dependencies in requirements.txt and identify non-compatible packages
- [ ] [XS] Run current test suite and capture baseline results in `tests/baseline_results.log`

## Phase 2 — Core Upgrade

- [ ] [M] Refactor application routing logic to use `@app.route` decorators in main Flask application file (e.g., `app.py`)
- [ ] [M] Refactor request handlers to Flask view functions or Blueprints in main Flask application file
- [ ] [M] Initialize Flask application object (`Flask(__name__)`) in main application module (`app.py`)
- [ ] [L] Refactor ORM model classes to inherit from `sqlalchemy.orm.declarative_base` in models module (e.g., `models.py`)
- [ ] [M] Update database session management to use `sqlalchemy.orm.sessionmaker` in database module (e.g., `db.py`)
- [ ] [S] Remove or replace incompatible legacy framework code in main application module (`app.py` and/or corresponding files)
- [ ] [S] Update dependency definitions to require Flask 2.x and SQLAlchemy 1.4.x in requirements.txt

## Phase 3 — Testing & Validation

- [ ] [S] Update and run unit tests to use Flask test client in tests/test_app.py
- [ ] [S] Add tests for all ORM-backed endpoints using SQLAlchemy session in tests/test_app.py
- [ ] [XS] Compare updated test suite results with `tests/baseline_results.log`
- [ ] [S] Verify end-to-end database transactions for major workflows using SQLAlchemy engine in tests/test_db.py

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update installation and setup instructions for Flask/SQLAlchemy in README.md
- [ ] [S] Document major API or usage changes in CHANGELOG.md
- [ ] [S] Draft summary of manual test/validation steps and edge cases in RUNBOOK.md