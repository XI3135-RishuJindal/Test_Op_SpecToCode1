## Prerequisites

- [ ] [S] Confirm existing Python version is compatible with SQLAlchemy 2.x in requirements.txt or Pipfile
- [ ] [XS] Ensure write access to repository and branch protection rules allow pushes for upgrade branches

## Phase 1 — Preparation

- [ ] [XS] Create upgrade branch `upgrade/sqlalchemy-2x` from latest `main`
- [ ] [S] Capture test baseline by running and archiving outputs of all existing tests (e.g., `pytest` test suite)
- [ ] [XS] Audit current SQLAlchemy usage by searching for `sqlalchemy` imports and ORM usage in codebase

## Phase 2 — Core Upgrade

- [ ] [XS] Upgrade SQLAlchemy version from `1.3.x` to latest `2.x` in requirements.txt or Pipfile
- [ ] [S] Update all `session.execute()` and engine execution usage to new SQLAlchemy 2.x API in affected modules (list specific files after audit)
- [ ] [M] Refactor ORM queries to use SQLAlchemy 2.x style and remove deprecated patterns in all ORM-mapping files (e.g., in models.py and DAOs)
- [ ] [S] Replace or update `Query.get()` usages to `Session.get()` as per the 2.x API in model access classes
- [ ] [M] Update all metadata reflection and table creation logic for new declarative and reflection syntax in model definition files
- [ ] [S] Refactor transaction, commit, and rollback logic to match SQLAlchemy 2.x’s context manager requirements in affected modules

## Phase 3 — Testing & Validation

- [ ] [XS] Run full automated test suite and capture current results (pytest or equivalent)
- [ ] [S] Compare test baseline results for regressions after upgrade
- [ ] [S] Increase test coverage for at least one complex query to verify migrated 2.x API use in ORM-heavy modules
- [ ] [XS] Validate no deprecation warnings or errors are present in test output relating to old SQLAlchemy patterns

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update CI pipeline configuration files to use upgraded SQLAlchemy and compatible Python version (e.g., in .github/workflows/ci.yaml)
- [ ] [XS] Verify Dockerfile or docker-compose.yaml uses correct base image and requirements for new version if containerized

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update README.md and developer setup docs to reference SQLAlchemy 2.x
- [ ] [XS] Add upgrade summary and breaking changes to CHANGELOG.md
- [ ] [S] Review and update runbook for any operational changes (migration steps, recovery, or debugging tips post-upgrade)
- [ ] [XS] Monitor error logs and DB transaction metrics for 48 hours after deployment to validate upgrade stability

---

Any sections not directly populated above are completed for this specific technology and upgrade path.

N/A — not applicable to this task.