## Prerequisites
- [ ] [XS] Confirm repository read access and ability to browse default branch in GitHub repository settings
- [ ] [XS] Install and configure Git CLI for documentation branch workflow in local environment

## Phase 1 — Preparation
- [ ] [XS] Create documentation-only branch for inventory work in git (e.g., `docs/build-test-inventory`) in local git repo
- [ ] [S] Inventory build entrypoints by listing build commands and scripts in `README.md` and/or `CONTRIBUTING.md` (capture exact commands as written)
- [ ] [S] Inventory test entrypoints by listing test commands and scripts in `README.md` and/or `CONTRIBUTING.md` (capture exact commands as written)
- [ ] [S] Inventory CI entrypoints by identifying build/test commands referenced in `.github/workflows/*.yml` (document each workflow file and the commands it runs)

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
N/A — not applicable to this task

## Phase 4 — CI/CD & Infrastructure
- [ ] [S] Inventory baseline runtime/framework versions by extracting any pinned versions referenced in `.github/workflows/*.yml` (document keys/fields and values exactly as present)
- [ ] [S] Inventory baseline runtime/framework versions by extracting any pinned versions referenced in `Dockerfile` / `docker-compose.yml` (if present) (document base images/tags and any version env vars exactly as present)

## Phase 5 — Documentation & Rollout
- [ ] [S] Document inventory results (build/test entrypoints + baseline runtime/framework versions) in `docs/modernization/build-test-entrypoints-and-baselines.md`
- [ ] [XS] Add links to the new inventory document in `README.md` (Documentation section) and/or `CONTRIBUTING.md` (Developer workflow section)
- [ ] [XS] Summarize findings and unknowns (explicitly note “unknown” where versions are not discoverable from repo) in `docs/modernization/build-test-entrypoints-and-baselines.md`
- [ ] [XS] Open PR with documentation-only changes and request review from code owners in `CODEOWNERS` (if present)