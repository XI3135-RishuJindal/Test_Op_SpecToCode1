# Tasks: Migrate Dependency Management from `requirements.txt` to `pyproject.toml`

> **Scope:** Replace `requirements.txt`-based dependency management with a `pyproject.toml` configuration using a modern Python build backend. No framework upgrades or runtime changes are included in this migration.

---

## Prerequisites

- [ ] [XS] Confirm Python version in use by inspecting the runtime environment (check `.python-version`, `runtime.txt`, or `python --version`) and record it for the `requires-python` field in `pyproject.toml`
- [ ] [XS] Confirm which build backend to adopt (`hatchling`, `setuptools`, or `flit_core`) by reviewing existing `setup.py` or `setup.cfg` if present — default to `hatchling` if no prior build tooling exists
- [ ] [XS] Verify `pip >= 21.3` and `build >= 0.10` are available in the local and CI environments, as both are required for `pyproject.toml`-only workflows
- [ ] [XS] Ensure write access to the repository and that a feature branch can be opened against the main branch

---

## Phase 1 — Preparation

- [ ] [S] Audit `requirements.txt` (and `requirements-dev.txt`, `requirements-test.txt`, or any other variant files) to produce a complete, categorised list of runtime vs. development/test dependencies with their pinned versions
- [ ] [XS] Create a feature branch named `migrate/pyproject-toml` from the current default branch
- [ ] [XS] Capture the current installed dependency tree by running `pip freeze > freeze-baseline.txt` and committing it to the branch for regression comparison
- [ ] [XS] Record the current test suite pass/fail baseline (test count, coverage percentage) in a `MIGRATION_NOTES.md` file committed to the branch

---

## Phase 2 — Core Upgrade

- [ ] [S] Create `pyproject.toml` at the repository root with `[build-system]`, `[project]`, and `[project.optional-dependencies]` tables, populating `dependencies` from the runtime section of `requirements.txt` and `optional-dependencies.dev` / `optional-dependencies.test` from the development/test sections
- [ ] [XS] Set `requires-python` in `[project]` to the version confirmed in Prerequisites, e.g. `requires-python = ">=3.x"`
- [ ] [XS] Migrate any `pip install` tool configuration (e.g. index URLs, trusted hosts) from `requirements.txt` header comments or `pip.conf` into a `[tool.pip]` section or a `pip.conf` note in `pyproject.toml` comments, as appropriate
- [ ] [XS] Add a `[tool.setuptools]` or equivalent backend configuration section in `pyproject.toml` if `setup.py` or `setup.cfg` exists, then delete `setup.py` / `setup.cfg` to consolidate into `pyproject.toml`
- [ ] [XS] Delete `requirements.txt` (and all variant files) from the repository root after confirming all dependencies are represented in `pyproject.toml`
- [ ] [XS] Update `.gitignore` to remove any `requirements*.txt` ignore rules that are no longer needed and add `dist/` and `*.egg-info/` if not already present

---

## Phase 3 — Testing & Validation

- [ ] [S] Create a clean virtual environment, install the project via `pip install -e ".[dev,test]"` using only `pyproject.toml`, and verify the resolved dependency tree against `freeze-baseline.txt` for unexpected additions or removals
- [ ] [XS] Run the full test suite in the clean environment and confirm the pass/fail count and coverage percentage match the baseline recorded in `MIGRATION_NOTES.md`
- [ ] [XS] Verify that `python -m build` produces a valid sdist and wheel from `pyproject.toml` without errors

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update all CI pipeline job steps that reference `pip install -r requirements.txt` (or variant files) to use `pip install -e ".[dev,test]"` sourced from `pyproject.toml` — update every affected job definition file (e.g. `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `tox.ini`, `Makefile`)
- [ ] [XS] Update any `Dockerfile` or `docker-compose.yml` that copies and installs `requirements.txt` to instead copy `pyproject.toml` (and `src/` layout if applicable) and run `pip install .`
- [ ] [XS] Update `tox.ini` or `noxfile.py` (if present) to remove `deps = -r requirements.txt` lines and replace with `extras = dev,test` or equivalent `pyproject.toml`-native dependency groups

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `README.md` installation instructions to replace `pip install -r requirements.txt` commands with `pip install -e ".[dev,test]"` and document the new `pyproject.toml` structure
- [ ] [XS] Add an entry to `CHANGELOG.md` (or equivalent) describing the migration from `requirements.txt` to `pyproject.toml` under an appropriate release heading
- [ ] [XS] Open the pull request for `migrate/pyproject-toml`, request review, and confirm CI passes end-to-end before merging
- [ ] [XS] After merge, delete the `freeze-baseline.txt` file in a follow-up commit or include its removal in the PR if it was only needed for validation