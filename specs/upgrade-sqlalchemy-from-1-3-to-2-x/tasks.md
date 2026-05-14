## Prerequisites

- [ ] [XS] Verify developer access to source repository and permissions for PR creation
- [ ] [XS] Ensure Python is installed on all developer systems (recommend Python ≥3.8 for SQLAlchemy 2.x)
- [ ] [XS] Confirm presence of pip and virtualenv (pip ≥20.0 recommended)
- [ ] [XS] Ensure up-to-date local development environment with existing dependencies installed (`pip install -r requirements.txt`)
- [ ] [XS] Identify existing SQLAlchemy references in requirements.txt or setup.py

## Phase 1 — Preparation

- [ ] [XS] Audit SQLAlchemy version in requirements.txt or setup.py
- [ ] [XS] Create upgrade feature branch `sqlalchemy-2-upgrade` from main
- [ ] [XS] Capture baseline test results by running all existing tests, and export output to `ci/baseline_sqlalchemy13.txt` (if test suite exists)
- [ ] [XS] Review presence and status of automated CI gates (e.g., GitHub Actions workflows, `ci/` directory configs)

## Phase 2 — Core Upgrade

- [ ] [XS] Upgrade SQLAlchemy to latest 2.x in requirements.txt or setup.py
- [ ] [M] Refactor database engine and session setup for SQLAlchemy 2.x in all relevant modules and scripts (e.g., imports, engine/session construction APIs)
- [ ] [L] Migrate all ORM query syntax (e.g., `session.query(Model)` to SQLAlchemy 2.0 Core/ORM style) in every file directly importing sqlalchemy.* or using session/query objects
- [ ] [M] Update legacy API calls (e.g., `execute()` usage, removed positional parameters) in all models and DAO modules
- [ ] [S] Remove/replace deprecated constructs and flags according to SQLAlchemy 2.x migration notes in all migration/seed scripts
- [ ] [S] Search for and resolve usage of `Query.from_self()` and `Query.with_entities()` patterns per 2.x changes

## Phase 3 — Testing & Validation

- [ ] [XS] Re-run all test suites under SQLAlchemy 2.x, export results to `ci/baseline_sqlalchemy2.txt`
- [ ] [S] Compare new test output with baseline for regressions, annotate failures with SQLAlchemy-related breaking changes
- [ ] [M] Add/expand test cases covering ORM queries previously using legacy patterns (if not adequately tested)
- [ ] [XS] Review and confirm successful migration by running a database smoke test against a staging or local database

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update CI pipeline config (e.g., `.github/workflows/ci.yml`) to ensure Python dependency resolver installs updated SQLAlchemy 2.x
- [ ] [XS] Bump base image or dependency hash in Dockerfile, if pinning SQLAlchemy or requirements.txt
- [ ] [XS] Verify infrastructure-as-code (IaC) and deployment scripts do not explicitly install or pin to SQLAlchemy <2.x

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update CHANGELOG.md to log the upgrade from SQLAlchemy 1.3 to 2.x and summarize migration steps and impacts
- [ ] [XS] Review and update README.md and any docs referencing SQLAlchemy usage or features if syntax/APIs changed
- [ ] [XS] Revise runbook to include SQLAlchemy 2.x troubleshooting notes for operators
- [ ] [XS] Draft and execute a rollout plan for releasing SQLAlchemy 2.x changes to staging then production
- [ ] [XS] Configure post-upgrade monitoring for database error logs and application tracebacks related to ORM/db access

---

**Note:** If any section above is not relevant to the SQLAlchemy upgrade, mark as N/A.

Sections not applicable:  
N/A — All sections above apply directly to the SQLAlchemy upgrade task.