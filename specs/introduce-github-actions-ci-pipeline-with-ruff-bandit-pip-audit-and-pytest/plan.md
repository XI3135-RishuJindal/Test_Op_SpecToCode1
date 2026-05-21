# PLAN: Introduce GitHub Actions CI Pipeline

> Implements the modernization goal described in `spec.md`: add a GitHub Actions CI pipeline running ruff, Bandit, pip-audit, and pytest.

---

## Overview

**Strategy: Big-Bang (single-phase delivery)**

A new CI pipeline has no existing system to migrate away from — there is nothing to strangle, no parallel run required, and no feature flag needed. The entire pipeline is introduced as a net-new `.github/workflows/` configuration file. Because the change is additive and does not touch application code, risk is low. The moderate effort estimate supports delivering this in one focused phase rather than spreading it across multiple increments.

The pipeline will enforce four quality gates in order:

1. **ruff** — fast Python linting and style enforcement
2. **Bandit** — static security analysis
3. **pip-audit** — dependency vulnerability scanning
4. **pytest** — automated test execution

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Scaffold `.github/workflows/ci.yml`; configure ruff, Bandit, pip-audit, and pytest jobs; wire up CI triggers and status checks | GitHub repository with Actions enabled; `requirements.txt` or `pyproject.toml` present in repo | 2–3 person-days |

> **Note:** Effort is derived from the "moderate" upgrade option. Exact person-day bounds were not provided in the option detail; 2–3 days reflects a moderate estimate for a self-contained CI configuration task with no application-code changes.

---

## Component Changes

### `.github/workflows/ci.yml` *(new file)*

- **What changes:** Created from scratch. Defines the full CI workflow.
- **Triggers:** `push` to all branches; `pull_request` targeting the default branch.
- **Jobs:**

| Job ID | Tool | Key config |
|--------|------|-----------|
| `lint` | ruff | `ruff check .` — fail on any violation |
| `security` | Bandit | `bandit -r . -ll` — report medium-and-above severity |
| `audit` | pip-audit | `pip-audit` — fail on any known CVE |
| `test` | pytest | `pytest --tb=short -q` — fail on any test failure |

- **Job ordering:** `lint` and `security` run in parallel; `audit` runs in parallel with both; `test` runs after `lint` passes (fast feedback loop — no point running tests against unlinted code). Exact dependency graph is configurable and should be agreed with the team.
- **Python version matrix:** TODO — confirm target Python version(s) from project metadata (`pyproject.toml` / `setup.cfg` / `runtime.txt`).

### `pyproject.toml` or `ruff.toml` *(new or modified)*

- **What changes:** ruff configuration block added (or created) to define `line-length`, `select`/`ignore` rule sets, and `target-version`.
- **Files affected:** `pyproject.toml` (preferred, under `[tool.ruff]`) or standalone `ruff.toml`.
- **Key config keys:** `line-length`, `select`, `ignore`, `target-version`.

### `pyproject.toml` or `.bandit` *(new or modified)*

- **What changes:** Bandit configuration to set severity/confidence thresholds and any project-specific skips.
- **Files affected:** `pyproject.toml` (under `[tool.bandit]`) or `.bandit` ini file.
- **Key config keys:** `skips`, `exclude_dirs`, `level` (`-ll` flag for medium+).

### `requirements-dev.txt` or `pyproject.toml` dev dependencies *(modified)*

- **What changes:** CI tool dependencies pinned and added to the development/CI dependency group so the workflow `pip install` step is reproducible.
- **Packages added:** `ruff`, `bandit[toml]`, `pip-audit`, `pytest` (plus any existing test dependencies already in the repo).

---

## Dependency Upgrade Plan

> **Note:** The tech analysis did not supply current or target version numbers for this project. Versions below are marked TODO pending inspection of the repository's existing dependency files.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| ruff | TODO — not present | TODO — latest stable | N/A (new addition) | Add to dev dependencies; create `[tool.ruff]` config block |
| bandit | TODO — not present | TODO — latest stable | N/A (new addition) | Use `bandit[toml]` extra for `pyproject.toml` config support |
| pip-audit | TODO — not present | TODO — latest stable | N/A (new addition) | Requires pip ≥ 21.2; verify runner pip version |
| pytest | TODO — may already be present | TODO — latest stable | N/A (new or upgrade) | If already present, confirm version is compatible with existing test suite before pinning |

> All version numbers must be confirmed from the repository's `requirements*.txt`, `pyproject.toml`, or `setup.cfg` before finalising this table.

---

## Infrastructure Changes

### GitHub Actions Runner

- **OS:** `ubuntu-latest` (GitHub-hosted runner) — sufficient for all four tools; no self-hosted runner required unless the project has network-restricted pip-audit scanning needs (TODO: confirm with team).
- **Python setup:** `actions/setup-python` action with version pinned to project's target Python (TODO: confirm version).
- **Caching:** `actions/cache` on `~/.cache/pip` keyed on the hash of the dependency file (`requirements*.txt` or `pyproject.toml`) to speed up repeated runs.

### Branch Protection Rules *(recommended, not automated by this plan)*

- TODO: Enable "Require status checks to pass before merging" on the default branch, selecting the `lint`, `security`, `audit`, and `test` job names as required checks. This must be configured manually in GitHub repository settings or via Terraform/GitHub provider IaC if present (TODO: check if IaC exists in repo).

### Docker / Kubernetes / IaC

N/A — not applicable to this task. No container builds or Kubernetes manifests are introduced by a CI linting/testing pipeline.

---

## Rollback Strategy

Because this change is purely additive (new files, no application code modified), rollback is straightforward at every step.

| Step | Rollback Action |
|------|----------------|
| 1. `ci.yml` merged but pipeline is broken/blocking PRs | Delete or rename `.github/workflows/ci.yml` on the default branch via a revert commit; pipeline stops running immediately |
| 2. ruff config causes false-positive failures | Remove or loosen `select` rules in `[tool.ruff]` config; push fix commit |
| 3. Bandit flags acceptable patterns | Add specific test IDs to `skips` list in Bandit config; push fix commit |
| 4. pip-audit blocks on a false-positive or unfixable CVE | Add a `pip-audit --ignore-vuln <VULN-ID>` flag with a documented justification comment in `ci.yml` |
| 5. pytest failures introduced by new test discovery | Scope pytest to existing passing directories via `testpaths` in `pyproject.toml` |
| 6. Branch protection rules block all merges | Disable required status checks in GitHub repository settings (Settings → Branches → Edit rule) |

Each step is independently reversible without affecting the others.

---

## Testing Strategy

> The CI pipeline *is* the testing infrastructure for this task. The strategy below covers validating the pipeline itself.

| Layer | What to test | Tool / Method | Gate |
|-------|-------------|---------------|------|
| **Unit** | Individual tool invocations succeed on a known-good file | Run each tool locally against a fixture file before committing `ci.yml` | Local pre-commit check |
| **Integration** | Full workflow runs end-to-end on a feature branch | Open a draft PR with the `ci.yml` change; observe all four jobs pass | All jobs green before merging |
| **Regression** | Pipeline does not break on subsequent unrelated PRs | Monitor first 3–5 PRs after merge for unexpected failures | No new failures introduced |
| **Performance** | Total CI wall-clock time is acceptable | Observe GitHub Actions run duration; target < 5 minutes for the full pipeline | TODO: set hard limit once baseline is measured |

**Coverage target for pytest:** TODO — establish baseline coverage on first run using `pytest --cov` and `coverage.xml`; set a minimum threshold (e.g., 80%) as a follow-on task once the pipeline is stable.

**CI gate policy:** All four jobs must pass (exit code 0) for a workflow run to be considered successful. No job may be marked `continue-on-error: true` in the initial configuration without explicit documented justification.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Confirm Python version and existing dev dependencies | 1 | Day 1 | TODO |
| Draft `.github/workflows/ci.yml` and tool configs | 1 | Day 1–2 | TODO |
| Open draft PR; iterate until all four jobs pass | 1 | Day 2–3 | TODO |
| Enable branch protection required status checks | 1 | Day 3 | TODO |
| Merge to default branch; monitor first live PRs | 1 | Day 3 | TODO |

> Timeline is derived from the moderate effort estimate (2–3 person-days). Exact calendar dates are TODO pending team scheduling.