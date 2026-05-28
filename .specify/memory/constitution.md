# CONSTITUTION
## Dependency Management Migration: requirements.txt → pyproject.toml

---

## Project Identity

**Name:** Dependency Management Modernization
**Purpose:** Migrate the project's Python dependency management from legacy `requirements.txt` files to the standardized `pyproject.toml` format (PEP 517/518/621).
**High-Level Goal:** Establish a single, authoritative source of truth for project metadata and dependencies, replacing fragmented `requirements.txt` files with a standards-compliant `pyproject.toml` configuration.

---

## Guiding Principles

1. **Prefer `pyproject.toml` over `requirements.txt` for all dependency declarations** because `requirements.txt` is a non-standard, tooling-specific format that lacks project metadata integration and is not aligned with current Python packaging standards (PEP 621).
2. **Prefer a single `pyproject.toml` over multiple requirement files** because fragmented files (e.g., `requirements-dev.txt`, `requirements-test.txt`) create maintenance overhead and dependency drift risk.
3. **Prefer explicit dependency groups (e.g., `[project.optional-dependencies]`) over flat lists** because grouping separates runtime, development, and test dependencies clearly and reduces accidental production bloat.
4. **Prefer preserving existing pinned versions during migration over re-resolving** because uncontrolled version changes introduce regression risk outside the scope of this task.
5. **Prefer non-destructive migration over in-place replacement** because the original `requirements.txt` files should remain available until the new configuration is validated, reducing rollback risk.

---

## Constraints

- **Scope freeze:** This migration is limited strictly to dependency management tooling. No library upgrades, runtime changes, or application code modifications are in scope.
- **Effort ceiling:** Moderate effort tier — scope must remain bounded to migration and validation only; no exploratory refactoring.
- **Dependency fidelity:** All dependencies present in existing `requirements.txt` files must be accounted for in `pyproject.toml`. No dependency may be silently dropped.
- **Build backend:** TODO — the specific build backend (`hatchling`, `setuptools`, `flit`, `pdm`, etc.) must be confirmed before implementation begins, as it affects `pyproject.toml` structure.
- **Runtime version:** TODO — minimum Python version constraint (`requires-python`) must be confirmed from the existing project environment.
- **Tooling mandate:** TODO — confirm whether the team standardizes on `pip`, `poetry`, `hatch`, or `pdm` as the primary installer/resolver, as this affects optional-dependency syntax and lock file strategy.

---

## Quality Standards

- **Completeness check:** A diff between all dependencies in legacy `requirements.txt` files and those declared in `pyproject.toml` must show zero omissions before the migration is considered complete.
- **Installation validation:** `pip install -e ".[dev,test]"` (or equivalent for the chosen build backend) must succeed in a clean virtual environment with no errors.
- **CI gate:** The existing CI pipeline must pass using only `pyproject.toml` as the dependency source, with `requirements.txt` references removed from CI configuration.
- **No regression:** All pre-existing tests must pass post-migration without modification to test code.
- **Review requirement:** The final `pyproject.toml` must receive at least one peer code review confirming dependency group accuracy before `requirements.txt` files are deleted.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt `pyproject.toml` as the sole dependency manifest | Aligns with PEP 621 standard; eliminates non-standard `requirements.txt` format | Accepted |
| ADR-002 | Retain `requirements.txt` files until CI validation passes | Reduces rollback risk during transition; files deleted only after full validation | Accepted |
| ADR-003 | Map dev/test requirements to optional dependency groups | Maintains separation of concerns without multiple files | Accepted |
| ADR-004 | Select build backend | TODO — must be decided before implementation; choice affects `[build-system]` table | Proposed |
| ADR-005 | Lock file strategy post-migration | TODO — determine whether a lock file (`pip-tools`, `poetry.lock`, etc.) is required | Proposed |