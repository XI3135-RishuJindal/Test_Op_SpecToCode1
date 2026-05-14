# Modernization_Service.Tasks

## Prerequisites
- [ ] [S] Prepare a list of all modules, packages, and scripts in the codebase that use SQLAlchemy.
- [ ] [XS] Verify current SQLAlchemy version and document all pinned versions in requirements files or dependency descriptors.
- [ ] [XS] Ensure access to up-to-date SQLAlchemy 2.x documentation and migration guides.

## Phase 1 — Preparation
- [ ] [S] Review and catalog all deprecated or changed SQLAlchemy APIs used in the codebase (e.g., Session, query, engine usage patterns).
- [ ] [S] Identify and flag any usage of removed legacy constructs (e.g., use of `session.query().filter_by()` style or legacy connection execution).

## Phase 2 — Core Upgrade
- [ ] [M] Update all `session.query()` usages to the new SQLAlchemy 2.x style (`select()`, `Session.execute()`).
- [ ] [M] Refactor any raw SQL execution code to comply with SQLAlchemy 2.x connection patterns.
- [ ] [S] Replace all deprecated imports and method calls according to the 2.x migration guide.
- [ ] [S] Update ORM model definitions where field/property or mapper changes are required for compatibility.
- [ ] [M] Revise transaction and session management to comply with the new 2.x approach (context managers, etc.).
- [ ] [S] Upgrade all dependency descriptors (requirements.txt, setup.py, pyproject.toml) to specify SQLAlchemy 2.x, resolving version constraints as needed.

## Phase 3 — Testing & Validation
- [ ] [S] Run existing test suite to identify failing tests related to SQLAlchemy upgrade.
- [ ] [M] Fix broken tests by addressing SQLAlchemy 2.x API changes in test code.
- [ ] [S] Add or update tests to cover code paths affected by migration, especially queries and database transactions.

## Phase 4 — CI/CD & Infrastructure
- [ ] [S] Update CI configuration to use an environment with SQLAlchemy 2.x installed.
- [ ] [S] Validate that all automated deployment and testing steps pass with upgraded dependencies.

## Phase 5 — Documentation & Rollout
- [ ] [S] Update developer documentation to reflect SQLAlchemy 2.x code patterns and migration decisions.
- [ ] [XS] Communicate migration completion and any required developer actions to the team.

## Post-Migration Cleanup
- [ ] [XS] Remove or archive any compatibility shims or legacy SQLAlchemy code that is no longer needed.
- [ ] [XS] Close or update all related tracking issues and epics in the task management system.