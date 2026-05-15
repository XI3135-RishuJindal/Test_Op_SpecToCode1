## Prerequisites

- [ ] [XS] Verify Python 3.x is installed on all developer and CI environments (version compatible with SQLAlchemy 2.x)
- [ ] [XS] Ensure access to the project repository with push permissions
- [ ] [XS] Confirm pip or build tool used for dependency management is available (e.g., requirements.txt, pyproject.toml)
- [ ] [XS] Obtain permission to update dependencies and edit source files using SQLAlchemy

## Phase 1 — Preparation

- [ ] [S] Create feature branch `upgrade/sqlalchemy-2.x` from latest main/master
- [ ] [XS] Capture test baseline by running current test suite (`pytest` or equivalent) and archiving results as baseline report
- [ ] [XS] Enumerate files importing SQLAlchemy `from sqlalchemy` or `import sqlalchemy` via code search
- [ ] [XS] List usage of ORM and core APIs likely impacted by SQLAlchemy 2.x breaking changes

## Phase 2 — Core Upgrade

- [ ] [S] Upgrade SQLAlchemy from 1.3 to 2.x in requirements.txt (or pyproject.toml/setup.cfg, matching existing tool)
- [ ] [M] Update imports and refactor engine/session setup per SQLAlchemy 2.x style in all files using `create_engine`, `sessionmaker`, and direct `Session` construction
- [ ] [M] Replace deprecated `query()` patterns (`session.query(...)`) with SQLAlchemy 2.x idioms in modules using ORM queries
- [ ] [S] Update usage of removed `autocommit` and `autoflush` options in all ORM and engine instantiations
- [ ] [S] Resolve usage of `MetaData(bind=...)`, refactoring to new patterns in migration or model definition scripts
- [ ] [S] Update exception handling for database errors to match 2.x exception hierarchy in data access modules
- [ ] [M] Refactor legacy transaction contexts (`session.begin(subtransactions=True)` or nested transactions) to supported 2.x contexts

## Phase 3 — Testing & Validation

- [ ] [S] Re-run entire test suite and capture results for comparison to Phase 1 baseline
- [ ] [S] Investigate and resolve any test failures introduced by the SQLAlchemy 2.x migration in affected modules
- [ ] [XS] Confirm code coverage for ORM/model/data-access modules is >= previous baseline (if code coverage is tracked)
- [ ] [XS] Manually test database migrations, if Alembic or similar tools are present

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update CI config (e.g., .github/workflows/python.yml) to pin SQLAlchemy==2.x in build/test steps
- [ ] [XS] If Docker is used, update Dockerfile to pip install SQLAlchemy==2.x
- [ ] [XS] Verify build and test pipelines complete successfully with new dependency

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update requirements.txt/pyproject.toml pin and add SQLAlchemy 2.x upgrade rationale to CHANGELOG.md
- [ ] [XS] Document required code changes and common migration patterns encountered in UPGRADE_GUIDE.md (or README.md if no upgrade doc exists)
- [ ] [XS] Notify stakeholders of upgrade and expected impacts via standard communication channels
- [ ] [S] Monitor error logs and data-access error rates in production for 1 week post-upgrade

---

**N/A — not applicable to this task**  
- Language-specific runtime upgrades  
- Non-SQLAlchemy dependencies  
- Application rewrites  
- Infrastructure-as-code changes unrelated to SQLAlchemy install  
- Rollout beyond the scope of the SQLAlchemy 2.x migration