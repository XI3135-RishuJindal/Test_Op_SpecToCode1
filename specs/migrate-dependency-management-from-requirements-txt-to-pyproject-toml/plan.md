# PLAN: Migrate Dependency Management from `requirements.txt` to `pyproject.toml`

## Overview

**Migration Strategy: Big-Bang**

This migration replaces `requirements.txt`-based dependency management with a `pyproject.toml`-based approach in a single, coordinated changeset. A big-bang strategy is appropriate here because:

- The change is scoped entirely to build/packaging metadata — no runtime application logic is altered.
- The risk surface is low: the migration is reversible by restoring the original `requirements.txt` and removing `pyproject.toml`.
- A strangler-fig or parallel-run approach would add unnecessary complexity for what is fundamentally a file-level configuration change.
- The upgrade urgency is rated **medium**, and the effort is modest, making a clean cutover preferable to a prolonged dual-maintenance period.

The migration adopts `pyproject.toml` as the single source of truth for project metadata and dependencies, conforming to [PEP 517](https://peps.python.org/pep-0517/) and [PEP 621](https://peps.python.org/pep-0621/). A build backend (`setuptools`, `hatch`, or `flit`) will be selected based on existing project structure (see TODO in [Infrastructure Changes](#infrastructure-changes)).

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & inventory all `requirements*.txt` files; document all direct and pinned transitive dependencies | None | 0.5 person-days |
| 2 | Author `pyproject.toml` with `[project]` metadata, `[project.dependencies]`, and optional dependency groups; select and configure build backend | Phase 1 complete | 0.5 person-days |
| 3 | Validate installation from `pyproject.toml` in a clean virtual environment; resolve any version conflicts | Phase 2 complete | 0.5 person-days |
| 4 | Update CI/CD pipeline install steps to use `pip install .` or `pip install .[dev]` instead of `pip install -r requirements.txt` | Phase 3 complete | 0.25 person-days |
| 5 | Remove `requirements.txt` files (or retain as generated lock artifacts if needed); update project documentation and README | Phase 4 complete | 0.25 person-days |

**Total Estimated Effort: ~2 person-days**

---

## Component Changes

### `requirements.txt` → `pyproject.toml`

**Files affected:**
- `requirements.txt` — to be superseded (deleted or demoted to a generated lock file)
- `requirements-dev.txt` / `requirements-test.txt` — if present, to be mapped to optional dependency groups (e.g., `[project.optional-dependencies]` with keys `dev`, `test`)
- `setup.py` / `setup.cfg` — if present, metadata to be consolidated into `pyproject.toml` and these files removed or minimized
- `pyproject.toml` — to be created (or extended if already partially present)

**Structural changes:**

1. **Create `pyproject.toml`** with the following sections:
   - `[build-system]` — declares the build backend (e.g., `setuptools>=68`, `hatchling`, or `flit_core`; TODO: confirm based on existing project structure)
   - `[project]` — name, version, description, `requires-python`, `dependencies` (direct runtime deps from `requirements.txt`)
   - `[project.optional-dependencies]` — groups such as `dev`, `test`, `lint` sourced from any supplementary requirements files
   - `[tool.*]` — migrate any tool configuration currently in `setup.cfg`, `tox.ini`, or standalone config files (e.g., `[tool.pytest.ini_options]`, `[tool.mypy]`, `[tool.ruff]`) into `pyproject.toml`

2. **Dependency version constraints:**
   - Pinned versions in `requirements.txt` (e.g., `requests==2.31.0`) should be converted to minimum-compatible constraints (e.g., `requests>=2.31.0`) in `[project.dependencies]`, unless the project requires strict reproducibility.
   - If strict reproducibility is required, generate a `requirements.lock` or use a lock-file tool (e.g., `pip-compile`, `uv lock`) as a separate artifact — `pyproject.toml` holds the logical constraints, the lock file holds the pins.

3. **No application source code changes are required.**

> **TODO:** Identify all `requirements*.txt` files present in the repository root and subdirectories. Confirm whether `setup.py` or `setup.cfg` exists and must be consolidated.

---

## Dependency Upgrade Plan

> **Note:** The tech analysis did not provide specific dependency names or version numbers. The table below describes the *process* for each dependency category. Populate with actual package names and versions discovered during Phase 1 audit.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| *(runtime deps from `requirements.txt`)* | TODO — from audit | TODO — retain or relax pins | None expected | Move to `[project.dependencies]` in `pyproject.toml` |
| *(dev/test deps from `requirements-dev.txt`)* | TODO — from audit | TODO — retain or relax pins | None expected | Move to `[project.optional-dependencies.dev]` |
| Build backend (e.g., `setuptools`) | TODO | TODO | None expected | Add to `[build-system.requires]`; version per project needs |
| `pip` | TODO | `>=21.3` recommended | None | Required for `pyproject.toml`-native installs without `setup.py` |

> **TODO:** Re-populate this table with exact version strings after completing the Phase 1 dependency audit.

---

## Infrastructure Changes

### CI/CD Pipeline

The install step in CI must be updated to install from `pyproject.toml` rather than `requirements.txt`.

**Before:**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # if present
```

**After:**
```bash
pip install ".[dev]"
# or, if using uv:
uv sync --extra dev
```

- Update the relevant CI configuration file (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `tox.ini` — TODO: confirm CI platform from repository context).
- If `tox.ini` is present, update `deps` entries or migrate `tox` configuration into `[tool.tox]` inside `pyproject.toml`.

### Docker

> **TODO:** No Dockerfile was provided in context. If a `Dockerfile` exists that references `COPY requirements.txt` and `RUN pip install -r requirements.txt`, update those lines to:
> ```dockerfile
> COPY pyproject.toml .
> # Copy source tree or stub as needed for editable/non-editable install
> RUN pip install .
> ```

### IaC / Other

> **TODO:** Not derivable from provided context. Review any infrastructure scripts that reference `requirements.txt` by filename.

---

## Rollback Strategy

Each phase is independently reversible:

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 (Audit) | No changes made; nothing to roll back. |
| Phase 2 (Author `pyproject.toml`) | Delete the newly created `pyproject.toml` (or revert the commit). `requirements.txt` remains untouched. |
| Phase 3 (Validation) | Discard the test virtual environment. No production changes have been made. |
| Phase 4 (CI/CD update) | Revert the CI configuration file change to restore `pip install -r requirements.txt` install steps. |
| Phase 5 (Remove `requirements.txt`) | Restore `requirements.txt` from version control (`git checkout HEAD~1 -- requirements.txt`). Remove or revert `pyproject.toml` if necessary. |

**Full rollback:** `git revert` the merge commit that introduced `pyproject.toml` and removed `requirements.txt`. The project returns to its prior state with zero impact on runtime behavior.

---

## Testing Strategy

Because this migration touches only packaging metadata and not application logic, the test strategy is focused on **installation correctness** rather than functional regression.

### Test Pyramid

| Layer | What to Test | Tools | CI Gate |
|-------|-------------|-------|---------|
| **Unit** | `pyproject.toml` is valid TOML and passes schema validation | `validate-pyproject` (CLI tool) | Fail CI on parse/schema error |
| **Integration** | Clean `pip install .` succeeds in a fresh virtual environment; all declared entry points are importable | `pip`, `python -c "import <pkg>"`, `tox` | Fail CI if install exits non-zero |
| **Integration** | Optional dependency groups install cleanly: `pip install ".[dev]"`, `pip install ".[test]"` | `pip`, `tox` | Fail CI if install exits non-zero |
| **Regression** | Existing test suite passes after installing from `pyproject.toml` (no missing dependencies) | TODO — confirm test framework (e.g., `pytest`) | Fail CI if any previously passing test fails |
| **Performance** | N/A — dependency metadata change has no runtime performance impact | N/A | N/A |

### Recommended CI Validation Steps

```yaml
# Example (adapt to actual CI platform — TODO: confirm)
- name: Validate pyproject.toml schema
  run: pip install validate-pyproject && validate-pyproject pyproject.toml

- name: Install from pyproject.toml (runtime)
  run: pip install .

- name: Install from pyproject.toml (dev extras)
  run: pip install ".[dev]"

- name: Run existing test suite
  run: pytest  # TODO: replace with actual test command
```

**Coverage target:** No new coverage target is introduced by this task. The goal is zero regression — all tests that passed before the migration must pass after.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Dependency audit complete; all `requirements*.txt` files inventoried | Phase 1 | Day 1 (0.5 pd) | TODO |
| `pyproject.toml` authored and peer-reviewed | Phase 2 | Day 1–2 (1.0 pd) | TODO |
| Clean-environment install validated; conflicts resolved | Phase 3 | Day 2 (1.5 pd) | TODO |
| CI/CD pipeline updated and green | Phase 4 | Day 2 (1.75 pd) | TODO |
| `requirements.txt` removed; docs updated; PR merged | Phase 5 | Day 2 (2.0 pd) | TODO |

**Total calendar time:** ~2 days (sequential) or ~1 day (with parallel review).
**Total person-days:** ~2 (derived from moderate upgrade option estimate).