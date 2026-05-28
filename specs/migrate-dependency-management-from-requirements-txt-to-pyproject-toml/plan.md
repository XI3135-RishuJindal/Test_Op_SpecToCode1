# PLAN: Migrate Dependency Management from `requirements.txt` to `pyproject.toml`

## Overview

**Migration Strategy: Big-Bang (with preparatory validation gate)**

The migration from `requirements.txt` to `pyproject.toml` is a self-contained tooling change with no runtime behavior impact. Because the change affects only how dependencies are declared and resolved — not application logic — a big-bang replacement is appropriate and lower-risk than a strangler-fig approach, which would require maintaining two parallel dependency systems simultaneously.

The upgrade urgency is rated **medium**, and the effort is modest (see Phases). The primary risk is environment reproducibility: if pinned versions in `requirements.txt` are not faithfully carried over, downstream installs may resolve different transitive dependency versions. This is mitigated by a lock-file validation gate before the old files are removed.

No architectural unknowns block this migration. The scope is strictly the dependency manifest layer.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & inventory existing `requirements.txt` file(s) — identify all direct deps, pinned versions, extras, and any `-r` includes or environment markers | None | 0.5 person-days |
| 2 | Author `pyproject.toml` with `[project]` and `[project.optional-dependencies]` tables; configure chosen build backend (e.g., `hatchling`, `setuptools`, or `flit`) | Phase 1 complete | 0.5 person-days |
| 3 | Validate environment parity — install from `pyproject.toml` in a clean virtualenv and diff resolved packages against the `requirements.txt` baseline | Phase 2 complete | 0.5 person-days |
| 4 | Update CI/CD pipeline references from `pip install -r requirements.txt` to `pip install .` (or `pip install .[dev]`) | Phase 3 passing | 0.25 person-days |
| 5 | Remove legacy `requirements.txt` file(s) and update project documentation/README | Phase 4 passing | 0.25 person-days |

**Total estimated effort: ~2 person-days**

---

## Component Changes

> **Note:** Specific file names, class names, and config keys are not derivable from the provided code context. The entries below describe the canonical file-level changes for this migration pattern. Update paths to match the actual repository layout.

### `requirements.txt` → `pyproject.toml`

- **Files affected:**
  - `requirements.txt` *(to be removed in Phase 5)*
  - `requirements-dev.txt` / `requirements/dev.txt` *(if present — to be removed in Phase 5)*
  - `pyproject.toml` *(to be created in Phase 2)*
  - `setup.py` / `setup.cfg` *(if present — consolidate into `pyproject.toml` or deprecate)*

- **Structural change:**
  - Direct runtime dependencies move to the `[project] dependencies` list in `pyproject.toml`.
  - Development/test-only dependencies move to `[project.optional-dependencies]` under a key such as `dev` or `test`.
  - Environment markers (e.g., `; python_version < "3.11"`) are preserved inline per PEP 508 syntax.
  - Pinned versions (`==x.y.z`) are carried over as-is for reproducibility; consider relaxing to compatible-release (`~=`) bounds as a follow-on task.

- **API / interface changes:** None — this change is invisible to application code.

### CI/CD Pipeline Configuration

- **Files affected:** TODO — pipeline config file name(s) not provided in context (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`, `tox.ini`, `Makefile`).
- **Change:** Replace all invocations of `pip install -r requirements.txt` with `pip install .` for runtime deps and `pip install .[dev]` (or equivalent extras key) for development deps.

### `README` / Developer Documentation

- **Files affected:** TODO — documentation file name(s) not provided in context.
- **Change:** Update "Getting Started" / "Installation" instructions to reflect `pip install .` workflow.

---

## Dependency Upgrade Plan

> **Note:** No specific dependency names or version numbers were provided in the tech analysis. The table below documents the **tooling** dependencies introduced by this migration. Application dependency versions must be sourced directly from the existing `requirements.txt` during Phase 1 — do not infer from training data.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `pip` | TODO (check `pip --version`) | ≥ 21.3 required | None for this task | PEP 660 editable installs require pip ≥ 21.3; upgrade if below this floor |
| Build backend (e.g., `hatchling`, `setuptools`, `flit_core`) | N/A — not currently declared | TODO — select one | N/A | Add to `[build-system] requires` in `pyproject.toml`; `setuptools>=61` supports full `pyproject.toml` without `setup.cfg` |
| Application runtime deps | TODO — from `requirements.txt` | Unchanged (carry over as-is) | None | Preserve exact pins from `requirements.txt` in Phase 2; version relaxation is out of scope |
| Application dev/test deps | TODO — from `requirements-dev.txt` | Unchanged (carry over as-is) | None | Map to `[project.optional-dependencies].dev` or `.test` |

---

## Infrastructure Changes

TODO — No CI/CD pipeline configuration, Docker base image definitions, Kubernetes manifests, or IaC files were provided in the context. Once those files are identified, apply the following targeted changes:

- **Docker:** If a `Dockerfile` contains `COPY requirements.txt .` + `RUN pip install -r requirements.txt`, replace with `COPY pyproject.toml .` + `RUN pip install .` (ensure `COPY` also includes any `src/` layout or `__init__` needed for the install to resolve).
- **CI/CD:** Replace `pip install -r requirements.txt` commands with `pip install .[dev]` (or split `pip install .` for runtime-only jobs). Update any cache keys that hash `requirements.txt` to hash `pyproject.toml` instead.
- **IaC / environment provisioning:** TODO — not derivable from context.

---

## Rollback Strategy

Each phase is independently reversible because `requirements.txt` is not deleted until Phase 5.

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 (audit) | No changes made to tracked files; nothing to revert. |
| Phase 2 (author `pyproject.toml`) | Delete `pyproject.toml` (and any `pyproject.toml`-related `setup.cfg` edits). The existing `requirements.txt` remains untouched and fully functional. |
| Phase 3 (validation) | If parity check fails, do not proceed to Phase 4. Correct `pyproject.toml` and re-run validation. No rollback needed — `requirements.txt` is still the active manifest. |
| Phase 4 (CI/CD update) | Revert the pipeline config commit (e.g., `git revert <sha>`). CI will resume using `pip install -r requirements.txt`. |
| Phase 5 (remove legacy files) | Restore `requirements.txt` from version control (`git checkout <sha> -- requirements.txt`). Re-add the `pip install -r requirements.txt` step to CI if Phase 4 was also reverted. |

**Key safeguard:** Do not merge the Phase 5 deletion PR until at least one full CI pipeline run has passed using only `pyproject.toml` as the dependency source.

---

## Testing Strategy

### Test Pyramid

| Layer | What to Verify | Tool / Method | CI Gate |
|-------|---------------|---------------|---------|
| **Unit** | Application unit tests pass unchanged after install from `pyproject.toml` | TODO — existing test runner (pytest, unittest) | Must pass; no new tests required for this task |
| **Integration** | All imports resolve; no `ModuleNotFoundError` at startup | `python -c "import <entrypoint_module>"` smoke test in CI | Must pass before Phase 4 merge |
| **Regression (env parity)** | Resolved package set from `pyproject.toml` install matches `requirements.txt` install | `pip freeze` diff in a clean virtualenv (Phase 3 gate) | Diff must be empty (or explicitly approved) before Phase 4 |
| **Performance** | N/A — no runtime behavior change | N/A | N/A |

### Concrete Validation Steps (Phase 3)

```bash
# Baseline: capture resolved env from requirements.txt
python -m venv .venv-baseline
.venv-baseline/bin/pip install -r requirements.txt
.venv-baseline/bin/pip freeze > baseline.txt

# Candidate: capture resolved env from pyproject.toml
python -m venv .venv-candidate
.venv-candidate/bin/pip install .
.venv-candidate/bin/pip freeze > candidate.txt

# Diff — output must be empty or reviewed
diff baseline.txt candidate.txt
```

### Coverage Target

No coverage target change is introduced by this task. Maintain whatever coverage threshold the project currently enforces.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Dependency inventory complete | Phase 1 | Day 1 (end of day) | TODO |
| `pyproject.toml` authored and peer-reviewed | Phase 2 | Day 2 (midday) | TODO |
| Environment parity validated (diff clean) | Phase 3 | Day 2 (end of day) | TODO |
| CI/CD pipeline updated and green | Phase 4 | Day 3 (midday) | TODO |
| Legacy `requirements.txt` removed; docs updated | Phase 5 | Day 3 (end of day) | TODO |

**Total calendar time: ~3 days** (assuming single-engineer execution with normal review cycles; parallelism or review delays may shift Phase 4–5 by 1 day).