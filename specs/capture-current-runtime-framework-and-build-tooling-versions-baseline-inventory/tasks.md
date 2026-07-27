## Prerequisites
- [ ] [XS] Obtain read access to the repository default branch in GitHub (repo settings)
- [ ] [XS] Obtain permission to read CI logs and job configuration in GitHub Actions (Actions tab)

## Phase 1 — Preparation
- [ ] [S] Identify and record runtime version signals by scanning repo root files (e.g., `README*`, `.tool-versions`, `.nvmrc`, `Dockerfile*`, `.github/workflows/*.yml`) in repository root
- [ ] [S] Identify and record build tooling by enumerating build config files (e.g., `pom.xml`, `build.gradle*`, `package.json`, `go.mod`, `Cargo.toml`, `pyproject.toml`, `requirements*.txt`, `Makefile`) in repository root
- [ ] [S] Capture CI-reported runtime and toolchain versions from workflow steps (e.g., `actions/setup-*`, container images) in `.github/workflows/*.yml`
- [ ] [S] Create baseline inventory document with current runtime/framework/build tool versions in `docs/modernization/baseline-inventory.md`

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
N/A — not applicable to this task

## Phase 4 — CI/CD & Infrastructure
N/A — not applicable to this task

## Phase 5 — Documentation & Rollout
- [ ] [XS] Add link to `docs/modernization/baseline-inventory.md` from `README.md` (or note “no README present” in the inventory doc)