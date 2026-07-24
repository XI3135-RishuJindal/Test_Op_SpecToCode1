## Prerequisites

- [ ] [XS] Confirm existing production deployment process and documentation in `docs/` (or equivalent) to identify current implicit change steps
- [ ] [XS] Identify and list current production approvers and on-call roles in `docs/ops/OWNERS.md` (or create file if missing)
- [ ] [XS] Verify write access to repository documentation paths (`README.md`, `docs/`, `docs/ops/`) for adding the checklist
- [ ] [XS] Align on “lightweight” scope of the checklist with engineering and operations leads in `docs/ops/change-management-scope.md`

## Phase 1 — Preparation

- [ ] [S] Inventory existing checklists or runbooks in `docs/ops/` (e.g., `release-runbook.md`, `incident-response.md`) and document overlaps in `docs/ops/change-management-review.md`
- [ ] [S] Capture current production change examples (last 3–5 releases) from `CHANGELOG.md` and deployment tickets into `docs/ops/change-examples.md`
- [ ] [XS] Define target audiences and required usage points (pre-deploy, deploy, post-deploy) in `docs/ops/change-checklist-requirements.md`

## Phase 2 — Core Upgrade

- [ ] [M] Draft a concise production change-management checklist in `docs/ops/production-change-checklist.md` covering pre-change, execution, and post-change steps
- [ ] [S] Integrate risk classification (e.g., low/medium/high impact) into `docs/ops/production-change-checklist.md` with clear criteria
- [ ] [S] Add rollback and validation requirements (e.g., health checks, metrics, smoke tests) to `docs/ops/production-change-checklist.md`
- [ ] [XS] Add explicit ownership and approval steps (who must review/approve which changes) to `docs/ops/production-change-checklist.md`
- [ ] [XS] Add a minimal change record template (metadata: change ID, owner, risk level, rollback plan, validation steps) to `docs/ops/production-change-checklist.md`
- [ ] [S] Create a one-page summary section in `README.md` linking to `docs/ops/production-change-checklist.md` for easy discovery

## Phase 3 — Testing & Validation

- [ ] [S] Pilot the checklist on a non-critical production change and record findings in `docs/ops/production-change-checklist-feedback.md`
- [ ] [S] Refine `docs/ops/production-change-checklist.md` based on pilot feedback to remove unnecessary steps and clarify ambiguous items
- [ ] [XS] Validate that the checklist can be completed in under 10 minutes for a standard low-risk change and document timing in `docs/ops/production-change-checklist-feedback.md`

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add a manual confirmation step in the primary deployment workflow (e.g., `.github/workflows/deploy-prod.yml` or equivalent) to reference `docs/ops/production-change-checklist.md` before production deployment
- [ ] [S] Add a required checklist confirmation item to the deployment request template in `.github/ISSUE_TEMPLATE/deployment-request.md` (or equivalent)
- [ ] [XS] Add a link to `docs/ops/production-change-checklist.md` in any existing release pipeline documentation file `docs/ops/release-runbook.md`

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add an entry to `CHANGELOG.md` describing the introduction of `docs/ops/production-change-checklist.md` and its intended usage
- [ ] [S] Create a short onboarding guide for engineers in `docs/ops/production-change-usage.md` describing when and how to apply the checklist
- [ ] [S] Present the new checklist to the team and capture agreed adoption rules (e.g., which change types must use it) in `docs/ops/production-change-governance.md`
- [ ] [S] Define and document metrics to track adherence (e.g., checklist referenced in deployment issues) in `docs/ops/production-change-metrics.md`
- [ ] [S] Schedule a 4–6 week post-rollout review and document outcomes and proposed adjustments in `docs/ops/production-change-retro.md`