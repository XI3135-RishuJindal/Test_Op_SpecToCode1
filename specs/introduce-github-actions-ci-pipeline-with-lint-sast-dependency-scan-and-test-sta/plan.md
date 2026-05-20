# Plan: Introduce GitHub Actions CI Pipeline

## Overview

**Migration Strategy: Big-Bang (Greenfield Pipeline Introduction)**

Since no existing CI/CD pipeline is present in the repository, this is a net-new introduction rather than a migration. A big-bang approach is appropriate: the entire pipeline is authored and merged in a single pull request (or a small, tightly scoped sequence of PRs), immediately gating all subsequent commits.

A strangler-fig or parallel-run strategy is unnecessary here because there is no legacy pipeline to displace. The risk score is **medium** (upgrade urgency: medium) — the primary risks are false-positive gate failures blocking developer velocity and misconfigured secrets/permissions, both of which are mitigated by an initial "warn-only" posture for new lint and SAST rules before hardening to "fail-on-error."

Estimated total effort derives from the **moderate** option: approximately **5–8 person-days**.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Scaffold | Create `.github/workflows/` directory structure; add base CI workflow file with job skeletons; configure branch protection rule to require CI | Repository admin access; GitHub Actions enabled on repo | 0.5 days |
| 2 — Lint Stage | Add linter job(s) appropriate to detected language(s); configure linter config files; set warn-only initially | Phase 1 complete; linter config files committed | 1–1.5 days |
| 3 — SAST Stage | Integrate GitHub CodeQL (or equivalent SAST tool); configure `codeql-config.yml`; set warn-only initially | Phase 1 complete; CodeQL Actions available | 1–1.5 days |
| 4 — Dependency Scan Stage | Add dependency vulnerability scan job (e.g., Dependabot alerts + `dependency-review-action`, or OSV-Scanner); configure policy file | Phase 1 complete; dependency manifest present in repo | 1 day |
| 5 — Test Stage | Add test runner job; configure test result reporting and coverage upload | Phase 1 complete; test suite exists or is scaffolded | 1–1.5 days |
| 6 — Harden & Gate | Flip all stages from warn-only to fail-on-error; enforce branch protection; document pipeline in `CONTRIBUTING.md` | Phases 2–5 complete; team sign-off on baseline pass rate | 0.5–1 day |

**Total: ~5–7 days** (within the moderate 5–8 person-day envelope)

---

## Component Changes

### `.github/workflows/ci.yml` *(new file)*
- Top-level workflow triggered on `push` and `pull_request` to `main` (and any protected branches).
- Jobs: `lint`, `sast`, `dependency-scan`, `test` — each as an independent job with `needs:` dependencies where sequencing is required.
- Shared `permissions:` block scoped to least-privilege (`contents: read`, `security-events: write` for SAST).

### `.github/workflows/codeql.yml` *(new file, or merged into ci.yml)*
- Dedicated CodeQL analysis workflow (GitHub recommends a separate file for the CodeQL Action schedule trigger).
- Configures `languages:` array — **TODO: populate once language is confirmed from repository scan.**

### `.github/codeql/codeql-config.yml` *(new file)*
- Custom CodeQL configuration: query suites, path exclusions (e.g., `vendor/`, `node_modules/`, generated code).
- **TODO: specific paths depend on repository layout.**

### `.github/dependency-review-config.yml` *(new file, optional)*
- Policy file for `actions/dependency-review-action`: sets `fail-on-severity` threshold (recommended: `high`).

### `CONTRIBUTING.md` *(new or modified)*
- Documents CI pipeline stages, how to run checks locally, and how to interpret gate failures.

### Branch Protection Rules *(GitHub repository settings — not a file)*
- Require status checks: `lint`, `sast`, `dependency-scan`, `test` before merge to `main`.
- Require branches to be up to date before merging.

---

## Dependency Upgrade Plan

> **Note:** Language, runtime, and build tool are listed as **unknown** in the tech analysis. The table below covers the GitHub Actions action-dependencies (versioned Actions) that will be introduced. Tool-specific linter/scanner versions are marked TODO pending language identification.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `actions/checkout` | N/A (new) | `v4` | N/A | Use `v4` for Node 20 runner compatibility |
| `actions/upload-artifact` | N/A (new) | `v4` | N/A | Required for test result and SAST report upload |
| `github/codeql-action/init` | N/A (new) | `v3` | N/A | Pin to `v3`; `v2` is deprecated |
| `github/codeql-action/analyze` | N/A (new) | `v3` | N/A | Pair with `init` at same version |
| `actions/dependency-review-action` | N/A (new) | `v4` | N/A | Requires `pull_request` trigger; not available on `push` |
| Linter (language-specific) | N/A | **TODO** | **TODO** | Pending language confirmation |
| Test runner (language-specific) | N/A | **TODO** | **TODO** | Pending language confirmation |
| OSV-Scanner / Trivy (alt dep scan) | N/A | **TODO** | **TODO** | Alternative if `dependency-review-action` insufficient |

---

## Infrastructure Changes

**GitHub Actions Runner:**
- Uses GitHub-hosted runners (`ubuntu-latest`) for all jobs. No self-hosted runner infrastructure required unless the repository has network-restricted dependencies — **TODO: confirm with team.**
- `ubuntu-latest` currently maps to `ubuntu-24.04`; pin to `ubuntu-22.04` if stability over novelty is preferred.

**Secrets / Environment Variables:**
- No external secrets required for the initial pipeline (CodeQL and dependency-review-action use the built-in `GITHUB_TOKEN`).
- **TODO:** If a third-party SAST or registry scan tool is chosen, a repository secret will need to be provisioned in GitHub repository settings.

**Branch Protection (GitHub Settings):**
- Enable "Require status checks to pass before merging" for `main`.
- Enable "Require a pull request before merging."
- **TODO:** Confirm whether GitHub Enterprise or GitHub.com Free/Pro/Team — some branch protection features are tier-gated.

**Docker / Kubernetes / IaC:**
N/A — not applicable to this task. The CI pipeline runs on GitHub-hosted runners; no container image builds, Kubernetes manifests, or IaC changes are introduced by this task.

---

## Rollback Strategy

Each phase produces an independently revertable artifact (a workflow file or config file). Rollback is a standard Git revert or file deletion.

| Phase | Rollback Action |
|-------|----------------|
| Phase 1 — Scaffold | Delete `.github/workflows/ci.yml`; remove branch protection status check requirements via GitHub repository settings. |
| Phase 2 — Lint | Remove or comment out the `lint` job block in `ci.yml`; delete linter config file; remove `lint` from required status checks. |
| Phase 3 — SAST | Delete `.github/workflows/codeql.yml` and `.github/codeql/codeql-config.yml`; remove `sast` from required status checks. |
| Phase 4 — Dependency Scan | Remove the `dependency-scan` job block; delete `.github/dependency-review-config.yml`; remove from required status checks. |
| Phase 5 — Test | Remove the `test` job block; remove from required status checks. |
| Phase 6 — Harden | Revert `fail-on-error` flags back to warn-only in respective job configurations; adjust branch protection thresholds. |

> **Key principle:** Because all pipeline definitions are version-controlled files, any rollback is a `git revert <commit>` or PR revert, deployable in under 5 minutes.

---

## Testing Strategy

The CI pipeline itself must be validated before it gates production code.

### Unit / Syntax Validation
- **Tool:** `actionlint` — static analysis for GitHub Actions workflow YAML files.
- Run locally (`actionlint .github/workflows/*.yml`) and as a pre-merge check during Phase 1.
- **Coverage target:** Zero `actionlint` errors on all workflow files before Phase 6 hardening.

### Integration / Dry-Run Testing
- Open a draft pull request against `main` after each phase to observe live job execution in the GitHub Actions UI.
- Validate that each job: (a) triggers correctly, (b) produces expected pass/fail signals, (c) posts status checks to the PR.
- Use a synthetic "known-bad" branch (e.g., introduce a deliberate lint error, a known CVE in a test dependency) to confirm gates fire correctly.

### Regression
- After Phase 6 hardening, run the full pipeline against the last 5 merged commits (via manual `workflow_dispatch` trigger) to confirm no false-positive failures on known-good code.
- **TODO:** Define acceptable false-positive rate threshold with the team (recommended: 0 blocking false positives at launch).

### Performance / Duration Gate
- Each individual job should complete within **10 minutes**; total pipeline wall-clock time should not exceed **20 minutes**.
- If jobs exceed thresholds, apply caching strategies (e.g., `actions/cache` for package manager caches) — **TODO: specific cache keys depend on build tool.**

### CI Gates (enforced from Phase 6 onward)
| Gate | Condition |
|------|-----------|
| Lint | Exit code 0 required; zero errors |
| SAST | No new `high` or `critical` severity findings introduced by the PR |
| Dependency Scan | No `high` or `critical` vulnerabilities in newly added dependencies |
| Test | All tests pass; coverage must not decrease below established baseline (**TODO: set baseline in Phase 5**) |

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Workflow scaffold merged; branch protection enabled | Phase 1 | Day 1 | TODO |
| Lint job live and warn-only | Phase 2 | Day 2 | TODO |
| SAST job live and warn-only | Phase 3 | Day 3 | TODO |
| Dependency scan job live and warn-only | Phase 4 | Day 4 | TODO |
| Test job live; coverage baseline established | Phase 5 | Day 5–6 | TODO |
| All gates hardened to fail-on-error; `CONTRIBUTING.md` updated; pipeline announced to team | Phase 6 | Day 7–8 | TODO |

> Effort derived from the **moderate** upgrade option (5–8 person-days). Dates are relative to project kick-off day; absolute calendar dates to be assigned by the project owner.