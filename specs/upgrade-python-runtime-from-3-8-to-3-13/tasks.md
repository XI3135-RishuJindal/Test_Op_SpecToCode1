# Tasks: Upgrade Python Runtime from 3.8 to 3.13

> **Scope:** Python runtime upgrade from 3.8 → 3.13 only.
> **Note:** Tech analysis did not specify frameworks, build tools, or infrastructure details. Tasks below are grounded in what is universally required for a Python 3.8 → 3.13 runtime upgrade. File names marked `<verify>` must be confirmed against the actual repository before work begins.

---

## Prerequisites

- [ ] [XS] Confirm Python 3.13 is installable in the target environment (local, CI, and production) and document the installation method (e.g., `pyenv`, system package manager, official installer)
- [ ] [XS] Verify repository structure and locate all files that pin the Python version (e.g., `.python-version`, `pyproject.toml`, `setup.cfg`, `setup.py`, `tox.ini`, `Makefile`, `.env` files) before any changes begin
- [ ] [XS] Confirm all team members and CI runners have `pyenv` (or equivalent) available to switch Python versions without affecting other projects
- [ ] [XS] Ensure write access to CI/CD pipeline configuration files and any container/image definitions present in the repository

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated branch `upgrade/python-3.13` from the current default branch and push it to the remote to serve as the integration branch for all upgrade work
- [ ] [M] Run the full existing test suite on Python 3.8 and capture a baseline report (pass/fail counts, coverage percentage, any pre-existing failures) in a file `docs/upgrade/baseline-py38-test-report.md` for regression comparison
- [ ] [S] Run `python -m py_compile` (or equivalent static check) across all `.py` source files on Python 3.8 to confirm zero syntax errors exist before the upgrade begins
- [ ] [M] Audit all direct and transitive dependencies in `requirements.txt` / `pyproject.toml` / `setup.cfg` `<verify>` for Python 3.13 compatibility using `pip install --dry-run` under Python 3.13 and document any incompatible packages in `docs/upgrade/dependency-compat-py313.md`
- [ ] [S] Identify all uses of Python 3.8-era APIs removed or deprecated by 3.13 by running `python -W error` and reviewing deprecation warnings captured in the baseline test run; log findings in `docs/upgrade/deprecation-findings.md`

---

## Phase 2 — Core Upgrade

- [ ] [XS] Update the Python version pin from `3.8` to `3.13` in `.python-version` `<verify>` so `pyenv` and tooling resolve the correct interpreter
- [ ] [XS] Update the `python_requires` field from `>=3.8` to `>=3.13` in `setup.cfg` or `pyproject.toml` `<verify>` to reflect the new minimum supported runtime
- [ ] [XS] Update the `Programming Language :: Python :: 3.8` classifier to `Programming Language :: Python :: 3.13` in `setup.cfg` or `pyproject.toml` `<verify>`
- [ ] [S] Update all pinned dependency versions in `requirements.txt` / `requirements-dev.txt` `<verify>` to versions confirmed compatible with Python 3.13 based on the audit in Phase 1
- [ ] [M] Resolve all uses of `collections.Callable`, `collections.Mapping`, and other `collections` ABCs moved to `collections.abc` in Python 3.10+ (removed in 3.10, fatal in 3.13) across all `.py` source files `<verify>`
- [ ] [M] Replace all uses of `asyncio.coroutine` decorator and `yield from`-based coroutines (removed in 3.11) with `async def` / `await` syntax in all affected `.py` source files `<verify>`
- [ ] [S] Resolve any use of `distutils` (removed in Python 3.12) by migrating to `setuptools` equivalents in `setup.py` / `setup.cfg` `<verify>`
- [ ] [S] Audit and fix any use of `typing` aliases deprecated in 3.9 and removed in 3.13 (e.g., `typing.List`, `typing.Dict`, `typing.Tuple`) by replacing with built-in generics (`list[...]`, `dict[...]`, `tuple[...]`) across all `.py` source files `<verify>`
- [ ] [M] Resolve any remaining `DeprecationWarning` or `SyntaxWarning` entries surfaced when running the test suite under Python 3.13 with `-W error` flag, editing the specific source files identified in `docs/upgrade/deprecation-findings.md`

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full test suite under Python 3.13 and produce a results report in `docs/upgrade/results-py313-test-report.md`; compare pass/fail counts and coverage percentage against the baseline captured in Phase 1
- [ ] [S] Investigate and fix any test failures unique to Python 3.13 (not present in the 3.8 baseline) identified in the Phase 3 test run, updating source or test files as needed
- [ ] [S] Run `python -W error` against the full test suite under Python 3.13 and confirm zero unresolved `DeprecationWarning` or `PendingDeprecationWarning` entries remain
- [ ] [XS] Verify that the installed dependency tree under Python 3.13 contains no packages flagged as incompatible or yanked by running `pip check` and resolving any reported conflicts

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the Python version matrix in the CI pipeline configuration file `<verify>` (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml`) to replace `3.8` with `3.13` in all job definitions
- [ ] [XS] Remove Python 3.8 from any multi-version test matrix in the CI configuration `<verify>` if 3.8 is no longer a supported target after this upgrade
- [ ] [S] Update any `FROM python:3.8*` base image references in `Dockerfile` `<verify>` to `FROM python:3.13-slim` (or the appropriate variant) and verify the image builds successfully
- [ ] [XS] Update any hardcoded `python3.8` binary path references in `Makefile`, shell scripts, or CI step commands `<verify>` to `python3.13` or the unversioned `python3`

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry documenting the Python runtime upgrade from 3.8 to 3.13, listing removed API fixes and any dependency version bumps made during the upgrade
- [ ] [S] Review and update `README.md` `<verify>` to replace all references to Python 3.8 prerequisites with Python 3.13, including installation instructions and badge links
- [ ] [XS] Open a pull request from `upgrade/python-3.13` to the default branch, referencing the baseline and results reports, and request review from at least one other engineer before merging
- [ ] [XS] After merging, monitor the first CI run on the default branch and the first deployment to a staging environment for any runtime errors not caught during local testing; document observations in `docs/upgrade/post-migration-notes.md`