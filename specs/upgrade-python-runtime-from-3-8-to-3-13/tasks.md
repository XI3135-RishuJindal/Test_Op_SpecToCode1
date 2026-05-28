# Tasks: Upgrade Python Runtime from 3.8 to 3.13

> **Scope:** Python runtime upgrade from 3.8 → 3.13 only.
> **Note:** Tech analysis did not identify specific frameworks, build tools, or dependency files. Tasks below are grounded in standard Python project artifacts. Adjust file names to match actual project structure before execution.

---

## Prerequisites

- [ ] [XS] Confirm Python 3.13 is installable in all target environments (local, CI, production) and document the installation method (e.g., `pyenv`, system package manager, container base image) in a shared team note
- [ ] [XS] Verify `pyenv` or equivalent version manager is available on all developer machines and set minimum required version in `.python-version` file
- [ ] [XS] Confirm access to CI/CD pipeline configuration files and container registry (if applicable) before work begins

---

## Phase 1 — Preparation

- [ ] [S] Create a dedicated branch `upgrade/python-3.8-to-3.13` from the main branch and open a draft PR to track all changes
- [ ] [S] Run `pip list --outdated` and `pip-audit` (or `safety check`) against the current Python 3.8 environment and save the output to `docs/upgrade/pre-upgrade-dependency-audit.txt` for baseline reference
- [ ] [S] Capture the full current test suite pass/fail baseline under Python 3.8 and save output to `docs/upgrade/pre-upgrade-test-baseline.txt`
- [ ] [M] Audit all direct and transitive dependencies in `requirements.txt` / `requirements-dev.txt` / `pyproject.toml` (whichever is present) for Python 3.13 compatibility using `pip install --dry-run` under a Python 3.13 interpreter and log any resolution failures
- [ ] [XS] Add a CI gate (failing check) on the upgrade branch that enforces Python 3.13 as the required interpreter, preventing accidental merges under 3.8

---

## Phase 2 — Core Upgrade

- [ ] [XS] Update the declared Python version constraint in `pyproject.toml` (`requires-python`) or `setup.cfg` (`python_requires`) from `>=3.8` to `>=3.13`
- [ ] [XS] Update `.python-version` (pyenv) from `3.8.x` to `3.13.x` with the exact patch version selected in Prerequisites
- [ ] [S] Replace any use of `typing` backports that are now built-in in 3.13 — specifically remove imports of `typing.Union`, `typing.Optional`, `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Set` used as generics in favour of the built-in `X | Y` syntax and `list[...]`, `dict[...]` etc. across all source files
- [ ] [S] Find and replace all uses of `collections.Callable`, `collections.Mapping`, `collections.MutableMapping`, and other ABCs removed from `collections` (deprecated since 3.3, removed in 3.10) with their `collections.abc` equivalents across all source files
- [ ] [S] Identify and remove any `asyncio` usage patterns deprecated before 3.10 — specifically `asyncio.coroutine` decorator and `yield from` coroutine syntax — replacing with `async def` / `await` in all affected modules
- [ ] [M] Pin or upgrade all packages in `requirements.txt` / `pyproject.toml` to versions that declare Python 3.13 support (check each package's `python_requires` metadata), resolving any conflicts introduced by version bumps
- [ ] [S] Remove any `__future__` imports (`from __future__ import annotations`, `from __future__ import generator_stop`) that are now default behaviour in Python 3.13 and are no longer needed
- [ ] [S] Audit usage of `distutils` (removed in Python 3.12) across all source and configuration files and replace with `setuptools` equivalents where found

---

## Phase 3 — Testing & Validation

- [ ] [M] Run the full test suite under Python 3.13 locally, compare pass/fail counts against `docs/upgrade/pre-upgrade-test-baseline.txt`, and resolve all new failures
- [ ] [S] Run `python -W error` (treat all deprecation warnings as errors) against the test suite under Python 3.13 and fix any newly surfaced `DeprecationWarning` or `SyntaxWarning` instances
- [ ] [S] Execute `pip-audit` / `safety check` under Python 3.13 with the updated dependency set and confirm no new CVEs were introduced by dependency version changes; save output to `docs/upgrade/post-upgrade-dependency-audit.txt`
- [ ] [XS] Verify that code coverage percentage under Python 3.13 is equal to or greater than the baseline captured in Phase 1; document result in the PR description

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration (e.g., `.github/workflows/*.yml`, `Jenkinsfile`, `.gitlab-ci.yml` — whichever is present) to replace all `python-version: "3.8"` matrix entries with `python-version: "3.13"`
- [ ] [XS] Remove Python 3.8 from any multi-version test matrix in CI configuration files, retaining only 3.13 (and any other supported versions explicitly required by the project)
- [ ] [S] Update the base image in `Dockerfile` (if present) from a `python:3.8-*` tag to `python:3.13-slim` (or equivalent), rebuild the image locally, and confirm the application starts correctly

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry under an `Unreleased` section documenting the Python 3.8 → 3.13 runtime upgrade, listing any removed backcompat shims and dependency version changes
- [ ] [XS] Update `README.md` (or equivalent) to change any stated Python version requirement from 3.8 to 3.13 in setup/installation instructions
- [ ] [XS] Update any contributor or environment setup documentation (e.g., `CONTRIBUTING.md`, `docs/development.md`) to reflect the new required Python version
- [ ] [S] Perform a staged rollout to a non-production environment running Python 3.13, monitor application logs for runtime errors or unexpected deprecation warnings for at least one full business day before promoting to production
- [ ] [XS] After production deployment, confirm the running interpreter version via health-check endpoint or startup log and close the draft PR with a link to the post-upgrade audit files