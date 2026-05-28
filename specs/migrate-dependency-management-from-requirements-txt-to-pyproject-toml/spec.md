# Spec: Migrate Dependency Management from requirements.txt to pyproject.toml

## Summary

This spec covers the migration of Python dependency management from the legacy `requirements.txt` file format to the modern `pyproject.toml` standard (PEP 517/518/621). The expected outcome is a single, authoritative source of truth for project metadata and dependencies, replacing the existing `requirements.txt`-based workflow with a `pyproject.toml`-based configuration compatible with current Python packaging standards.

## Motivation

- **Standards compliance:** `requirements.txt` is not a packaging standard — it is a pip-specific convention. PEP 621 (standardised project metadata in `pyproject.toml`) is now the accepted approach across the Python ecosystem and is required by modern build backends (Hatchling, Flit, PDM, setuptools ≥ 61).
- **Tooling fragmentation:** Maintaining dependencies solely in `requirements.txt` excludes the project from tooling that reads `pyproject.toml` (e.g., `pip`, `uv`, `poetry`, `dependabot` via PEP 621, type checkers, linters with project-aware configs).
- **Upgrade urgency:** Rated **medium** — there is no immediate CVE or EOL forcing this change, but continued use of `requirements.txt` alone accumulates tooling and maintenance debt.
- **Tech debt reduction:** Consolidating project metadata, build configuration, and dependency declarations into one file reduces the number of configuration files contributors must understand and maintain.

## Current State

- Dependencies are declared in one or more `requirements.txt` files (e.g., a root `requirements.txt` and potentially separate files for development or testing such as `requirements-dev.txt`, `requirements-test.txt`).
- There is no `pyproject.toml` present, or it exists without a `[project.dependencies]` table.
- Dependency installation is performed via `pip install -r requirements.txt`.
- No standardised project metadata (name, version, authors, license, Python version constraint) is machine-readable from a packaging-standard file.
- CI pipelines and contributor documentation reference `requirements.txt` directly.

> **TODO:** Confirm the exact set of `requirements.txt` files present in the repository (root, dev, test, docs, etc.) and whether a `pyproject.toml` or `setup.py`/`setup.cfg` already exists.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Core dependency declaration | `requirements.txt` | `[project.dependencies]` table in `pyproject.toml` | N — existing `pip install` workflows remain functional via PEP 517 |
| Development/optional dependencies | `requirements-dev.txt` (or equivalent) | `[project.optional-dependencies]` (e.g., `dev`, `test` extras) in `pyproject.toml` | N — callers must update install command to use extras syntax |
| Project metadata (name, version, etc.) | Absent or in `setup.py`/`setup.cfg` | `[project]` table in `pyproject.toml` | N |
| Build backend declaration | Absent or implicit | `[build-system]` table in `pyproject.toml` | N |
| CI install step | `pip install -r requirements.txt` | `pip install -e ".[dev,test]"` or equivalent | Y — CI configuration must be updated |
| Contributor documentation | References `requirements.txt` | Updated to reference `pyproject.toml` extras | Y — documentation must be updated |
| `requirements.txt` files | Present and authoritative | Removed or retained only as a generated/legacy artefact | Y — direct use of these files is deprecated |

> **TODO:** Confirm which build backend to adopt (e.g., `hatchling`, `setuptools`, `flit-core`, `pdm-backend`). This determines the exact shape of the `[build-system]` table.

> **TODO:** Confirm whether `requirements.txt` files should be fully deleted or retained as generated lock files for deployment reproducibility.

## Compatibility & Breaking Changes

| Breaking Change | Affected Caller | Migration Path |
|---|---|---|
| `pip install -r requirements.txt` no longer the canonical install command | CI pipelines, contributor onboarding scripts | Update to `pip install -e ".[dev]"` or equivalent extras invocation after `pyproject.toml` is in place |
| `requirements-dev.txt` (or equivalent) removed or no longer maintained | Developers installing dev dependencies manually | Use `pip install -e ".[dev]"` targeting the `dev` optional-dependency group in `pyproject.toml` |
| Project metadata previously absent or in `setup.py`/`setup.cfg` | Any tooling reading `setup.py`/`setup.cfg` | Migrate metadata to `[project]` table; remove or stub out legacy files |
| Dependency version pins format may differ | Automated tooling parsing `requirements.txt` directly | Update tooling to parse `pyproject.toml` or regenerate `requirements.txt` from it if still needed |
| `dependabot` / Renovate config targeting `requirements.txt` | Automated dependency update bots | Update bot configuration to target `pyproject.toml` |

> **TODO:** Determine if any deployment or infrastructure tooling (e.g., Docker builds, serverless packaging scripts) reads `requirements.txt` directly and requires a separate migration or a generated `requirements.txt` as an interim artefact.

## Acceptance Criteria

1. **Given** the repository contains a `pyproject.toml`, **when** a packaging-standard tool (e.g., `pip`, `build`, `uv`) reads it, **then** all previously declared runtime dependencies from `requirements.txt` are present under `[project.dependencies]` with equivalent version constraints.

2. **Given** the repository contains a `pyproject.toml` with optional-dependency groups, **when** a developer installs the project with the `dev` (or equivalent) extra, **then** all packages previously listed in `requirements-dev.txt` (or equivalent) are installed without error.

3. **Given** the updated CI pipeline, **when** the install step runs, **then** the build completes successfully and all tests pass — matching the pass/fail result of the previous `requirements.txt`-based install.

4. **Given** the `pyproject.toml` is present, **when** `pip check` is executed in a clean virtual environment after installation, **then** no dependency conflicts are reported.

5. **Given** the migration is complete, **when** a search is performed for any CI or script reference to `pip install -r`, **then** no such references remain pointing to the old `requirements.txt` files (or all remaining references are explicitly documented as intentional generated-artefact usage).

6. **Given** the `pyproject.toml` contains a `[project]` table, **when** project metadata is inspected (e.g., via `pip show <package-name>` or `importlib.metadata`), **then** the package name, version, and Python version constraint are correctly reported.

7. **Given** the migration is complete, **when** the automated dependency update bot (Dependabot/Renovate) runs, **then** it correctly identifies and proposes updates for dependencies declared in `pyproject.toml`.

> **TODO:** Define the exact test suite command to use as the baseline pass/fail reference for criterion 3.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | Which build backend should be adopted (`hatchling`, `setuptools`, `flit-core`, `pdm-backend`, other)? | TODO | TODO |
| 2 | Should `requirements.txt` be fully deleted, or regenerated from `pyproject.toml` as a pinned lock file for deployment reproducibility? | TODO | TODO |
| 3 | Are there multiple `requirements.txt` files (e.g., dev, test, docs)? What is the complete list? | TODO | TODO |
| 4 | Does a `setup.py` or `setup.cfg` currently exist, and does it need to be migrated or removed as part of this effort? | TODO | TODO |
| 5 | Do any deployment pipelines, Docker images, or infrastructure scripts install dependencies directly from `requirements.txt` and require a separate migration plan? | TODO | TODO |
| 6 | Should a lock file tool (e.g., `pip-compile`, `uv lock`) be adopted alongside `pyproject.toml` to maintain reproducible builds? | TODO | TODO |
| 7 | What is the minimum supported Python version to declare in `[project.requires-python]`? | TODO | TODO |