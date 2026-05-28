# TASKS: Migrate Dependency Management from `requirements.txt` to `pyproject.toml`

> **Scope:** Replace `requirements.txt`-based dependency management with a `pyproject.toml` configuration. No runtime, framework, or dependency version upgrades are in scope unless required to complete the migration itself.

---

## Prerequisites

- [ ] [XS] Confirm Python version in use by inspecting the runtime environment (`.python-version`, `runtime.txt`, CI config, or `python --version`) and record it for the `requires-python` field in `pyproject.toml`
- [ ] [XS] Confirm which build backend will be used (`hatchling`, `setuptools`, `flit-core`, or `poetry-core`) and ensure it is installable in the local and CI environments
- [ ] [XS] Verify that `pip >= 21.3` (PEP 660 / `pyproject.toml` install support) is available in all target environments by running `pip --version`
- [ ] [XS] Ensure write access to the repository and the ability to open a pull request against the main branch

---

## Phase 1 — Preparation

- [ ] [S] Audit `requirements.txt` (and any companion files such as `requirements-dev.txt`, `requirements-test.txt`, `requirements-prod.txt`) to produce a complete, categorised inventory of all direct dependencies, pinned versions, and extras
- [ ] [XS] Create a dedicated migration branch (e.g., `chore/migrate-to-pyproject-toml`) from the current default branch
- [ ] [XS] Capture the current installed-package baseline by running `pip freeze > baseline-freeze.txt` in the existing environment and committing it to the branch for later comparison
- [ ] [XS] Record the current test-suite pass/fail state on the migration branch before any file changes, to establish a clean regression baseline

---

## Phase 2 — Core Upgrade

- [ ] [M] Create `pyproject.toml` at the repository root, populating `[project]` metadata (`name`, `version`, `description`, `requires-python`) and a `[build-system]` table matching the chosen build backend
- [ ] [M] Migrate all production dependencies from `requirements.txt` into the `[project] dependencies` list in `pyproject.toml`, preserving existing version constraints and extras
- [ ] [S] Migrate all development/test-only dependencies (from `requirements-dev.txt`, `requirements-test.txt`, or equivalent) into an appropriate `[project.optional-dependencies]` table (e.g., `[project.optional-dependencies] dev = [...]` and `test = [...]`) in `pyproject.toml`
- [ ] [S] Migrate any tool configuration already present in `setup.cfg`, `tox.ini`, or `pytest.ini` (e.g., `[tool.pytest.ini_options]`, `[tool.coverage.run]`) into `pyproject.toml` under the relevant `[tool.*]` sections
- [ ] [XS] Delete `requirements.txt` and any migrated companion requirements files from the repository, adding a tombstone comment in the git commit message referencing the new `pyproject.toml` location
- [ ] [XS] Verify the package installs cleanly in a fresh virtual environment by running `pip install -e ".[dev,test]"` (or equivalent extras) against the new `pyproject.toml`
- [ ] [XS] Run `pip freeze > post-migration-freeze.txt` in the new environment and diff against `baseline-freeze.txt` to confirm no unintended dependency additions or removals

---

## Phase 3 — Testing & Validation

- [ ] [S] Run the full existing test suite against the environment installed from `pyproject.toml` and confirm all tests that passed on the baseline continue to pass
- [ ] [XS] Confirm that optional-dependency groups install correctly in isolation (e.g., `pip install -e ".[test]"` only, then run tests) to validate group separation
- [ ] [XS] Verify that a clean install without optional extras (`pip install .`) succeeds and does not pull in dev/test packages

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [M] Update the CI pipeline configuration (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, or equivalent) to replace any `pip install -r requirements.txt` steps with `pip install -e ".[dev,test]"` (or the appropriate extras) referencing `pyproject.toml`
- [ ] [XS] Update any `Dockerfile` or container build scripts that reference `requirements.txt` to instead copy `pyproject.toml` and run `pip install` against it
- [ ] [XS] Update any `Makefile`, `tox.ini`, or local developer setup scripts (e.g., `scripts/bootstrap.sh`) that reference `requirements.txt` to use the new `pyproject.toml`-based install command

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `README.md` (or equivalent developer setup documentation) to replace all `pip install -r requirements.txt` instructions with the `pyproject.toml`-based equivalents and document the available optional-dependency groups
- [ ] [XS] Add an entry to `CHANGELOG.md` (or equivalent) describing the migration, the removed files, and the new install instructions
- [ ] [XS] Open the pull request, request review, and confirm CI passes end-to-end on the branch before merging
- [ ] [XS] After merge, verify that the first post-merge CI run on the default branch installs and tests successfully using `pyproject.toml`