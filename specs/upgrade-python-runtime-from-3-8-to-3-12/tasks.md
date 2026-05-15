# TASKS: Python 3.8 → 3.12 Runtime Upgrade

## Prerequisites

- [ ] [S] Ensure Python 3.12.x is installed and available on all developer and CI systems
- [ ] [XS] Verify write access to requirements.txt, setup.py, and Dockerfile (if present)

## Phase 1 — Preparation

- [ ] [XS] Create `feature/python312-upgrade` branch from latest `main`
- [ ] [XS] Capture current test baseline using Python 3.8 environment via `pytest` (or other configured test runner)
- [ ] [XS] Pin current Python version (`python==3.8.*`) in requirements.txt or runtime.txt if present, to serve as downgrade reference

## Phase 2 — Core Upgrade

- [ ] [S] Update local Python version reference from 3.8 to 3.12 in `.python-version` (if exists)
- [ ] [S] Change Python runtime version to 3.12 in `runtime.txt` (Heroku or similar, if exists)
- [ ] [S] Update `Dockerfile` base image from `python:3.8` to `python:3.12` if Dockerfile exists
- [ ] [S] Modify CI configuration (`.github/workflows/*` or `.gitlab-ci.yml`) to use Python 3.12 runner
- [ ] [S] Update setup.py or pyproject.toml to set `python_requires='>=3.12'` (if present)

## Phase 3 — Testing & Validation

- [ ] [S] Reinstall all dependencies in a clean Python 3.12 virtual environment
- [ ] [M] Run all existing tests with Python 3.12 and record results
- [ ] [S] Compare Python 3.12 test results against captured 3.8 baseline, noting regressions if any
- [ ] [XS] Review deprecation warnings and update code only if new runtime errors appear (else, defer changes)

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update any deployment IaC files (e.g., `.ebextensions/*`, `app.yaml`) specifying Python 3.8 → 3.12 (if present)
- [ ] [XS] Verify build and release pipeline success under Python 3.12 in CI

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add upgrade notes to `CHANGELOG.md` specifying runtime change to Python 3.12
- [ ] [XS] Review and update `README.md` and `CONTRIBUTING.md` setup instructions for Python 3.12
- [ ] [S] Monitor application logs for runtime-specific errors in staging for at least 24 hours post-deploy

---

Sections for frameworks, libraries, application code, and other components are  
N/A — not applicable to this task.