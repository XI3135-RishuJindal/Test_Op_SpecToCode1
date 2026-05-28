# Spec: Migrate Dependency Management from requirements.txt to pyproject.toml

## Summary

This spec covers the migration of Python dependency management from the legacy `requirements.txt` file format to the modern `pyproject.toml` standard (PEP 517/518/621). The expected outcome is a single, authoritative source of truth for project metadata and dependencies, replacing the existing `requirements.txt`-based workflow with a `pyproject.toml`-based configuration compatible with modern Python packaging tooling.

## Motivation

- **Standardization:** `requirements.txt` is not a packaging standard — it is a pip-specific convention that does not encode project metadata, build system requirements, or dependency groups in a structured, interoperable way. PEP 621 (`pyproject.toml`) is the current Python packaging standard adopted by the Python Packaging Authority (PyPA).
- **Tooling compatibility:** Modern Python tooling (pip ≥ 21.3, build, hatch, poetry, uv, etc.) natively resolves dependencies from `pyproject.toml`. Continued reliance on `requirements.txt` limits compatibility with these tools.
- **Tech debt reduction:** The tech analysis identifies this migration as a **medium urgency** item representing accumulated tech debt in the build and dependency management layer.
- **Single source of truth:** `requirements.txt` files frequently diverge from actual project metadata when both exist, creating inconsistency between what is declared and what is installed.
- **Dependency grouping:** `pyproject.toml` supports structured optional dependency groups (e.g., `[project.optional-dependencies]` for `dev`, `test`, `docs`), which `requirements.txt` does not natively support without multiple files and manual coordination.

## Current State

- Project dependencies are declared in one or more `requirements.txt` files (e.g., a root-level `requirements.txt` and potentially separate files such as `requirements-dev.txt`, `requirements-test.txt`).
- There is no `pyproject.toml` present, or if present, it does not contain a `[project]` table with dependency declarations.
- Dependencies are installed via `pip install -r requirements.txt`.
- No structured build system declaration (`[build-system]` table) is currently in place via `pyproject.toml`.
- Project metadata (name, version, description, author, license) is either absent, declared in a `setup.py`, `setup.cfg`, or scattered across other files — TODO: confirm exact current metadata source from codebase.
- TODO: Confirm whether multiple `requirements.txt` variants exist (e.g., pinned vs. unpinned, dev vs. prod).
- TODO: Confirm whether a `setup.py` or `setup.cfg` is present and must be consolidated.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Core dependency declaration | `requirements.txt` | `[project.dependencies]` in `pyproject.toml` | N — functionally equivalent for installers |
| Dev/test dependencies | `requirements-dev.txt` / `requirements-test.txt` (if present) | `[project.optional-dependencies]` groups in `pyproject.toml` | N — install command changes |
| Build system declaration | Absent or `setup.py` | `[build-system]` table in `pyproject.toml` | N |
| Project metadata | `setup.py` / `setup.cfg` / absent | `[project]` table in `pyproject.toml` | N |
| CI install command | `pip install -r requirements.txt` | `pip install .` or `pip install .[dev,test]` | Y — CI pipeline commands must be updated |
| Contributor install instructions | README / docs referencing `requirements.txt` | Updated to reference `pyproject.toml`-based install | N — documentation change only |

**What is removed:**
- `requirements.txt` (and variants) are removed as the authoritative dependency source after migration is validated.

**What is added:**
- `pyproject.toml` with `[build-system]`, `[project]`, and `[project.optional-dependencies]` tables.

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| CI pipeline install commands change from `pip install -r requirements.txt` to `pip install .[group]` | CI workflows fail if not updated | Update all CI configuration files to use the new install command before removing `requirements.txt` |
| Developer onboarding instructions reference `requirements.txt` | New contributors follow outdated steps | Update README and any contributing guides to reflect `pyproject.toml`-based workflow |
| Any tooling or scripts that explicitly reference `requirements.txt` by filename | Scripts break at runtime | Audit all scripts and tooling for hardcoded references to `requirements.txt` and update accordingly — TODO: full list of affected scripts unknown until codebase audit |
| Pinned transitive dependencies (if `requirements.txt` contained pinned versions) may no longer be enforced | Reproducibility risk | Evaluate whether a lock file tool (e.g., `pip-compile`, `uv lock`) is needed to preserve pinned reproducibility — TODO: confirm current pinning strategy |

## Acceptance Criteria

1. **Given** the repository contains a `pyproject.toml`, **when** `pip install .` is executed in a clean virtual environment, **then** all production dependencies are installed without error and the package is importable.
2. **Given** the repository contains a `pyproject.toml` with an optional dependency group named `dev` (or equivalent), **when** `pip install .[dev]` is executed, **then** all development dependencies are installed without error.
3. **Given** the repository contains a `pyproject.toml` with an optional dependency group named `test` (or equivalent), **when** `pip install .[test]` is executed and the test suite is run, **then** all tests pass at the same rate as before the migration.
4. **Given** the migration is complete, **when** the repository is inspected, **then** no `requirements.txt` file (or variant) exists as an authoritative dependency source — or, if retained for legacy tooling, it is explicitly marked as deprecated and not the source of truth.
5. **Given** the updated CI pipeline configuration, **when** a CI build is triggered, **then** the build completes successfully using only `pyproject.toml`-based install commands, with no reference to `requirements.txt`.
6. **Given** the `pyproject.toml` `[project]` table, **when** validated with a conformant tool (e.g., `pip install --dry-run` or a metadata validator), **then** all required PEP 621 fields (name, version, dependencies) are present and valid.
7. **Given** a developer follows the updated README onboarding instructions, **when** they set up the project from scratch, **then** they can install all dependencies and run the test suite successfully without referencing any `requirements.txt` file.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | Does the project currently have a `setup.py` or `setup.cfg` that must be consolidated into `pyproject.toml` as part of this migration? | TODO | TODO |
| 2 | Are there multiple `requirements.txt` variants (e.g., pinned, dev, test, docs)? What is the full list? | TODO | TODO |
| 3 | Does the current `requirements.txt` contain pinned transitive dependencies for reproducibility? If so, should a lock file mechanism be adopted? | TODO | TODO |
| 4 | Which build backend should be declared in `[build-system]` (e.g., `setuptools`, `hatchling`, `flit-core`)? | TODO | TODO |
| 5 | Are there any CI/CD systems, deployment scripts, or external tooling outside the repository that reference `requirements.txt` by name and would be broken by its removal? | TODO | TODO |
| 6 | Should `requirements.txt` be retained temporarily as a generated artifact (e.g., via `pip-compile`) for legacy compatibility during a transition period? | TODO | TODO |