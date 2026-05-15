# Tasks: Upgrade Flask from 1.x to 3.x

## Prerequisites

- [ ] [XS] Verify and record current Flask version in requirements.txt
- [ ] [XS] Ensure Python virtual environment is available and activated
- [ ] [XS] Ensure access to repository with permissions to create branches and PRs
- [ ] [XS] Install pip version 23.0 or newer locally
- [ ] [XS] Ensure connectivity to PyPI for dependency installation

## Phase 1 — Preparation

- [ ] [S] Audit all Flask dependencies in requirements.txt for compatibility with Flask 3.x
- [ ] [XS] Create `upgrade/flask-3.x` branch from current main branch
- [ ] [XS] Run existing test suite to capture current passing/failing baseline in CI logs
- [ ] [XS] Export and archive current requirements.txt as requirements.pre-flask3.txt

## Phase 2 — Core Upgrade

- [ ] [XS] Upgrade Flask to latest 3.x in requirements.txt
- [ ] [M] Refactor all usage of deprecated Flask APIs removed in 2.x and 3.x in app/ and views/ modules
- [ ] [S] Update all import statements referencing moved modules (e.g., `flask.ext.*`) in app/ and views/
- [ ] [S] Resolve incompatible usages of Flask extension APIs deprecated or removed in tests/ and blueprints/ modules

## Phase 3 — Testing & Validation

- [ ] [S] Rebuild environment and install updated dependencies using `pip install -r requirements.txt`
- [ ] [S] Run full test suite and record results in CI logs for post-upgrade comparison
- [ ] [XS] Verify all endpoints in app/ and views/ return expected HTTP status codes
- [ ] [S] Compare regression baseline (pre-upgrade) with post-upgrade test results

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update CI pipeline (e.g., .github/workflows/ci.yml) Python matrix to include and prefer Flask 3.x
- [ ] [XS] Validate Dockerfile uses pip to install updated requirements.txt

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add Flask 3.x upgrade notes to CHANGELOG.md
- [ ] [XS] Update requirements.txt comment header to indicate minimum Flask version 3.x
- [ ] [S] Review and update runbook to reference Flask 3.x for support and troubleshooting
- [ ] [XS] Monitor logs for 48 hours post rollout for Flask-specific runtime errors

---

*Sections not directly relevant to Flask upgrade have been marked as N/A where appropriate.*