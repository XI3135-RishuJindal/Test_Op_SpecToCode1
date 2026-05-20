# PLAN: Integrate Bandit and pip-audit into GitHub Actions CI Pipeline

## Overview

**Migration Strategy: Feature-Flag Gated (Non-Breaking CI Addition)**

The integration of Bandit (static application security testing) and pip-audit (dependency vulnerability scanning) into the GitHub Actions CI pipeline is a purely additive change. No existing application code, runtime, or build tooling is modified.

The chosen approach is a **feature-flag gated rollout** using GitHub Actions' `continue-on-error` and branch-scoped workflow triggers:

1. Security scan jobs are introduced as non-blocking (`continue-on-error: true`) in the first phase to establish a baseline and surface existing findings without breaking the pipeline.
2. Once the finding backlog is triaged and resolved, the gate is hardened to blocking (`continue-on-error: false`) in the second phase.

**Justification:** The upgrade urgency is rated **medium** and the option is **moderate** effort. A big-bang approach that immediately fails the pipeline on all findings would likely block development work before a findings baseline is established. The two-phase gated approach manages that risk directly.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Baseline & Non-Blocking Integration | Add `security-scan.yml` workflow with Bandit and pip-audit jobs; run on all PRs and `main` pushes; `continue-on-error: true`; upload SARIF/JSON reports as artifacts; triage existing findings | GitHub Actions runner access; `bandit` and `pip-audit` installable via pip | 2–3 person-days |
| 2 — Harden to Blocking Gate | Remove `continue-on-error: true`; configure severity thresholds; add branch protection rule requiring the `security-scan` check to pass; document suppression/ignore process | Phase 1 complete; findings backlog resolved or suppressed with justification | 1–2 person-days |

> **Total estimated effort: 3–5 person-days** (derived from the moderate upgrade option).

---

## Component Changes

### GitHub Actions Workflow — new file

**File:** `.github/workflows/security-scan.yml`

- **What changes:** New workflow file created from scratch. No existing workflow files are modified in Phase 1.
- **Structure:**
  - Trigger: `on: [push, pull_request]` scoped to relevant branches.
  - Job `bandit-scan`: checks out code, sets up Python, installs `bandit`, runs scan, uploads JSON report artifact.
  - Job `pip-audit-scan`: checks out code, sets up Python, installs `pip-audit`, runs audit against `requirements*.txt` or `pyproject.toml`, uploads JSON report artifact.
- **APIs/flags modified:** None — additive only.

### Branch Protection Rules — configuration change

**Location:** GitHub repository Settings → Branches → Protection Rules for `main` (and any other protected branches).

- **Phase 1:** No change required (jobs are non-blocking).
- **Phase 2:** Add `security-scan / bandit-scan` and `security-scan / pip-audit-scan` as required status checks.

### Findings Suppression Configuration — new file (if needed)

**File:** `.bandit` or `pyproject.toml` (`[tool.bandit]` section)

- Used to document intentional suppressions with justification comments (`# nosec B<id> — reason`).
- `pip-audit` ignores managed via `--ignore-vuln <VULN-ID>` flags or a dedicated ignore file (format TBD based on pip-audit version in use).

---

## Dependency Upgrade Plan

> **Note:** The tech analysis did not provide current environment versions. Version targets below reflect the task requirement; pin to specific versions once the runtime environment is confirmed.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `bandit` | N/A (not currently installed in CI) | TODO — pin after confirming Python runtime version | N/A — new addition | Install via `pip install bandit`; configure via `.bandit` or `pyproject.toml [tool.bandit]` |
| `pip-audit` | N/A (not currently installed in CI) | TODO — pin after confirming Python runtime version | N/A — new addition | Install via `pip install pip-audit`; requires network access to OSV/PyPI Advisory DB from runner |

> **TODO:** Once the Python runtime version is confirmed from the repository's existing workflow files or `pyproject.toml`, pin exact versions (e.g., `bandit==X.Y.Z`, `pip-audit==X.Y.Z`) and record them here.

---

## Infrastructure Changes

### CI/CD Pipeline

- **New file:** `.github/workflows/security-scan.yml` (see Component Changes above).
- **Existing workflow files:** No modifications required in Phase 1. In Phase 2, if a monolithic workflow exists, the security jobs may optionally be merged into it — evaluate based on actual workflow structure (TODO: review existing `.github/workflows/` contents).
- **Runner:** TODO — confirm whether `ubuntu-latest` (GitHub-hosted) is available and sufficient, or whether a self-hosted runner is required.
- **Network access:** `pip-audit` queries the OSV vulnerability database. Confirm outbound HTTPS is permitted from the CI runner environment.

### Docker / Kubernetes / IaC

N/A — not applicable to this task. The change is confined to the CI pipeline configuration.

---

## Rollback Strategy

### Phase 1 Rollback

- **Action:** Delete or disable `.github/workflows/security-scan.yml`.
- **How:** Either delete the file via a PR, or set `on: workflow_dispatch` only to prevent automatic triggering.
- **Impact:** Zero impact on application code, deployments, or other CI jobs. Fully reversible in a single commit.

### Phase 2 Rollback

- **Step 1 — Unblock the pipeline immediately:** In GitHub repository Settings → Branches, remove `security-scan / bandit-scan` and `security-scan / pip-audit-scan` from required status checks. This unblocks PRs within seconds without any code change.
- **Step 2 — Revert gate hardening:** Re-add `continue-on-error: true` to both jobs in `.github/workflows/security-scan.yml` via a PR. Scans continue to run and report without blocking.
- **Each step is independently reversible** — Step 1 can be taken without Step 2 if the goal is only to unblock an urgent PR.

---

## Testing Strategy

### Unit / Smoke Tests for the Workflow Itself

- **Tool:** [`act`](https://github.com/nektos/act) — run GitHub Actions workflows locally before merging.
- **Gate:** Workflow YAML must parse and both jobs must execute to completion (exit 0 in Phase 1) on a local checkout before the PR introducing the workflow is merged.

### Integration Tests (Workflow Validation)

- **Method:** Open a test PR that intentionally contains a known Bandit finding (e.g., `subprocess.call` with `shell=True`) and a pinned dependency with a known CVE. Verify:
  - Bandit reports the finding in the artifact.
  - pip-audit reports the CVE in the artifact.
  - In Phase 1: PR is not blocked.
  - In Phase 2: PR is blocked until finding is resolved or suppressed.

### Regression Tests

- **Gate:** All pre-existing CI jobs must continue to pass after the workflow file is added. No existing job names or status check names are modified.
- **Verification:** Review GitHub Actions run summary after merging Phase 1 to confirm no unintended side effects.

### Performance / Runtime Budget

- **Target:** Both security scan jobs should complete in under **5 minutes** each on a standard GitHub-hosted runner.
- **If exceeded:** Scope Bandit scan to changed files only using `--targets` flag, or cache pip install steps using `actions/cache`.

### Coverage Targets

- **Bandit:** Scan entire repository source tree (all `.py` files). Minimum severity threshold for blocking (Phase 2): `MEDIUM` and above. Confidence threshold: `MEDIUM` and above. (TODO: adjust based on findings baseline from Phase 1.)
- **pip-audit:** Audit all dependency manifests present in the repository (`requirements.txt`, `requirements-dev.txt`, `pyproject.toml` — TODO: confirm actual filenames).

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Draft `security-scan.yml` with non-blocking Bandit and pip-audit jobs | Phase 1 | Day 2 | TODO |
| PR reviewed, merged to `main`; baseline findings report generated | Phase 1 | Day 3 | TODO |
| Findings backlog triaged; suppressions documented with justification | Phase 1 → 2 transition | Day 5 | TODO |
| Gate hardened to blocking; branch protection rules updated | Phase 2 | Day 6 | TODO |
| Post-hardening validation PR tested end-to-end | Phase 2 | Day 7 | TODO |

> **Total calendar estimate: ~5–7 days** at moderate effort, assuming a single engineer and no significant findings backlog. If the findings backlog is large, the Phase 1 → 2 transition milestone should be re-estimated after the baseline report is reviewed.