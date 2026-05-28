# Tasks: Upgrade Python Runtime from 3.8 to 3.13

> **Scope:** Python runtime upgrade from 3.8 → 3.13 only.
> **Note:** Tech analysis did not identify specific frameworks, build tools, or dependency files. Tasks below are grounded in standard Python project artifacts. Remove any task that does not apply to your repository.

---

## Prerequisites

- [ ] [XS] Confirm Python 3.13 is installable in all target environments (local, CI, production) and document the installation method (e.g., `pyenv`, system package manager, container base image) in a shared team note
- [ ] [XS] Verify `pyenv` (or equivalent version manager) is available on all developer machines and supports Python 3.13 (`pyenv install --list | grep 3.13`)
- [ ] [XS] Confirm repository access and that a feature branch can be opened against the main branch without requiring additional approvals to begin

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated feature branch `upgrade/python-3.8-to-3.13` from the current default branch
- [ ] [S] Capture the current full dependency resolution as a baseline by running `pip freeze > baseline_3.8_freeze.txt` in the existing 3.8 environment and committing the file to the branch for later comparison
- [ ] [XS] Record the current test suite pass/fail counts and coverage percentage from the 3.8 environment in a `MIGRATION_NOTES.md` file committed to the branch, to serve as the regression baseline
- [ ] [M] Run `pip install pip-audit` and audit all dependencies for known incompatibilities with Python 3.13; document findings in `MIGRATION_NOTES.md`
- [ ] [S] Identify all uses of removed or deprecated Python 3.8–3.12 APIs in the codebase by running `python -W error -m py_compile` on all `.py` files under Python 3.13 and logging output to `MIGRATION_NOTES.md`
- [ ] [S] Run `pylint --py-version=3.13` or `pyupgrade --py313-plus` across the codebase to surface syntax and API changes required; commit the report to `MIGRATION_NOTES.md`

---

## Phase 2 — Core Upgrade

- [ ] [XS] Update `.python-version` file (if present) from `3.8.x` to `3.13.x`
- [ ] [XS] Update the `python_requires` field in `setup.py` or `setup.cfg` (if present) from `>=3.8` to `>=3.13`
- [ ] [XS] Update the `requires-python` field in `pyproject.toml` (if present) from `>=3.8` to `>=3.13`
- [ ] [S] Re-resolve and update `requirements.txt` (or `requirements/*.txt` files if split by environment) under Python 3.13 using `pip-compile` or `pip install -r requirements.txt` and commit the refreshed lockfile
- [ ] [S] Re-resolve and update `Pipfile.lock` (if `Pipfile` is present) by running `pipenv install` under Python 3.13 and committing the updated lockfile
- [ ] [S] Re-resolve and update `poetry.lock` (if `pyproject.toml` uses Poetry) by running `poetry env use 3.13 && poetry update` and committing the updated lockfile
- [ ] [M] Replace all usages of `typing` module backports that are now built-in in 3.13 (e.g., `typing.Union` → `X | Y`, `typing.Optional` → `X | None`, `typing.List` → `list`) across all `.py` source files using `pyupgrade --py313-plus`
- [ ] [S] Remove any `__future__` annotations imports (`from __future__ import annotations`) that are no longer needed under 3.13 and verify no runtime behaviour changes result
- [ ] [S] Replace any usage of `distutils` (removed in 3.12) with `setuptools` equivalents in all affected `.py` files and `setup.py`
- [ ] [S] Replace any usage of `asyncio.coroutine` decorator and `yield from` coroutine syntax (removed in 3.11) in all affected `.py` files with `async def` / `await`
- [ ] [S] Address any `SyntaxWarning` or `DeprecationWarning` emissions surfaced during Phase 1 audit, updating the relevant `.py` files

---

## Phase 3 — Testing & Validation

- [ ] [S] Install the full dependency set under Python 3.13 in a clean virtual environment and confirm `pip install` completes without errors
- [ ] [M] Execute the full existing test suite under Python 3.13 and record pass/fail counts and coverage percentage in `MIGRATION_NOTES.md`; diff against the 3.8 baseline captured in Phase 1
- [ ] [S] Investigate and fix any test failures introduced by the runtime upgrade, updating affected test files and source files as needed
- [ ] [XS] Confirm coverage percentage under Python 3.13 meets or exceeds the 3.8 baseline recorded in `MIGRATION_NOTES.md`
- [ ] [XS] Run `pip-audit` again under Python 3.13 resolved dependencies and confirm no new vulnerabilities were introduced by dependency version changes

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g., `.github/workflows/*.yml`, `.gitlab-ci.yml`, `Jenkinsfile`, or `azure-pipelines.yml` — whichever is present) to replace all `python-version: "3.8"` references with `python-version: "3.13"`
- [ ] [XS] Update any CI matrix strategy blocks that pin `3.8` to use `3.13` as the minimum version, removing the `3.8` matrix entry
- [ ] [S] Update the `Dockerfile` (if present) base image from `python:3.8-*` to `python:3.13-slim` (or equivalent tag) and rebuild to confirm the image builds successfully
- [ ] [XS] Update any `docker-compose.yml` or `docker-compose.override.yml` files (if present) that reference a `python:3.8` image tag to `python:3.13`
- [ ] [XS] Update any `runtime.txt` file (if present, e.g., for Heroku or Render deployments) from `python-3.8.x` to `python-3.13.x`
- [ ] [XS] Update any `.tool-versions` file (if present, for `asdf`) from `python 3.8.x` to `python 3.13.x`

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry documenting the Python runtime upgrade from 3.8 to 3.13, listing any removed API replacements and dependency version changes made
- [ ] [XS] Update `README.md` (or equivalent) prerequisite/setup section to replace all references to Python 3.8 with Python 3.13, including any `pyenv` or virtual environment setup instructions
- [ ] [XS] Update `MIGRATION_NOTES.md` with a final summary of all changes made, issues encountered, and the confirmed test baseline comparison result
- [ ] [S] Open the pull request for `upgrade/python-3.8-to-3.13`, ensure all CI checks pass on Python 3.13, and request review before merging
- [ ] [XS] After merge, monitor the first post-merge CI run and any staging deployment for runtime errors or import failures and confirm clean execution