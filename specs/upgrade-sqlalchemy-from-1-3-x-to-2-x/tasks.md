## Prerequisites

- [ ] [XS] Ensure Python 3.7+ is present in development and CI environments
- [ ] [XS] Verify access to the code repository and branch permissions
- [ ] [XS] Confirm presence of SQLAlchemy 1.3.x in requirements.txt or setup.py

## Phase 1 — Preparation

- [ ] [S] Create feature branch `upgrade/sqlalchemy-2.x` from latest main
- [ ] [XS] Audit requirements.txt or setup.py for direct/indirect SQLAlchemy pins
- [ ] [S] Capture test baseline by running `pytest` and archiving test reports

## Phase 2 — Core Upgrade

- [ ] [XS] Upgrade SQLAlchemy from 1.3.x to latest 2.x in requirements.txt or setup.py
- [ ] [M] Refactor codebase to use new SQLAlchemy 2.x Core and ORM APIs, including session and engine usage in all affected modules and files  
- [ ] [M] Update all relational query/filter syntaxes in repository/data access classes for SQLAlchemy 2.x compatibility

## Phase 3 — Testing & Validation

- [ ] [S] Re-run `pytest` on upgrade branch and collect test results
- [ ] [S] Compare test failure/success rates to baseline and identify regressions
- [ ] [S] Verify code coverage for all affected modules

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update CI pipeline to use Python 3.7+ and SQLAlchemy 2.x in .github/workflows/ci.yml if Python or dependency versions are hardcoded

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update CHANGELOG.md to document SQLAlchemy 2.x upgrade  
- [ ] [XS] Review and update any runbook instructions mentioning SQLAlchemy usage  
- [ ] [S] Monitor error rates post-deploy using existing application monitoring for SQLAlchemy-related exceptions

---

Sections not applicable:

- Build tool upgrades: N/A — not applicable to this task
- Docker image or containerization: N/A — not applicable to this task (not cited in analysis)
- Infrastructure as Code: N/A — not applicable to this task