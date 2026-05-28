# PLAN: Migrate Dependency Management from `requirements.txt` to `pyproject.toml`

## Overview

**Migration Strategy: Big-Bang (with preparatory validation gate)**

The migration from `requirements.txt` to `pyproject.toml` is a self-contained tooling change with no runtime behavior impact. A big-bang approach is appropriate because:

- The change is atomic: the project either uses `requirements.txt` or `pyproject.toml` — parallel-run adds no safety benefit for a build tooling migration.
- Risk is low-to-medium: the application's runtime dependencies do not change, only how they are declared and resolved.
- Rollback is trivially reversible by restoring the original `requirements.txt` file, which must be retained until the migration is fully validated.
- The effort estimate is small (see Phases), making a phased strangler-fig approach unnecessary overhead.

The strategy is: audit → author `pyproject.toml` → validate in CI → cut over → archive `requirements.txt`.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Audit & Inventory | Enumerate all `requirements*.txt` files (e.g., `requirements.txt`, `requirements-dev.txt`, `requirements-test.txt`). Pin exact versions for every unpinned entry. Identify transitive vs. direct dependencies. | None | 0.5 person-days |
| 2 — Author `pyproject.toml` | Create `pyproject.toml` with `[project]` metadata, `[project.dependencies]`, and optional-dependency groups (e.g., `dev`, `test`). Choose and configure a build backend (`setuptools`, `hatchling`, or `flit_core`). | Phase 1 complete | 0.5 person-days |
| 3 — Validation & CI Integration | Install from `pyproject.toml` in a clean virtual environment. Run full test suite. Update CI pipeline to use `pip install -e ".[dev,test]"` (or equivalent). Confirm parity with old install. | Phase 2 complete | 0.5 person-days |
| 4 — Cut-over & Cleanup | Remove or archive `requirements*.txt`. Update all developer documentation (`README`, `CONTRIBUTING`). Merge to main branch. | Phase 3 passing in CI | 0.25 person-days |

> **Total estimated effort: ~1.75 person-days** (derived from the "moderate" option estimate for a low-complexity tooling migration).

---

## Component Changes

### `requirements.txt` (and variants)

- **What changes:** File(s) are deprecated and ultimately removed after cut-over.
- **Files affected:** `requirements.txt`, and any of `requirements-dev.txt`, `requirements-test.txt`, `requirements-prod.txt` present in the repository.
- **Action:** Contents are migrated into `pyproject.toml` dependency tables. Files are archived (e.g., moved to `archive/` or deleted) in Phase 4.

### `pyproject.toml` (new file)

- **What changes:** Created at the repository root.
- **Key configuration sections:**

```toml
[build-system]
requires = ["setuptools>=68", "wheel"]   # or hatchling / flit_core — TODO: confirm build backend
build-backend = "setuptools.build_meta"

[project]
name = "TODO: project-name"
version = "TODO: project-version"
requires-python = ">=TODO"              # derive from existing runtime
dependencies = [
    # TODO: populate from requirements.txt
]

[project.optional-dependencies]
dev = [
    # TODO: populate from requirements-dev.txt
]
test = [
    # TODO: populate from requirements-test.txt
]
```

- **APIs modified:** None — this is a metadata/tooling file only.

### CI Pipeline Configuration

- **What changes:** Install commands updated from `pip install -r requirements.txt` to `pip install -e ".[dev,test]"` (or `pip install .` for production installs).
- **Files affected:** TODO — CI configuration file path not provided in context (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `tox.ini`, `Makefile`).

### `README` / `CONTRIBUTING` / Developer Docs

- **What changes:** Installation instructions updated to reference `pyproject.toml`-based install.
- **Files affected:** TODO — specific doc file paths not provided in context.

---

## Dependency Upgrade Plan

> **Note:** No dependency version information was provided in the tech analysis. The table below defines the migration structure; all version values must be populated from the actual `requirements.txt` audit in Phase 1.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| *(all direct runtime deps)* | TODO — from `requirements.txt` | Same (no version changes in this migration) | None | Move to `[project.dependencies]` |
| *(all dev/lint/format deps)* | TODO — from `requirements-dev.txt` | Same | None | Move to `[project.optional-dependencies.dev]` |
| *(all test deps)* | TODO — from `requirements-test.txt` | Same | None | Move to `[project.optional-dependencies.test]` |
| `pip` | TODO | ≥23.0 recommended | None | Ensure CI uses a modern `pip` that fully supports `pyproject.toml` metadata |
| `setuptools` *(if chosen as backend)* | TODO | ≥68.0 | None | Required for full PEP 517/518/621 support |

> **Key principle:** This migration does **not** change any dependency versions. Version changes are out of scope and should be tracked separately to isolate risk.

---

## Infrastructure Changes

N/A — not applicable to this task.

> No Docker, Kubernetes, or IaC context was provided. If the project uses a Docker image with a `COPY requirements.txt` + `RUN pip install -r requirements.txt` pattern, the `Dockerfile` `RUN` instruction must be updated to `RUN pip install .` — but this is TODO pending confirmation of a `Dockerfile` in the repository.

---

## Rollback Strategy

Each phase is independently reversible:

| Phase | Rollback Action |
|-------|----------------|
| **Phase 1 — Audit** | No changes committed; nothing to roll back. |
| **Phase 2 — Author `pyproject.toml`** | Delete `pyproject.toml`. The `requirements*.txt` files remain untouched and the project is fully operational. |
| **Phase 3 — CI Integration** | Revert CI configuration changes (restore `pip install -r requirements.txt` commands). Delete or ignore `pyproject.toml`. All CI pipelines return to prior state. |
| **Phase 4 — Cut-over** | Restore `requirements*.txt` from version control history (`git checkout <pre-cutover-sha> -- requirements.txt`). Revert documentation changes. Delete `pyproject.toml`. |

> **Prerequisite for safe rollback:** Do **not** delete `requirements*.txt` from version control history at any point. In Phase 4, they may be removed from the working tree but the git history preserves them.

---

## Testing Strategy

The goal is to prove that installing from `pyproject.toml` produces an identical working environment to installing from `requirements.txt`.

### Unit / Smoke Tests
- **Tool:** Existing project test suite (TODO — framework not specified in context, e.g., `pytest`).
- **Gate:** 100% of previously passing tests must continue to pass after installing from `pyproject.toml`.
- **Command:** `pip install -e ".[dev,test]" && pytest` (or equivalent).

### Integration / Environment Parity Tests
- **Tool:** `pip check` — verifies no dependency conflicts exist in the resolved environment.
- **Tool:** `pipdeptree` or `pip list` — compare installed package list between old (`requirements.txt`) and new (`pyproject.toml`) installs to confirm no packages are missing or version-shifted.
- **Gate:** Zero `pip check` errors; package list diff shows no unintended changes.

### Regression Tests
- **Approach:** Run the full existing test suite in a clean virtual environment (no cache) using the new install method.
- **CI Gate:** The CI pipeline must be updated to run this clean-install validation before the Phase 4 cut-over merge is approved.

### Performance
N/A — not applicable to this task. Dependency resolution time is not a meaningful performance concern for this migration.

### CI Gates (summary)

```
1. pip install -e ".[dev,test]"   → must exit 0
2. pip check                       → must exit 0
3. pytest (full suite)             → must match prior pass rate
4. pip list diff vs. requirements  → must show no unintended version changes
```

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit of all `requirements*.txt` files complete; pinned inventory documented | Phase 1 | Day 1 (0.5 days in) | TODO |
| `pyproject.toml` authored and peer-reviewed | Phase 2 | Day 2 (1.0 days in) | TODO |
| CI pipeline updated; all gates passing on feature branch | Phase 3 | Day 2–3 (1.5 days in) | TODO |
| `requirements*.txt` archived; docs updated; merged to main | Phase 4 | Day 3 (1.75 days in) | TODO |

> All effort estimates are derived from the "moderate" upgrade option for a low-complexity tooling migration (~1.75 person-days total). Actual completion dates depend on team scheduling — populate the Owner column with responsible engineers before work begins.