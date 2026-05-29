# Spec: Create pyproject.toml for Dependency and Build Management

## Summary

This spec covers the introduction of a `pyproject.toml` file to centralize dependency declaration and build system configuration for the project. The expected outcome is a single, standards-compliant configuration file that replaces or consolidates existing ad-hoc dependency and build management artifacts, enabling reproducible builds and modern Python tooling compatibility.

## Motivation

- **Standardization:** PEP 517 and PEP 518 established `pyproject.toml` as the canonical configuration file for Python projects. Adopting it aligns the project with current Python packaging standards and ecosystem expectations.
- **Tech Debt:** The absence of a `pyproject.toml` represents medium-urgency tech debt. Without it, dependency resolution, build isolation, and tool configuration are fragmented or undefined, increasing onboarding friction and CI inconsistency.
- **Tooling Compatibility:** Modern Python tools (e.g., pip, build, pytest, linters, type checkers) increasingly expect or require `pyproject.toml` for configuration. Projects lacking it may encounter degraded or unsupported behavior with current tool versions.
- **Reproducibility:** Explicit dependency pinning and build system declaration reduce "works on my machine" failures across development, CI, and production environments.
- **Upgrade Urgency:** Rated **medium** — no immediate CVE or EOL forcing function, but continued absence increases integration risk as tooling drops legacy configuration support.

## Current State

The current dependency and build management approach is not fully specified in the provided context. The following represents the known state:

- **Language/Runtime:** TODO — specific language version not confirmed in provided analysis.
- **Build Tool:** TODO — existing build tool or configuration format not identified.
- **Existing Dependency Files:** TODO — it is unknown whether `setup.py`, `setup.cfg`, `requirements.txt`, or other files currently exist and would be affected.
- **Existing Tool Configuration:** TODO — it is unknown which tool-specific config files (e.g., `tox.ini`, `.flake8`, `mypy.ini`, `pytest.ini`) currently exist and are candidates for consolidation.
- **Key Behaviors Affected:** Dependency installation, build artifact generation, and developer tooling invocation.

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Build system declaration | TODO (absent or in `setup.py`/`setup.cfg`) | Declared in `pyproject.toml` `[build-system]` table | TODO |
| Project metadata | TODO (absent or in `setup.py`/`setup.cfg`) | Declared in `pyproject.toml` `[project]` table | TODO |
| Dependency list | TODO (absent, `requirements.txt`, or `setup.py`) | Declared in `pyproject.toml` `[project.dependencies]` | TODO |
| Optional/dev dependencies | TODO | Declared in `pyproject.toml` `[project.optional-dependencies]` | TODO |
| Tool configuration (linters, test runner, type checker) | Scattered across individual config files (TODO — confirm which exist) | Consolidated into `pyproject.toml` `[tool.*]` tables where supported | N |
| CI dependency installation | TODO | Driven by `pyproject.toml` declarations | TODO |

## Compatibility & Breaking Changes

| Change | Impact | Migration Path |
|---|---|---|
| Removal or replacement of `setup.py` | Any caller invoking `python setup.py` directly will break | Callers must switch to PEP 517-compliant build frontend (e.g., `python -m build`). TODO — confirm whether `setup.py` currently exists. |
| Removal or replacement of `setup.cfg` | Tool config and metadata in `setup.cfg` will no longer be read | Content must be migrated to equivalent `pyproject.toml` tables. TODO — confirm whether `setup.cfg` currently exists. |
| Removal of standalone `requirements.txt` | Scripts or CI steps referencing `requirements.txt` directly will break | CI and scripts must be updated to install from `pyproject.toml` declarations. TODO — confirm whether `requirements.txt` currently exists and its scope. |
| Consolidation of tool config files | Individual config files removed or emptied | Developers and CI must rely on `pyproject.toml` for tool configuration. TODO — confirm which tool config files exist. |

## Acceptance Criteria

1. **Given** the repository contains a `pyproject.toml`, **when** a PEP 517-compliant build frontend is invoked, **then** a valid build artifact is produced without errors.
2. **Given** the `pyproject.toml` `[project.dependencies]` table is populated, **when** a fresh virtual environment installs the project, **then** all declared dependencies are installed at the specified version constraints with no resolution errors.
3. **Given** the `pyproject.toml` `[project.optional-dependencies]` table includes a development dependency group, **when** the project is installed with that group, **then** all development tools are available in the environment.
4. **Given** the `pyproject.toml` `[build-system]` table is present, **when** pip or an equivalent tool performs a build-isolated install, **then** the build succeeds without requiring a pre-installed build backend.
5. **Given** tool configuration has been migrated to `[tool.*]` tables in `pyproject.toml`, **when** each respective tool (TODO — enumerate specific tools once confirmed) is invoked, **then** it reads configuration from `pyproject.toml` and produces the same behavior as the prior configuration.
6. **Given** the `pyproject.toml` is present, **when** a CI pipeline runs the full install and build sequence, **then** the pipeline completes successfully with a green status.
7. **Given** the `pyproject.toml` `[project]` table is populated, **when** project metadata is queried via `importlib.metadata` or equivalent, **then** the returned name, version, and description match the values declared in `pyproject.toml`.

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the target Python version (minimum and maximum) to declare in `pyproject.toml`? | TODO | TODO |
| 2 | Which build backend should be used (e.g., setuptools, hatchling, flit-core, pdm-backend)? | TODO | TODO |
| 3 | Do `setup.py`, `setup.cfg`, or `requirements.txt` currently exist and need migration or removal? | TODO | TODO |
| 4 | Which standalone tool config files (e.g., `tox.ini`, `pytest.ini`, `.flake8`, `mypy.ini`) currently exist and are candidates for consolidation? | TODO | TODO |
| 5 | Are there any consumers (CI systems, deployment scripts, external tooling) that depend on the current build/dependency artifacts and will require coordinated updates? | TODO | TODO |
| 6 | Should optional dependency groups be defined (e.g., `dev`, `test`, `docs`), and if so, what is their intended composition? | TODO | TODO |
| 7 | Is version pinning strategy for dependencies (exact pins vs. compatible release vs. ranges) already decided or does it need to be established? | TODO | TODO |