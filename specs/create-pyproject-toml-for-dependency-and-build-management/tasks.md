# TASKS: Create pyproject.toml for Dependency and Build Management

## Prerequisites

- [ ] [XS] Verify Python installation and confirm version compatibility (Python 3.8+ recommended for `pyproject.toml` PEP 517/518 support) in local development environment
- [ ] [XS] Confirm build backend choice (e.g., `setuptools>=61`, `hatchling`, or `flit_core`) is available via `pip` in the project environment
- [ ] [XS] Audit existing dependency definition files (e.g., `setup.py`, `setup.cfg`, `requirements.txt`, `requirements-dev.txt`, `Pipfile`) in the repository root to inventory all current dependencies before migration

---

## Phase 1 — Preparation

- [ ] [S] Inventory all runtime dependencies from existing `requirements.txt` (or `setup.py`/`setup.cfg` if present) and record pinned versions, version ranges, and any extras in a working notes file
- [ ] [S] Inventory all development/test dependencies from `requirements-dev.txt`, `requirements-test.txt`, or equivalent files in the repository root
- [ ] [XS] Create a feature branch (e.g., `feat/add-pyproject-toml`) from the default branch for all changes in this task
- [ ] [XS] Capture the current dependency install baseline by running `pip freeze > baseline-freeze.txt` in the project's virtual environment and committing it to the branch for regression reference

---

## Phase 2 — Core Upgrade

- [ ] [M] Create `pyproject.toml` in the repository root with the following sections populated from the inventoried dependencies:
  - `[build-system]` — specify `requires` and `build-backend` (e.g., `setuptools>=61` and `setuptools.build_meta`)
  - `[project]` — populate `name`, `version`, `description`, `requires-python`, `dependencies` (runtime deps from inventory)
  - `[project.optional-dependencies]` — add `dev` and/or `test` groups from dev/test dependency inventory
- [ ] [S] Migrate all runtime dependency entries from `requirements.txt` into the `[project] dependencies` list in `pyproject.toml`, preserving version constraints and extras
- [ ] [S] Migrate all development and test dependency entries into `[project.optional-dependencies]` groups (e.g., `dev`, `test`) in `pyproject.toml`
- [ ] [XS] Add `[tool.setuptools]` (or equivalent build backend config) section in `pyproject.toml` to specify package discovery (e.g., `packages = {find = {}}`) matching the existing project structure
- [ ] [XS] Remove or deprecate `setup.py`, `setup.cfg`, and/or `requirements*.txt` files from the repository root once all entries are confirmed migrated into `pyproject.toml` — do not delete until Phase 3 validation passes
- [ ] [XS] Verify `pyproject.toml` is valid by running `pip install --dry-run .` and `python -m build --no-isolation` (if `build` package is available) in the project root

---

## Phase 3 — Testing & Validation

- [ ] [S] Install the project from `pyproject.toml` in a clean virtual environment using `pip install -e ".[dev,test]"` and confirm all dependencies resolve without conflicts
- [ ] [XS] Diff `pip freeze` output from the clean install against `baseline-freeze.txt` captured in Phase 1 and document any version changes or missing packages
- [ ] [S] Run the existing test suite (using whatever test runner is currently configured, e.g., `pytest`) after installing from `pyproject.toml` and confirm all tests pass at the same baseline rate
- [ ] [XS] Confirm that no import errors or missing-package errors occur for the project's main entry points after installing solely from `pyproject.toml`

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml` — whichever is present in the repository) to replace `pip install -r requirements.txt` install steps with `pip install -e ".[dev,test]"` using `pyproject.toml`
- [ ] [XS] Confirm that any Docker build steps or `Dockerfile` `RUN pip install` commands in the repository are updated to install from `pyproject.toml` (e.g., `COPY pyproject.toml .` and `RUN pip install .`) if a `Dockerfile` is present

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `README.md` (or equivalent project documentation) to replace any install instructions referencing `requirements.txt` or `setup.py` with the new `pip install -e ".[dev,test]"` command
- [ ] [XS] Add a `CHANGELOG` entry (or equivalent) documenting the migration to `pyproject.toml` and listing removed files (e.g., `requirements.txt`, `setup.cfg`)
- [ ] [XS] Open a pull request from `feat/add-pyproject-toml` to the default branch, including the `baseline-freeze.txt` diff as evidence of dependency parity in the PR description