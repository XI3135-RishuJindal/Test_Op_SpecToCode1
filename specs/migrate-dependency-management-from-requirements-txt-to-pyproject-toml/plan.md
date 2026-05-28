# PLAN: Migrate Dependency Management from `requirements.txt` to `pyproject.toml`

## Overview

**Migration Strategy: Big-Bang (with preparatory validation gate)**

The migration from `requirements.txt` to `pyproject.toml` is a self-contained tooling change with no runtime behavior impact. A big-bang approach is appropriate because:

- The change is atomic: the project either uses `requirements.txt` or `pyproject.toml` — parallel-run adds no safety benefit for a file-format migration.
- Risk score is **medium** (per tech analysis), driven primarily by environment reproducibility concerns, not architectural complexity.
- The effort estimate is low-to-moderate; a strangler-fig or feature-flag strategy would introduce unnecessary overhead for what is fundamentally a build-tooling swap.
- Rollback is straightforward: the original `requirements.txt` files are preserved in version control until the migration is verified and signed off.

The migration will be executed in three sequential phases: audit & preparation, conversion & validation, and cleanup & enforcement.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Audit & Preparation | Inventory all `requirements*.txt` files, pin all transitive dependencies, choose a build backend (`setuptools`, `hatchling`, or `flit`), and establish a baseline lockfile or frozen environment for regression comparison. | None | ~1 person-day |
| 2 — Conversion & Validation | Author `pyproject.toml` with `[project]`, `[project.optional-dependencies]`, and `[build-system]` tables. Validate install in a clean virtual environment. Update CI pipeline to use the new file. | Phase 1 complete | ~1–2 person-days |
| 3 — Cleanup & Enforcement | Remove `requirements*.txt` files (or demote to generated artifacts). Add CI lint gate (e.g., `validate-pyproject`) to prevent regression. Update contributor documentation. | Phase 2 signed off | ~0.5 person-days |

> **Total estimated effort:** ~2.5–3.5 person-days (derived from the "moderate" upgrade option).

---

## Component Changes

### `requirements.txt` / `requirements*.txt`
- **What changes:** These files are the source of truth for dependencies today. After migration they are either deleted or regenerated as lock artifacts (e.g., via `pip-compile` outputting from `pyproject.toml`).
- **Files affected:** `requirements.txt` and any variants such as `requirements-dev.txt`, `requirements-test.txt`, `requirements-prod.txt`.
  - TODO: Confirm exact filenames by auditing the repository root and any subdirectories.

### `pyproject.toml` (new file)
- **What changes:** Created at the repository root. Must include at minimum:
  - `[build-system]` — specifies the build backend and its requirements.
  - `[project]` — includes `name`, `version`, `dependencies` (runtime deps from `requirements.txt`).
  - `[project.optional-dependencies]` — groups such as `dev`, `test`, `lint` (from `requirements-dev.txt` etc.).
- **Files affected:** `pyproject.toml` (net-new).

### CI/CD Pipeline Configuration
- **What changes:** Any pipeline step that runs `pip install -r requirements.txt` must be updated to `pip install .` (for runtime deps) or `pip install ".[dev,test]"` (for full dev installs).
- **Files affected:** TODO — pipeline file names not provided in context (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `tox.ini`, `Makefile`).

### `setup.py` / `setup.cfg` (if present)
- **What changes:** If either file exists, its `install_requires` and `extras_require` content must be consolidated into `pyproject.toml` and the files removed or reduced to a shim.
- **Files affected:** TODO — presence not confirmed in provided context.

### `tox.ini` / `Makefile` / developer scripts (if present)
- **What changes:** Any `deps = -r requirements.txt` references in `tox.ini` must be replaced with `deps = .[test]`. Makefile targets invoking `pip install -r` must be updated.
- **Files affected:** TODO — confirm presence in repository.

---

## Dependency Upgrade Plan

> **Note:** No specific dependency names or version numbers were provided in the tech analysis. The table below documents the **tooling** dependencies introduced by this migration.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `pip` | TODO — audit current pinned version | ≥ 21.3 required for full `pyproject.toml` editable install support | None for end users | Ensure CI and developer environments meet minimum version. |
| Build backend (e.g., `setuptools`) | TODO | TODO — match version confirmed during Phase 1 audit | N/A — new addition | Choose one backend (`setuptools`, `hatchling`, or `flit`) and pin it in `[build-system].requires`. |
| `validate-pyproject` (new, optional) | N/A | TODO — latest stable at time of Phase 1 | N/A — new addition | Used as a CI lint gate to validate `pyproject.toml` schema. |
| `pip-tools` (optional, for lockfile generation) | TODO | TODO | N/A | If a deterministic lockfile is required, `pip-compile` can generate `requirements.txt` from `pyproject.toml` as a derived artifact. |

> All version numbers for project runtime/test dependencies must be sourced from the existing `requirements*.txt` files during Phase 1 — they are not available in the provided context and must not be assumed.

---

## Infrastructure Changes

TODO — No infrastructure context (Docker base images, Kubernetes manifests, CI/CD platform, IaC tooling) was provided. Apply the following checklist once context is available:

- **Docker:** If a `Dockerfile` contains `COPY requirements.txt .` and `RUN pip install -r requirements.txt`, update to `COPY pyproject.toml .` and `RUN pip install .` (or `pip install ".[prod]"` if a production extras group is defined).
- **CI/CD:** Update install steps as described in Component Changes above. TODO — identify pipeline platform and file locations.
- **IaC:** TODO — no IaC context provided.

---

## Rollback Strategy

Each phase is independently reversible.

### Phase 1 Rollback
- No production change has been made. Discard the audit notes and branch. No action required in the repository.

### Phase 2 Rollback
1. Delete or revert `pyproject.toml` from the branch/commit.
2. Restore any CI pipeline changes to reference `requirements.txt` again.
3. Verify CI passes against the restored `requirements.txt` files.
4. The original `requirements*.txt` files must **not** be deleted during Phase 2 — they serve as the rollback artifact.

### Phase 3 Rollback
1. Restore `requirements*.txt` files from version control history (`git checkout <last-good-sha> -- requirements.txt`).
2. Revert the CI lint gate addition (remove `validate-pyproject` step).
3. Revert pipeline install commands back to `pip install -r requirements.txt`.
4. Remove or revert `pyproject.toml` if it was the sole dependency source.
5. Communicate rollback to all contributors so local environments are re-synced.

> **Key invariant:** Do not delete `requirements*.txt` files from the repository until Phase 3 is explicitly signed off and the rollback window has closed.

---

## Testing Strategy

### Unit / Static Validation
- **Tool:** `validate-pyproject` (CLI or pre-commit hook)
- **Gate:** Run on every PR that touches `pyproject.toml`. Fails if the TOML schema is invalid.
- **Coverage target:** 100% of `pyproject.toml` tables validated against PEP 517/518/621 schema.

### Integration — Clean Install Validation
- **Tool:** `pip install` in a fresh virtual environment (matrix: Python versions in use — TODO confirm versions from context).
- **Steps:**
  1. `python -m venv .venv-test && source .venv-test/bin/activate`
  2. `pip install .` — assert exit code 0.
  3. `pip install ".[dev,test]"` — assert exit code 0.
  4. `pip check` — assert no dependency conflicts.
- **CI gate:** Must pass before Phase 2 is merged.

### Regression — Dependency Equivalence Check
- **Approach:** Before deleting `requirements.txt`, generate a frozen environment from both the old and new configurations and diff the resolved package versions.
  1. From `requirements.txt`: `pip install -r requirements.txt && pip freeze > old-freeze.txt`
  2. From `pyproject.toml`: `pip install . && pip freeze > new-freeze.txt`
  3. `diff old-freeze.txt new-freeze.txt` — investigate any unexpected version changes.
- **Acceptance criterion:** No unintended version changes for any package that was explicitly pinned in the original `requirements.txt`.

### Performance
N/A — not applicable to this task. Dependency file format has no runtime performance impact.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Repository audit complete; all `requirements*.txt` files inventoried; build backend selected | Phase 1 | End of Day 1 | TODO |
| `pyproject.toml` authored and peer-reviewed | Phase 2 | End of Day 2 | TODO |
| CI pipeline updated and green on `pyproject.toml` install | Phase 2 | End of Day 3 | TODO |
| Dependency equivalence regression check passed | Phase 2 | End of Day 3 | TODO |
| `requirements*.txt` files removed; `validate-pyproject` gate enforced; docs updated | Phase 3 | End of Day 4 | TODO |
| Migration signed off and rollback window closed | Phase 3 | End of Day 4 | TODO |

> Effort derived from the "moderate" upgrade option (~2.5–3.5 person-days total). Timeline assumes a single engineer working on this task without blocking dependencies.