## Prerequisites
- [ ] [XS] Obtain GitHub repository URL/ZIP download link/local filesystem path from stakeholders in project intake notes
- [ ] [XS] Obtain required credentials (GitHub org membership, SSO, PAT/SSH key) and confirm access level (read vs write) in GitHub access request thread/ticket
- [ ] [XS] Install Git CLI (version N/A — not provided in tech analysis) on the workstation used for validation

## Phase 1 — Preparation
- [ ] [XS] Clone repository from provided GitHub URL using `git clone` and capture result in terminal log (local shell history)
- [ ] [XS] Download and extract provided source ZIP and verify it contains a valid repository structure in extracted directory (presence of `.git` or expected top-level files)
- [ ] [XS] Validate repository integrity by running `git status` and `git log -n 1` in repo root directory
- [ ] [XS] Validate remote connectivity and permissions by running `git remote -v` and `git ls-remote --heads origin` in repo root directory
- [ ] [S] Identify and record default branch name by running `git remote show origin` in repo root directory
- [ ] [S] Record commit SHA used for all future work by saving `git rev-parse HEAD` output in `ACCESS_VALIDATION.md` at repo root
- [ ] [S] Create `ACCESS_VALIDATION.md` in repo root documenting source access method (URL/ZIP/path), date/time, and validation commands executed

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
N/A — not applicable to this task

## Phase 4 — CI/CD & Infrastructure
N/A — not applicable to this task

## Phase 5 — Documentation & Rollout
- [ ] [XS] Add/confirm `.gitignore` does not contain sensitive local artifacts created during access validation (no changes if not needed) in `.gitignore` at repo root
- [ ] [XS] Confirm no secrets or credentials were added to the working tree by reviewing `git diff --stat` and `git status` in repo root directory