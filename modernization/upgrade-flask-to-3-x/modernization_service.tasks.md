# Modernization_Service.Tasks

## Prerequisites

- [ ] [S] Identify all codebases/repos using Flask
- [ ] [S] Determine current Flask version(s) in use
- [ ] [S] Audit third-party Flask extensions and dependencies for Flask 3.x compatibility
- [ ] [S] Document Python versions in use and confirm Flask 3.x compatibility

## Phase 1 — Preparation

- [ ] [S] Pin current Flask version in requirements.txt or equivalent file for safe rollback
- [ ] [S] Create a new project branch for the Flask 3.x upgrade effort
- [ ] [S] Take inventory of all Flask app initialization patterns in the codebase

## Phase 2 — Core Upgrade

- [ ] [M] Upgrade Flask to 3.x in requirements.txt or equivalent dependency file
- [ ] [M] Update code to address breaking changes (e.g., import paths, removed APIs, updated configuration patterns) in all Flask apps
- [ ] [M] Upgrade Flask extension packages to latest versions compatible with Flask 3.x
- [ ] [S] Refactor any deprecated usage in Flask Blueprints, error handlers, or custom CLI commands

## Phase 3 — Testing & Validation

- [ ] [M] Run all existing unit tests and integration tests on the upgraded codebase
- [ ] [M] Fix failing tests and resolve compatibility issues arising from Flask 3.x upgrade
- [ ] [S] Manually verify app startup and core endpoints in local/dev environment
- [ ] [S] Smoke test critical user flows (authentication, API endpoints, etc.) post-upgrade

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update CI pipeline to use/test against Flask 3.x and supported Python versions
- [ ] [S] Update Dockerfile(s) or runtime configurations if Python or Flask runtime versions change

## Phase 5 — Documentation & Rollout

- [ ] [S] Document all Flask 3.x-related migrations and key code changes in CHANGELOG.md
- [ ] [S] Update README/setup docs to specify new Flask and dependency requirements
- [ ] [S] Communicate upgrade plan and validation results to stakeholders

## Post-Migration Cleanup

- [ ] [S] Remove unused or obsolete code related to removed/deprecated Flask APIs
- [ ] [S] Delete the upgrade project branch after successful merge and deploy
- [ ] [S] Remove temporary pinning for rollback (if no longer needed)
