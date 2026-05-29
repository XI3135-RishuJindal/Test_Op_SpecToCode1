# CONSTITUTION

## Project Identity

**Name:** pyproject.toml Migration  
**Purpose:** Introduce a `pyproject.toml` file to centralize dependency declaration and build configuration for the project.  
**High-Level Goal:** Replace or supplement any existing ad-hoc dependency/build files (e.g., `setup.py`, `setup.cfg`, `requirements.txt`) with a standards-compliant `pyproject.toml`, establishing a single source of truth for build metadata and dependencies per [PEP 517](https://peps.python.org/pep-0517/) / [PEP 621](https://peps.python.org/pep-0621/).

---

## Guiding Principles

1. **Prefer `pyproject.toml` (PEP 621) over `setup.py`/`setup.cfg` because** the latter formats are legacy, increasingly unsupported, and create ambiguity in dependency resolution tooling.
2. **Prefer a single canonical dependency list over scattered `requirements*.txt` files because** fragmentation causes drift between development, CI, and production environments.
3. **Prefer an explicit build backend declaration (e.g., `hatchling`, `setuptools`, or `flit`) over implicit defaults because** PEP 517 requires a declared backend for reproducible builds.
4. **Prefer pinned or bounded dependency ranges over unpinned versions because** unbounded dependencies introduce silent breakage risk during installs.
5. **Prefer optional dependency groups (e.g., `[project.optional-dependencies]`) over separate files for dev/test extras because** it keeps the toolchain unified and discoverable.

---

## Constraints

- **Scope Freeze:** This task is strictly limited to creating and validating `pyproject.toml`. Refactoring source code, CI pipelines, or deployment configuration is out of scope unless directly required for the file to be functional.
- **Effort Ceiling:** Moderate effort option — estimated work should not exceed what is required to produce a correct, validated `pyproject.toml`. No large-scale dependency upgrades are in scope.
- **TODO — Runtime/Language Version:** The target Python version range is not specified in the tech analysis. A minimum Python version constraint (`requires-python`) **must** be confirmed before the file is merged.
- **TODO — Build Backend:** The preferred build backend (e.g., `setuptools`, `hatchling`, `flit_core`) has not been specified. This must be decided and recorded in the Decision Log before implementation.
- **TODO — Existing Files:** It is unknown whether `setup.py`, `setup.cfg`, or `requirements.txt` files currently exist. Their disposition (keep, deprecate, or remove) must be determined during implementation.

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| Schema validity | `pyproject.toml` must pass validation via `validate-pyproject` (or equivalent) with zero errors |
| Installability | `pip install .` (and `pip install .[dev]` if extras exist) must succeed in a clean virtual environment |
| Dependency completeness | All runtime imports resolvable from declared dependencies — verified by running the existing test suite post-install |
| No duplicate declarations | If legacy files (`setup.cfg`, `requirements.txt`) are retained, they must not contradict `pyproject.toml` entries |
| Peer review | At least one reviewer must verify the file before merge |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Adopt `pyproject.toml` as the build/dependency manifest | Aligns with PEP 517/621 standards; reduces legacy tooling debt | Accepted |
| ADR-002 | Build backend selection | TODO — must be chosen based on existing project structure and team preference | Proposed |
| ADR-003 | Disposition of legacy dependency files | TODO — determine whether `setup.py`/`requirements.txt` are removed or kept as transitional artifacts | Proposed |