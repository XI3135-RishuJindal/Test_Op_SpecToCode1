# Spec: Migrate Dependency Management from requirements.txt to pyproject.toml

## Summary

This spec covers the migration of Python dependency management from the legacy `requirements.txt` file format to the modern `pyproject.toml` standard (PEP 517/518/621). The expected outcome is a single, authoritative source of truth for project metadata and dependencies, replacing the existing `requirements.txt`-based workflow with a `pyproject.toml`-based configuration compatible with current Python packaging standards.

## Motivation

- **Standards compliance:** `requirements.txt` is not a packaging standard — it is a pip-specific convention. PEP 517, PEP 518, and PEP 621 define `pyproject.toml` as the standardised way to declare project metadata and dependencies, and it is now supported by all major Python build backends (setuptools, hatchling, flit, PDM, etc.).
- **Tech debt reduction:** Maintaining dependencies in a flat `requirements.txt` file provides no support for dependency groups (e.g., dev, test, docs), no structured metadata, and no build system declaration, accumulating tooling and maintenance debt over time.
- **Tooling ecosystem alignment:** Modern Python tooling (pip ≥ 21.3, build, tox, pytest, mypy, ruff, etc.) preferentially reads from `pyproject.toml`, reducing friction and configuration duplication.
- **Upgrade urgency:** Medium — there is no immediate CVE or EOL forcing this change, but continued use of `requirements.txt` as the sole dependency source increases friction with modern CI/CD and developer tooling.
- **Reproducibility:** `pyproject.toml` supports optional lock-file workflows (e.g., via `pip-compile`, `uv`, or `pdm lock`) that improve reproducibility beyond what a bare `requirements.txt` provides.

> **Note:** Specific runtime version, build tool, and framework details were not provided in the tech analysis. Version-specific constraints are marked TODO below.

## Current State

- **Dependency declaration:** All runtime (and likely development) dependencies are declared in one or more `requirements.txt` files (e.g., `requirements.txt`, `requirements-dev.txt`, `requirements-test.txt` — exact filenames TODO).
- **Build system:** No `pyproject.toml` is currently present, or it exists without a `[project]` or `[build-system]` table (TODO — confirm current state of any existing `pyproject.toml`).
- **Installation workflow:** Dependencies are installed via `pip install -r requirements.txt`. CI pipelines and developer setup scripts reference this file directly.
- **Dependency pinning:** TODO — confirm whether `requirements.txt` contains pinned versions (`==`), minimum bounds (`>=`), or unpinned entries.
- **Extras / dependency groups:** TODO — confirm whether separate `requirements-dev.txt` or similar files exist and what they contain.
- **Project metadata:** TODO — confirm where project name, version, author, and license are currently declared (e.g., `setup.py`, `setup.cfg`, or absent).

## Proposed Changes

For each affected component, the following changes are proposed:

| Component | Before | After | Breaking? |
|---|---|---|---|
| Dependency declaration | `requirements.txt` (pip-specific flat file) | `[project.dependencies]` table in `pyproject.toml` | N |
| Dev/test dependencies | Separate `requirements-dev.txt` / `requirements-test.txt` (TODO — confirm filenames) | `[project.optional-dependencies]` groups (e.g., `dev`, `test`) or build-backend-specific dependency groups in `pyproject.toml` | N |
| Build system declaration | Absent or in `setup.py` / `setup.cfg` (TODO) | `[build-system]` table in `pyproject.toml` | N |
| Project metadata | `setup.py` / `setup.cfg` / absent (TODO) | `[project]` table in `pyproject.toml` | N |
| CI install step | `pip install -r requirements.txt` | `pip install .` or `pip install .[dev,test]` | Y — CI scripts must be updated |
| Developer setup docs | References to `requirements.txt` in README / CONTRIBUTING | Updated to reference `pyproject.toml`-based install commands | N |
| `requirements.txt` files | Present and authoritative | Removed or retained only as generated lock files (TODO — decide lock-file strategy) | Y — files removed from repo |

**What is removed:**
- `requirements.txt` as the authoritative dependency source (file may be deleted or demoted to a generated lock file).
- Any supplementary `requirements-*.txt` files whose content is absorbed into `pyproject.toml` optional dependency groups.

**What is added:**
- `pyproject.toml` with `[build-system]`, `[project]`, and `[project.optional-dependencies]` tables.
- TODO: Decision on build backend (e.g., `setuptools`, `hatchling`, `flit-core`) — to be confirmed.
- TODO: Decision on lock-file strategy (e.g., `pip-compile` generating `requirements.lock`, or `uv.lock`, or none).

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `requirements.txt` removed or no longer authoritative | Any script, CI job, or developer workflow that runs `pip install -r requirements.txt` will break | Update all `pip install -r requirements.txt` invocations to `pip install .` (runtime deps) or `pip install .[dev]` / `pip install .[test]` (optional groups) |
| Dev/test dependency group names change | Developers and CI jobs referencing specific `requirements-*.txt` files will break | Map old file names to new optional-dependency group names; update documentation and CI configuration accordingly |
| Build system now declared in `pyproject.toml` | Any tooling that assumed no build system declaration may behave differently | TODO — audit existing `setup.py` / `setup.cfg` for conflicts before removal |
| Project metadata moved to `pyproject.toml` | Tools reading metadata from `setup.py` or `setup.cfg` must be updated | TODO — confirm whether `setup.py` / `setup.cfg` exist and plan their deprecation or removal |
| Lock-file strategy change | If `requirements.txt` was used as a lock file for reproducible installs, removing it without a replacement breaks reproducibility | TODO — decide and document replacement lock-file mechanism before removing `requirements.txt` |

## Acceptance Criteria

1. **Given** the repository contains a `pyproject.toml`, **when** `pip install .` is executed in a clean virtual environment, **then** all runtime dependencies declared in the former `requirements.txt` are installed without error and the package is importable.

2. **Given** the repository contains a `pyproject.toml` with optional dependency groups, **when** `pip install .[dev]` and `pip install .[test]` are executed in a clean virtual environment, **then** all development and test dependencies formerly declared in supplementary `requirements-*.txt` files are installed without error.

3. **Given** the migrated `pyproject.toml`, **when** `pip check` is run after installation, **then** no dependency conflicts are reported.

4. **Given** the CI pipeline has been updated, **when** the CI workflow runs, **then** all install steps complete successfully using `pyproject.toml`-based install commands and no step references `requirements.txt`.

5. **Given** the full test suite existed and passed before migration, **when** the test suite is executed after migration in an environment installed via `pyproject.toml`, **then** all previously passing tests continue to pass with no new failures.

6. **Given** the `pyproject.toml` is present, **when** `python -m build` (or the equivalent build-backend command) is executed, **then** a valid source distribution (`.tar.gz`) and wheel (`.whl`) are produced without error.

7. **Given** the migration is complete, **when** the repository is inspected, **then** no `requirements.txt` file (or supplementary `requirements-*.txt` files) serves as the authoritative dependency source — either the files are absent or they are clearly marked as generated lock files with a corresponding generation process documented.

8. **Given** the `pyproject.toml`, **when** a dependency version constraint is validated against the versions that were pinned or bounded in the original `requirements.txt`, **then** every dependency present in the original file is represented in `pyproject.toml` with an equivalent or explicitly justified constraint.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What are the exact filenames and contents of all current `requirements*.txt` files? | TODO | TODO |
| 2 | Does a `pyproject.toml` already exist in the repository? If so, what tables does it currently contain? | TODO | TODO |
| 3 | Do `setup.py` or `setup.cfg` files exist, and should they be removed as part of this migration? | TODO | TODO |
| 4 | Which build backend should be adopted (`setuptools`, `hatchling`, `flit-core`, other)? | TODO | TODO |
| 5 | What lock-file strategy (if any) should replace the reproducibility role of a pinned `requirements.txt`? (e.g., `pip-compile`, `uv lock`, `pdm lock`, none) | TODO | TODO |
| 6 | Are there any deployment or production systems (e.g., Docker images, Heroku, serverless) that install dependencies directly from `requirements.txt` and require separate migration steps? | TODO | TODO |
| 7 | What are the exact optional dependency group names to use (e.g., `dev`, `test`, `docs`, `lint`)? | TODO | TODO |
| 8 | What is the minimum supported Python version to declare in `pyproject.toml` under `requires-python`? | TODO | TODO |