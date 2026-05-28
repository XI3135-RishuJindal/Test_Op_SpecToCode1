# CONSTITUTION
## Dependency Management Migration: requirements.txt → pyproject.toml

---

## Project Identity

**Name:** Dependency Management Modernization
**Purpose:** Migrate Python dependency management from legacy `requirements.txt` files to the standardized `pyproject.toml` format (PEP 517/518/621).
**High-Level Goal:** Establish a single, authoritative source of truth for project metadata and dependencies, replacing fragmented `requirements.txt` files with a standards-compliant `pyproject.toml` configuration.

---

## Guiding Principles

1. **Prefer `pyproject.toml` over `requirements.txt` for all dependency declarations** because `requirements.txt` is a non-standard, tooling-specific format that lacks metadata, version bounds semantics, and build system integration.
2. **Prefer preserving existing dependency versions over upgrading them** because this migration's scope is structural, not a dependency upgrade; conflating the two increases risk and scope.
3. **Prefer a single `pyproject.toml` over multiple scattered requirement files** because fragmented files (e.g., `requirements-dev.txt`, `requirements-test.txt`) are a known source of drift and inconsistency.
4. **Prefer explicit dependency groups (e.g., `[project.optional-dependencies]`) over flat lists** because separating runtime, dev, and test dependencies reduces production artifact bloat and clarifies intent.
5. **Prefer non-destructive migration over immediate deletion of legacy files** because downstream consumers (CI pipelines, deployment scripts) may still reference `requirements.txt`; removal must be coordinated and confirmed.

---

## Constraints

- **Scope freeze:** This project is strictly limited to dependency management migration. No runtime upgrades, no dependency version bumps, and no application code changes are in scope.
- **Effort ceiling:** Moderate effort tier; no large-scale refactoring or toolchain replacement is authorized within this engagement.
- **Technology mandate:** The target format is `pyproject.toml` per PEP 621. The choice of backing tool (e.g., pip, Poetry, Hatch, PDM) is **TODO — must be decided before implementation begins** (see Decision Log).
- **Compatibility constraint:** The migrated configuration must produce a functionally equivalent dependency set to the current `requirements.txt` files — no additions, removals, or silent version changes.
- **Runtime/Language version:** TODO — Python version minimum must be confirmed and declared in `pyproject.toml` under `requires-python`.

---

## Quality Standards

- **Equivalence verification:** A dependency resolution check must confirm that all packages resolvable from the old `requirements.txt` files are resolvable from `pyproject.toml` before the legacy files are removed. This must be a documented, repeatable step.
- **CI gate:** All existing CI pipelines must pass using only `pyproject.toml` as the dependency source before the migration is considered complete.
- **No orphaned files:** All `requirements*.txt` files must be either removed or explicitly retained with a deprecation notice and a tracked removal ticket — no silent abandonment.
- **Documentation:** `README` or equivalent must be updated to reflect the new install instructions (`pip install -e ".[dev]"` or tool equivalent) before the PR is merged.
- **Code review:** Migration PR requires at least one reviewer who can verify dependency equivalence and CI pipeline compatibility.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Migrate to `pyproject.toml` as the single dependency manifest | PEP 621 standardization; eliminates non-standard `requirements.txt` fragmentation | Accepted |
| ADR-002 | Scope limited to structural migration only; no dependency version changes | Minimizes risk; keeps the change reviewable and reversible | Accepted |
| ADR-003 | Retain `requirements.txt` files with deprecation notice until all consumers are updated | Prevents breaking CI/CD pipelines that reference legacy files before cutover is confirmed | Accepted |
| ADR-004 | Choice of build backend (pip/setuptools, Poetry, Hatch, PDM) | TODO — must be evaluated against existing project structure and team tooling preferences | Proposed |
| ADR-005 | Minimum Python version (`requires-python`) | TODO — must be confirmed from existing runtime environment before `pyproject.toml` is authored | Proposed |