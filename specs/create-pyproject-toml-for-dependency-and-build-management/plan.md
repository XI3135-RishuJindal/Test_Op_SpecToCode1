# PLAN: Create pyproject.toml for Dependency and Build Management

## Overview

**Migration Strategy: Big-Bang**

This task introduces a `pyproject.toml` file as the single source of truth for dependency declaration and build configuration. Because the task is additive (creating a new file rather than replacing a running system), a big-bang approach is appropriate and low-risk. There is no existing build tooling described in the tech analysis to migrate away from incrementally, so a strangler-fig or parallel-run strategy would add unnecessary complexity without benefit.

> **Note:** The tech analysis reports language, runtime, and build tool as "unknown." Several decisions below are marked TODO pending discovery of the actual project state (e.g., whether a `setup.py`, `setup.cfg`, or `requirements.txt` already exists).

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit existing dependency files and project structure | None | TODO (person-days not provided in upgrade option) |
| 2 | Author `pyproject.toml` with build backend, metadata, and dependencies | Phase 1 complete | TODO |
| 3 | Validate build, install, and CI integration | Phase 2 complete | TODO |
| 4 | Deprecate and remove legacy dependency files (if any) | Phase 3 passing | TODO |

> **TODO:** Effort estimates in person-days cannot be derived because the upgrade option detail was not provided. Populate these values once the option is specified.

---

## Component Changes

### `pyproject.toml` (new file — project root)

**What changes:** This file is created from scratch. It consolidates build system declaration, project metadata, dependency lists, optional dependency groups, and tool configuration (linter, formatter, test runner) into a single PEP 517/518/621-compliant file.

**Structural sections to include:**

```toml
[build-system]
# TODO: Confirm build backend — candidates are hatchling, flit-core, setuptools>=61
requires = ["TODO"]
build-backend = "TODO"

[project]
name = "TODO"          # derive from existing setup.py / setup.cfg if present
version = "TODO"       # or use dynamic = ["version"]
description = "TODO"
requires-python = "TODO"   # derive from runtime discovery
dependencies = []          # TODO: migrate from requirements.txt / install_requires

[project.optional-dependencies]
dev  = []   # TODO: migrate from requirements-dev.txt / extras_require["dev"]
test = []   # TODO: migrate from test requirements

[tool.TODO]  # e.g., [tool.pytest.ini_options], [tool.ruff], [tool.mypy]
```

**Files affected:**

| File | Action | Notes |
|------|--------|-------|
| `pyproject.toml` | **Create** | Primary deliverable |
| `setup.py` | **Remove or stub** | TODO — only if confirmed present |
| `setup.cfg` | **Remove** | TODO — only if confirmed present; migrate keys to `pyproject.toml` |
| `requirements.txt` | **Deprecate** | TODO — only if confirmed present; content migrated to `[project].dependencies` |
| `requirements-dev.txt` | **Deprecate** | TODO — only if confirmed present; content migrated to `[project.optional-dependencies].dev` |

**APIs modified:** N/A — no runtime APIs are changed by this task.

---

## Dependency Upgrade Plan

> **TODO:** The tech analysis did not identify specific dependencies, current versions, or target versions. The table below provides the structural template; populate it after Phase 1 audit.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Build backend (e.g., `setuptools`, `hatchling`, `flit-core`) | TODO | TODO | TODO | Declare under `[build-system].requires` |
| Runtime deps (from `requirements.txt`) | TODO | TODO | TODO | Move to `[project].dependencies` |
| Dev/test deps | TODO | TODO | TODO | Move to `[project.optional-dependencies]` |

---

## Infrastructure Changes

**CI/CD Pipeline:**
- TODO: If a CI pipeline exists (GitHub Actions, GitLab CI, Jenkins, etc.), update the dependency-install step from `pip install -r requirements.txt` to `pip install -e ".[dev,test]"` or equivalent.
- TODO: Add a CI gate that runs `pip check` after install to validate dependency resolution.
- TODO: If a lockfile tool is adopted (e.g., `pip-compile`, `uv lock`, `poetry.lock`), add a lockfile-generation step to CI.

**Docker:**
- TODO: If a `Dockerfile` exists, update the `RUN pip install` instruction to use the new `pyproject.toml`-based install command.

**IaC / Kubernetes:**
- N/A — not applicable to this task unless the build artifact changes in a way that affects image tags or deployment manifests (TODO: verify).

---

## Rollback Strategy

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 (Audit) | No changes made; nothing to roll back. |
| Phase 2 (Author `pyproject.toml`) | Delete `pyproject.toml`. Restore any modified legacy files from version control (`git checkout -- setup.py setup.cfg requirements.txt`). |
| Phase 3 (Validate & CI) | Revert CI pipeline changes via `git revert` on the pipeline config commit. The legacy install path is restored immediately. |
| Phase 4 (Remove legacy files) | Restore deleted files from version control (`git checkout <pre-deletion-commit> -- requirements.txt setup.py`). Remove `pyproject.toml` if necessary. |

Each phase is committed separately so any phase can be reverted independently without affecting prior phases.

---

## Testing Strategy

### Test Pyramid

| Layer | What to Test | Tool | Coverage Target / Gate |
|-------|-------------|------|------------------------|
| **Unit** | `pyproject.toml` is valid TOML and passes schema validation | `tomllib` (stdlib ≥ 3.11) or `tomli`; `validate-pyproject` CLI | 100% of declared fields parse without error — CI hard gate |
| **Integration** | Package installs cleanly in a fresh virtual environment | `pip install -e ".[dev,test]"` in CI matrix | Zero install errors across all supported Python versions (TODO: confirm version matrix) |
| **Integration** | All previously passing tests still pass after dependency migration | TODO: existing test runner (pytest assumed) | TODO: match or exceed pre-migration pass rate |
| **Regression** | No dependency version regressions; `pip check` reports no conflicts | `pip check` | Zero conflicts — CI hard gate |
| **Performance** | N/A for this task | — | — |

### CI Gates (must pass before merge)
1. `validate-pyproject pyproject.toml` — schema lint.
2. `pip install -e ".[dev,test]"` in a clean `venv` — install smoke test.
3. `pip check` — dependency conflict check.
4. TODO: Full test suite run if test runner is identified in Phase 1.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Existing dependency files audited; build backend selected | Phase 1 | TODO | TODO |
| `pyproject.toml` authored and reviewed | Phase 2 | TODO | TODO |
| CI pipeline updated; all gates passing | Phase 3 | TODO | TODO |
| Legacy files removed; PR merged | Phase 4 | TODO | TODO |

> **TODO:** Populate dates and owners once the upgrade option person-days estimate and team assignments are confirmed.