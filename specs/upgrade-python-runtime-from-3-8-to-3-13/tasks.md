# Tasks: Upgrade Python Runtime from 3.8 to 3.13

> **Scope:** Python runtime upgrade from 3.8 → 3.13 only.
> **Note:** Tech analysis did not identify specific frameworks, build tools, or dependency files. Tasks below are grounded in standard Python runtime upgrade practices. Assignees should verify file names against the actual repository before starting.

---

## Prerequisites

- [ ] [XS] Confirm Python 3.13 is installable in all target environments (local, CI, production) and document the installation method (e.g., `pyenv`, system package manager, container base image) in a shared team note
- [ ] [XS] Verify `pyenv` (or equivalent version manager) is available on all developer machines and supports Python 3.13 — update `pyenv` to latest if needed
- [ ] [XS] Confirm repository access and that a feature branch can be opened against the main integration branch

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated feature branch `upgrade/python-3.8-to-3.13` from the main branch and push it to the remote
- [ ] [S] Audit all direct and transitive dependencies in `requirements.txt` / `requirements*.txt` / `pyproject.toml` / `setup.cfg` (whichever exist) for Python 3.13 compatibility using `pip-audit` or `pip install --dry-run` under Python 3.13
- [ ] [S] Run the full existing test suite under Python 3.8 and capture the baseline pass/fail report and coverage percentage to `docs/test-baseline-py38.txt` for regression comparison
- [ ] [XS] Record the current Python version pin in `.python-version`, `runtime.txt`, `pyproject.toml`, `setup.cfg`, and any `tox.ini` / `.travis.yml` / GitHub Actions workflow files — list every file that contains a hard-coded `3.8` reference
- [ ] [M] Research and document breaking changes between Python 3.8 and 3.13 that are relevant to the codebase (removed stdlib modules: `distutils`, `aifc`, `cgi`, `cgitb`, `chunk`, `crypt`, `imghdr`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib`; deprecated C-API changes; `asyncio` changes; `typing` changes) and save findings to `docs/py313-migration-notes.md`

---

## Phase 2 — Core Upgrade

- [ ] [XS] Update the Python version pin from `3.8` to `3.13` in `.python-version` (used by `pyenv`)
- [ ] [XS] Update the `python_requires` field from `>=3.8` to `>=3.13` in `pyproject.toml` or `setup.cfg` (whichever is present)
- [ ] [XS] Update the `python-version` matrix / env value from `3.8` to `3.13` in every GitHub Actions workflow file under `.github/workflows/`
- [ ] [XS] Update the Python version specifier in `tox.ini` (`basepython` and `envlist` entries referencing `py38`) to `py313` if `tox.ini` exists
- [ ] [S] Replace or remove any imports of stdlib modules removed in 3.9–3.13 (`distutils`, `cgi`, `aifc`, etc.) identified in Phase 1 notes — update each affected source file with the recommended replacement
- [ ] [S] Resolve any `SyntaxWarning` or `DeprecationWarning` items surfaced by running `python -W error -m py_compile` on all source files under Python 3.13 — fix each affected file
- [ ] [M] Update all pinned dependency versions in `requirements.txt` / `requirements-dev.txt` / `pyproject.toml` to versions that declare Python 3.13 support, resolving any conflicts identified in the Phase 1 audit
- [ ] [S] Validate `asyncio` usage if the codebase uses `asyncio` — replace deprecated `asyncio.coroutine` decorator and `yield from` coroutine patterns removed in 3.11, per `docs/py313-migration-notes.md`
- [ ] [S] Replace any `typing` constructs deprecated and removed by 3.13 (e.g., `typing.io`, `typing.re`, bare `typing.List`/`typing.Dict` where `list`/`dict` builtins are now preferred) across all source files

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full test suite under Python 3.13 locally and record the pass/fail report and coverage percentage to `docs/test-results-py313.txt`
- [ ] [S] Compare `docs/test-results-py313.txt` against `docs/test-baseline-py38.txt` — investigate and resolve every newly failing test before proceeding
- [ ] [S] Run `python -W error` (treat all warnings as errors) against the test suite under Python 3.13 and fix any remaining deprecation warnings surfaced in source or test files
- [ ] [XS] Confirm coverage percentage under Python 3.13 is equal to or greater than the Python 3.8 baseline captured in Phase 1

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (GitHub Actions or equivalent) to install and use Python 3.13 — change `python-version: '3.8'` to `python-version: '3.13'` in all relevant job steps in `.github/workflows/`
- [ ] [XS] Update any `Dockerfile` or `docker-compose.yml` base image references from `python:3.8-*` to `python:3.13-slim` (or equivalent tag) if container files exist in the repository
- [ ] [XS] Update any `runtime.txt` file (used by Heroku or similar PaaS) from `python-3.8.x` to `python-3.13.x` if present

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG` entry under an `Unreleased` section documenting the Python 3.8 → 3.13 runtime upgrade and listing any removed-stdlib replacements made
- [ ] [XS] Update `README.md` prerequisites section to reflect the new minimum Python version of 3.13
- [ ] [S] Review and update any developer setup runbook or `CONTRIBUTING.md` that references Python 3.8 installation steps — replace with Python 3.13 instructions
- [ ] [XS] Open the pull request from `upgrade/python-3.8-to-3.13` targeting the main branch, attach `docs/test-baseline-py38.txt` and `docs/test-results-py313.txt` as PR artifacts, and request review
- [ ] [XS] After merge, monitor the first CI run on the main branch and confirm all jobs pass under Python 3.13 before closing the migration tracking issue