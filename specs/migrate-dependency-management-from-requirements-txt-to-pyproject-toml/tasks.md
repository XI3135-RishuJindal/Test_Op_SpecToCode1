# Tasks: Migrate Dependency Management from `requirements.txt` to `pyproject.toml`

> **Scope:** Replace `requirements.txt`-based dependency management with a `pyproject.toml` configuration. No runtime, framework, or dependency version upgrades are in scope unless required to complete the migration itself.

---

## Prerequisites

- [ ] [XS] Confirm Python version in use by inspecting the runtime environment (`.python-version`, `runtime.txt`, CI config, or `python --version`) and record it for the `requires-python` field in `pyproject.toml`
- [ ] [XS] Confirm which build backend will be used (`hatchling`, `setuptools`, `flit-core`, or `poetry-core`) and ensure it is available in the local development environment
- [ ] [XS] Verify that `pip >= 21.3` (PEP 660 support) or `pip >= 23.0` (recommended) is available in all environments that will install the project, as older `pip` versions cannot process `pyproject.toml`-only projects
- [ ] [XS] Ensure all contributors and CI runners have access to the repository branch and can install from `pyproject.toml` before the migration branch is merged

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated migration branch (e.g., `chore/migrate-to-pyproject-toml`) from the main branch
- [ ] [S] Audit `requirements.txt` (and any companion files such as `requirements-dev.txt`, `requirements-test.txt`, `requirements-prod.txt`) to produce a complete, categorised inventory of all direct dependencies, their pinned or constrained versions, and which environment group they belong to (runtime, dev, test, docs)
- [ ] [XS] Capture the current resolved dependency lockset by running `pip freeze > freeze-before.txt` in a clean virtual environment built from the existing `requirements.txt` files — commit this file to the branch as a migration baseline
- [ ] [XS] Record the full list of transitive dependencies from `freeze-before.txt` so post-migration resolution can be diffed against it
- [ ] [XS] Identify and note any editable installs (`-e ./path`), VCS references (`git+https://...`), or private index entries (`--index-url`, `--extra-index-url`) in `requirements.txt` that require special handling in `pyproject.toml`

---

## Phase 2 — Core Upgrade

- [ ] [S] Create `pyproject.toml` at the repository root with the `[build-system]` table specifying the chosen build backend and its `requires` list
- [ ] [M] Populate the `[project]` table in `pyproject.toml` with `name`, `version`, `description`, `requires-python`, and all runtime dependencies from `requirements.txt` translated into the `dependencies` list using PEP 508 specifiers
- [ ] [S] Add an `[project.optional-dependencies]` table in `pyproject.toml` for each non-runtime group identified in Phase 1 (e.g., `dev`, `test`, `docs`), translating entries from the corresponding `requirements-*.txt` files
- [ ] [XS] Migrate any editable or VCS-based dependencies identified in Phase 1 into the appropriate `pyproject.toml` section or a companion `pip` constraints file, documenting any limitations
- [ ] [XS] Add a `[tool.pip]` or equivalent section in `pyproject.toml` (or a `pip.conf` / `.pip/pip.conf`) to preserve any custom index URLs that were present in `requirements.txt` via `--index-url` or `--extra-index-url` directives
- [ ] [XS] Delete `requirements.txt` and all companion `requirements-*.txt` files from the repository after confirming all entries are accounted for in `pyproject.toml`
- [ ] [XS] Update `.gitignore` to remove any `requirements*.txt` ignore rules that are no longer relevant and add ignore rules for build artifacts produced by the new build backend (e.g., `dist/`, `*.egg-info/`)
- [ ] [XS] Update any `setup.py` or `setup.cfg` files — if they exist solely to declare dependencies — to remove duplicate dependency declarations now managed by `pyproject.toml`, or remove the files entirely if they are otherwise empty

---

## Phase 3 — Testing & Validation

- [ ] [S] Create a fresh virtual environment, install the project using `pip install -e ".[dev,test]"` (or the equivalent extras) from `pyproject.toml` only, and verify the environment builds without errors
- [ ] [XS] Run `pip freeze > freeze-after.txt` in the new environment and diff it against `freeze-before.txt` to confirm no unintended dependency additions, removals, or version changes
- [ ] [S] Execute the full existing test suite against the environment installed from `pyproject.toml` and confirm all tests pass at the same rate as the pre-migration baseline
- [ ] [XS] Verify that all optional dependency groups install cleanly in isolation (e.g., `pip install -e ".[test]"` alone, `pip install -e ".[docs]"` alone) without pulling in unintended extras

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update all CI pipeline job definitions (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, or equivalent) to replace `pip install -r requirements.txt` commands with `pip install -e ".[dev,test]"` (or the appropriate extras) referencing `pyproject.toml`
- [ ] [XS] Update any `Dockerfile` or container build files that reference `requirements.txt` (e.g., `COPY requirements.txt .` / `RUN pip install -r requirements.txt`) to instead copy `pyproject.toml` and run `pip install .` or `pip install -e .`
- [ ] [XS] Update any `Makefile`, `tox.ini`, `noxfile.py`, or developer-facing shell scripts that reference `requirements.txt` install commands to use the `pyproject.toml`-based install commands
- [ ] [XS] Update `tox.ini` or `nox` session definitions (if present) to set `extras` or `deps` fields to reference the new optional dependency groups defined in `pyproject.toml` rather than `requirements-*.txt` files

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update `README.md` (or equivalent onboarding documentation) to replace all `pip install -r requirements.txt` instructions with `pip install -e ".[dev]"` (or the appropriate extras) and explain the new extras groups available
- [ ] [XS] Add an entry to `CHANGELOG.md` (or equivalent) documenting the migration from `requirements.txt` to `pyproject.toml`, the motivation, and any developer workflow changes
- [ ] [XS] Update any contributing guide (`CONTRIBUTING.md`) or developer setup runbook that references `requirements.txt` to reflect the new `pyproject.toml`-based workflow
- [ ] [XS] Open the migration PR, request review from at least one other contributor, and confirm CI passes end-to-end before merging
- [ ] [XS] After merging, monitor the first post-merge CI runs and any developer environment setup reports for unexpected dependency resolution failures and resolve promptly