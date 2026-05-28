# CONSTITUTION
## Dependency Management Migration: requirements.txt → pyproject.toml

---

## Project Identity

**Name:** Dependency Management Modernization
**Purpose:** Migrate the project's Python dependency management from legacy `requirements.txt` files to the standardized `pyproject.toml` format (PEP 517/518/621).
**High-Level Goal:** Establish a single, authoritative source of truth for project metadata and dependencies, replacing fragmented `requirements.txt` files with a standards-compliant `pyproject.toml` configuration.

---

## Guiding Principles

1. **Prefer `pyproject.toml` over `requirements.txt` for all dependency declarations** because `requirements.txt` is a non-standard, tooling-specific format that lacks metadata, version constraints expressiveness, and build system integration.
2. **Prefer a single `pyproject.toml` over multiple requirements files** because fragmented files (e.g., `requirements-dev.txt`, `requirements-test.txt`) create drift and ambiguity about the canonical dependency set.
3. **Prefer explicit dependency groups (e.g., `[project.optional-dependencies]`) over flat lists** because separating runtime, dev, and test dependencies reduces production surface area and clarifies intent.
4. **Prefer preserving existing pinned versions during migration over re-resolving them** because uncontrolled version changes are out of scope and introduce regression risk beyond this task's mandate.
5. **Prefer a build backend already compatible with `pyproject.toml`** (e.g., `setuptools`, `hatch`, `flit`) over introducing a new toolchain, because minimizing toolchain churn is consistent with a moderate-effort migration.

---

## Constraints

- **Effort ceiling:** Moderate option — migration must remain a bounded, low-risk task. No architectural changes, no dependency upgrades, and no runtime changes are in scope.
- **Scope freeze:** Only dependency declaration and metadata are in scope. Refactoring application code, upgrading dependency versions, or changing CI/CD pipelines beyond what is necessary to consume `pyproject.toml` is explicitly out of scope.
- **Technology mandate:** The output artifact must be a valid `pyproject.toml` conforming to PEP 621. The chosen build backend must support PEP 517.
- **Backward compatibility:** All dependencies present in the existing `requirements.txt` file(s) must be represented in `pyproject.toml` with no silent omissions.
- **TODO:** Runtime version and build tool are unknown — the specific `[build-system]` backend selection must be confirmed before implementation begins.
- **TODO:** Whether a lock file tool (e.g., `pip-tools`, `poetry`, `uv`) is required alongside `pyproject.toml` is not specified and must be decided.

---

## Quality Standards

- **Completeness check:** A diff between all packages listed in the original `requirements.txt` file(s) and the resolved dependencies from `pyproject.toml` must show zero omissions before the migration is considered done.
- **Validation gate:** `pyproject.toml` must pass schema validation (e.g., `validate-pyproject` or equivalent) with zero errors before merge.
- **Install verification:** A clean virtual environment install using only `pyproject.toml` (e.g., `pip install .` and `pip install .[dev]`) must succeed with no errors as a mandatory CI gate.
- **Review requirement:** At least one peer review is required on the final `pyproject.toml` to verify dependency group correctness and no version drift.
- **Documentation:** The project README or a `CONTRIBUTING.md` must be updated to replace any `requirements.txt`-based setup instructions with `pyproject.toml`-based equivalents before the task is closed.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Adopt `pyproject.toml` as the sole dependency manifest | PEP 621 standardization; eliminates `requirements.txt` fragmentation | Accepted |
| ADR-002 | Preserve existing dependency versions during migration | Prevents unintended regressions; version upgrades are out of scope for this task | Accepted |
| ADR-003 | Build backend selection deferred pending runtime confirmation | Runtime and build tool are listed as unknown in tech analysis | Proposed |
| ADR-004 | Lock file strategy to be determined separately | Not specified in upgrade option; must not block migration but should be decided before rollout | Proposed |