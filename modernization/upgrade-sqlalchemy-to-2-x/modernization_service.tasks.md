# Modernization_Service.Tasks — SQLAlchemy 2.x Upgrade

## Prerequisites

- [ ] [XS] Ensure access to the code repository and necessary permissions for dependency upgrades
- [ ] [S] Identify all codebases, services, and components that use SQLAlchemy
- [ ] [XS] Document the current version of SQLAlchemy in use

## Phase 1 — Preparation

- [ ] [S] Review SQLAlchemy 2.x migration documentation and list breaking changes affecting the codebase
- [ ] [S] Search for deprecated or removed APIs and features present in the current codebase
- [ ] [S] Identify and list all requirements.txt, setup.py, or equivalent dependency files referencing SQLAlchemy

## Phase 2 — Core Upgrade

- [ ] [S] Upgrade SQLAlchemy to 2.x in the dependency management file(s) (e.g., requirements.txt, setup.py, pyproject.toml) and install locally
- [ ] [M] Refactor database engine and session creation to be compatible with SQLAlchemy 2.x
- [ ] [L] Update all ORM and Core query code to use SQLAlchemy 2.x syntax (e.g., transition from legacy Query to 2.x style)
- [ ] [S] Replace removed or deprecated SQLAlchemy APIs and patterns throughout the codebase
- [ ] [S] Update all imports and usages of SQLAlchemy constructs that have moved or changed in 2.x

## Phase 3 — Testing & Validation

- [ ] [S] Run and fix all existing automated tests to ensure compatibility with SQLAlchemy 2.x
- [ ] [M] Manually test all database-related features for runtime errors and regressions caused by upgrade
- [ ] [S] Verify migration scripts and Alembic (if used) compatibility with SQLAlchemy 2.x

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update CI/CD pipelines to use an environment with SQLAlchemy 2.x installed
- [ ] [S] Validate successful deployment of application(s) with SQLAlchemy 2.x in a staging environment

## Phase 5 — Documentation & Rollout

- [ ] [XS] Update project documentation to reference SQLAlchemy 2.x (e.g., dependencies, developer guides)
- [ ] [S] Announce upgrade and provide a brief summary of impact and important changes to the development team
- [ ] [XS] Document any developer-facing upgrade instructions or code patterns that require attention in SQLAlchemy 2.x

## Post-Migration Cleanup

- [ ] [XS] Remove any obsolete code, comments, or utilities supporting old SQLAlchemy versions
- [ ] [XS] Close any migration-specific tickets or issues related to the SQLAlchemy upgrade
- [ ] [XS] Archive or document lessons learned and major changes for future reference