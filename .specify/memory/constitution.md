# CONSTITUTION
## Dependency Management Migration: requirements.txt → pyproject.toml

---

## Project Identity

**Name:** Dependency Management Modernization
**Purpose:** Migrate Python dependency management from legacy `requirements.txt` files to the standardized `pyproject.toml` format (PEP 517/518/621).
**High-Level Goal:** Establish a single, standards-compliant source of truth for project metadata and dependencies, eliminating the fragmentation and tooling limitations associated with `requirements.txt`.

---

## Guiding Principles

1. **Prefer `pyproject.toml` as the sole dependency manifest over maintaining any `requirements.txt` files** because split manifests create drift and ambiguity about which file is authoritative.
2. **Prefer a single migration pass over an incremental dual-file period** because maintaining both formats simultaneously doubles maintenance burden and defeats the purpose of the migration.
3. **Prefer explicit dependency version constraints in `pyproject.toml` over unpinned or loosely specified dependencies** because the migration is an opportunity to codify known-good version bounds and reduce future breakage.
4. **Prefer preserving existing dependency versions and constraints over upgrading them during this migration** because conflating dependency upgrades with format migration increases risk and obscures the source of any regressions.
5. **Prefer a compatible build backend (e.g., `setuptools`, `hatchling`, or `flit-core`) that is already in use or minimally invasive** because introducing an unfamiliar build system expands scope beyond the stated task.

---

## Constraints

- **Scope freeze:** This migration is strictly limited to dependency management format changes. No dependency version upgrades, no refactoring of application code, and no changes to CI/CD pipelines beyond what is required to consume `pyproject.toml`.
- **Timeline/Effort:** Moderate effort ceiling (specific person-days TODO — not provided in upgrade option). All work must fit within the "moderate" option envelope.
- **Technology mandates:**
  - Output must be a valid `pyproject.toml` conforming to PEP 621 (standardized project metadata).
  - The chosen build backend must support PEP 517/518.
  - TODO: Confirm minimum Python version to set in `requires-python` field.
  - TODO: Confirm whether a lock file tool (e.g., `pip-tools`, `poetry`, `uv`) is required or in scope.
- **No runtime changes:** Runtime version is currently unknown; `pyproject.toml` must not introduce runtime version constraints that did not previously exist.

---

## Quality Standards

- **Parity check:** Every dependency present in the original `requirements.txt`(s) must appear in `pyproject.toml` with an equivalent or stricter constraint. Verified by automated diff/audit script before merge.
- **Installation validation:** `pip install .` (or equivalent build-backend command) must succeed in a clean virtual environment with zero errors as a mandatory CI gate.
- **No orphaned files:** All `requirements.txt` files must be removed or explicitly replaced (e.g., a generated `requirements.txt` from `pip-tools` is acceptable only if documented as derived, not authoritative).
- **Code review:** Migration PR requires at least one reviewer to confirm dependency parity and `pyproject.toml` schema validity.
- **Documentation:** `README` or `CONTRIBUTING` must be updated to reflect the new install instructions before the PR is merged.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt `pyproject.toml` as the single dependency manifest | PEP 621 is the current Python packaging standard; `requirements.txt` is not a packaging specification and lacks metadata support | Accepted |
| ADR-002 | Preserve existing dependency versions during migration | Decouples format risk from version-upgrade risk; keeps the changeset reviewable and rollback straightforward | Accepted |
| ADR-003 | Build backend selection | TODO — must be decided based on existing project structure (setuptools vs. hatchling vs. flit-core) | Proposed |
| ADR-004 | Lock file strategy (e.g., `pip-tools` compile, `uv lock`) | TODO — depends on team workflow and whether reproducible installs are currently enforced | Proposed |