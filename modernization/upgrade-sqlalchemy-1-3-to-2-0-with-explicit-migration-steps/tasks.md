# TASKS — SQLAlchemy 1.3 to 2.0 Upgrade

## Prerequisites

- [ ] [S] Audit current project for all SQLAlchemy dependencies and record all direct and indirect version pins.
- [ ] [XS] Ensure access to a representative database for local development and testing.
- [ ] [XS] Confirm that test infrastructure (unit, integration tests) covers all current ORM/database-related code paths.

## Phase 1 — Preparation

- [ ] [S] Review SQLAlchemy 2.0 migration guide: document all deprecated/removed APIs and behavioral changes impacting the existing codebase.
- [ ] [M] Inventory all locations in the codebase where SQLAlchemy is imported or used.
- [ ] [S] Create a dedicated "sqlalchemy-2.0-migration" feature branch for upgrade development work.
- [ ] [M] Identify all usages of implicit session creation and record for explicit migration.

## Phase 2 — Core Upgrade

- [ ] [M] Update dependency requirements (requirements.txt/setup.py/pyproject.toml or equivalent) to specify SQLAlchemy 2.x.
- [ ] [XL] Refactor all code to replace legacy/implicit session patterns with explicit session management according to SQLAlchemy 2.0 patterns.
- [ ] [L] Replace all deprecated or removed API calls or import paths flagged in the migration guide with their recommended alternatives.
- [ ] [M] Update all database connection configuration to fit SQLAlchemy 2.0 standards as required.
- [ ] [S] Search for use of synchronous/legacy ORM patterns (e.g., Query object patterns, old-style engine usage) and refactor as needed.
- [ ] [M] Refactor any custom type decorators, compilation extensions, or event handlers as per 2.0 guidance.
- [ ] [S] Remove or upgrade any third-party SQLAlchemy plugins/integrations incompatible with 2.0, replacing or updating as needed.

## Phase 3 — Testing & Validation

- [ ] [M] Run all existing unit and integration tests under SQLAlchemy 2.0 and document failures.
- [ ] [L] Update or rewrite broken tests that rely on legacy SQLAlchemy APIs or deprecations.
- [ ] [S] Add new tests to cover newly refactored session management or key ORM behaviors.
- [ ] [M] Perform manual QA of migration code paths (CRUD, queries, transactions) in a development/staging environment.

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update CI pipeline to use SQLAlchemy 2.x in all build stages and runners.
- [ ] [S] Validate that container/build images (e.g., Dockerfiles, virtualenvs) are pinned to the correct SQLAlchemy 2.x version.
- [ ] [XS] Add a required check to CI to prevent re-introduction of SQLAlchemy 1.x APIs.

## Phase 5 — Documentation & Rollout

- [ ] [S] Update developer documentation to reflect new SQLAlchemy usage patterns, session management, and configuration changes.
- [ ] [XS] Document any known compatibility impacts or caveats for local developer or production environments.
- [ ] [S] Announce migration and summarize critical API changes to the team in a release note or internal changelog.

## Post-Migration Cleanup

- [ ] [XS] Remove old migration scripts, compatibility shims, or unused "legacy" code that supported SQLAlchemy 1.x.
- [ ] [XS] Close out the "sqlalchemy-2.0-migration" feature branch after merge, ensuring all dependencies are up to date.
- [ ] [XS] Remove any temporary CI/CD exceptions or feature flags created solely for backwards compatibility during migration.