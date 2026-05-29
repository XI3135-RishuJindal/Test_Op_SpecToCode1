# Plan: Upgrade Python Runtime from 3.8 to 3.13

## Overview

**Migration Strategy: Feature-Flag Gated / Strangler-Fig**

The upgrade from Python 3.8 to 3.13 spans five minor versions, introducing several deprecation removals and behavioral changes (notably in typing, `asyncio`, `ssl`, `distutils`, and the removal of legacy APIs). Given that the tech analysis does not surface a specific framework stack or build tooling, and the upgrade urgency is rated **medium**, a **strangler-fig / parallel-run** approach is appropriate:

1. A parallel CI pipeline targeting Python 3.13 is introduced alongside the existing 3.8 pipeline.
2. Compatibility fixes are applied incrementally, validated against both runtimes.
3. The 3.8 pipeline is retired only after the 3.13 pipeline is green and the application has been validated in a staging environment.

This avoids a big-bang cutover, limits blast radius, and allows rollback at any phase without reverting application logic changes.

> **Risk justification:** The moderate effort/risk rating means a full big-bang migration is inadvisable, but the codebase is not so large that a full strangler-fig decomposition is required. Parallel CI with incremental fixes is the pragmatic middle ground.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit & Inventory — scan codebase for deprecated/removed APIs (`distutils`, legacy `typing` constructs, `collections` aliases, `asyncio` loop APIs, etc.); generate compatibility report | None | TODO person-days (derive from option) |
| 2 | Dependency Compatibility — upgrade or pin all third-party dependencies to versions that support Python 3.13; resolve conflicts | Phase 1 complete | TODO person-days |
| 3 | Code Remediation — fix all identified incompatibilities: type annotation syntax, removed stdlib modules, changed default behaviors | Phase 2 complete | TODO person-days |
| 4 | Parallel CI Pipeline — add Python 3.13 target to CI; run full test suite against both 3.8 and 3.13; fix any remaining failures | Phase 3 complete | TODO person-days |
| 5 | Staging Validation & Cutover — deploy 3.13 build to staging; run regression and performance tests; retire 3.8 pipeline and update production runtime | Phase 4 green | TODO person-days |

> **Note:** Specific person-day estimates are marked TODO because the upgrade option details were not provided. Populate from the `moderate` option estimate once available.

---

## Component Changes

> **Note:** No specific files, classes, or methods were provided in the code context. The changes below are keyed to known Python 3.8→3.13 breaking points. File and class names must be filled in once the codebase is available.

### 3.1 `distutils` Removal (removed in 3.12)
- **What changes:** Any `from distutils import ...` or `setup.py` using `distutils` directly must be migrated to `setuptools` equivalents.
- **Files affected:** `setup.py`, `setup.cfg`, any build helper scripts — TODO (identify via `grep -r "distutils"`)
- **API modified:** Replace `distutils.core.setup` → `setuptools.setup`; replace `distutils.command.*` → `setuptools.command.*`

### 3.2 `typing` Modernization
- **What changes:** Deprecated aliases (`typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Optional`, etc.) still work in 3.13 but emit `DeprecationWarning` and are scheduled for removal. Migrate to built-in generics (`list[str]`, `dict[str, int]`, `X | None`).
- **Files affected:** TODO — identify via `grep -rn "from typing import"` or `pyupgrade --py313-plus`
- **API modified:** `typing.List` → `list`, `typing.Dict` → `dict`, `typing.Union[X, None]` → `X | None`, `typing.Tuple` → `tuple`

### 3.3 `collections` ABC Aliases (removed in 3.10)
- **What changes:** `collections.Callable`, `collections.Mapping`, etc. were removed in 3.10. Must use `collections.abc.*`.
- **Files affected:** TODO — identify via `grep -rn "collections\."` 
- **API modified:** `collections.Callable` → `collections.abc.Callable`, etc.

### 3.4 `asyncio` API Changes
- **What changes:** `asyncio.get_event_loop()` behavior changed in 3.10+; implicit loop creation deprecated. Explicit `asyncio.run()` or `asyncio.get_running_loop()` required.
- **Files affected:** TODO — identify via `grep -rn "get_event_loop\|new_event_loop"`
- **API modified:** Replace bare `loop = asyncio.get_event_loop()` patterns with `asyncio.run(main())` entry points or `asyncio.get_running_loop()` within coroutines.

### 3.5 Exception Chaining & `__cause__`
- **What changes:** `raise X from None` and exception group syntax (`ExceptionGroup`, `except*`) are available in 3.11+. No forced migration required, but existing bare `except:` clauses should be reviewed.
- **Files affected:** TODO

### 3.6 `ssl` / `hashlib` Defaults
- **What changes:** Minimum TLS version defaults tightened in 3.10+. Any hardcoded `ssl.PROTOCOL_TLSv1` or `ssl.PROTOCOL_TLSv1_1` will raise errors.
- **Files affected:** TODO — identify via `grep -rn "ssl\.PROTOCOL"`

### 3.7 `configparser` / `imghdr` / `cgi` / `cgitb` Removals (3.13)
- **What changes:** `cgi`, `cgitb`, `imghdr`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib` removed in 3.13.
- **Files affected:** TODO — identify via `python -W error::DeprecationWarning` test run on 3.11/3.12 as intermediate step.

---

## Dependency Upgrade Plan

> **Note:** No dependency versions were provided in the tech analysis. All current and target versions are marked TODO and must be populated from the actual `requirements.txt` / `pyproject.toml` / `Pipfile` before Phase 2 begins.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| Python runtime | 3.8.x | 3.13.x | See §3.1–3.7 above | Update base image, `pyenv`, or system package |
| `setuptools` | TODO | TODO (≥68.0 for 3.13 support) | `distutils` shim removed in newer setuptools | Ensure `setup.py` does not rely on `distutils` via setuptools shim |
| `pip` | TODO | TODO (≥23.x) | N/A | Upgrade alongside Python |
| All other dependencies | TODO | TODO | TODO | Run `pip install --dry-run` against 3.13; check each package's Python classifier for `Programming Language :: Python :: 3.13` |

**Recommended tooling for dependency audit:**
- `pip-audit` — security and compatibility scan
- `pipdeptree` — visualize conflicts
- `tox` with `py313` environment — matrix test

---

## Infrastructure Changes

> **Note:** No Docker, Kubernetes, or CI/CD configuration was provided in the context. All items below are TODO pending infrastructure file review.

### Docker
- **Base image:** TODO — update `FROM python:3.8-...` → `FROM python:3.13-slim` (or equivalent distro-pinned image) in `Dockerfile`.
- **Multi-stage builds:** TODO — verify builder and runtime stages both reference 3.13.
- **`.python-version` / `runtime.txt`:** TODO — update if present (used by Heroku, pyenv, etc.).

### CI/CD Pipeline
- **Python version matrix:** TODO — update `.github/workflows/*.yml` / `Jenkinsfile` / `.gitlab-ci.yml` / `azure-pipelines.yml` to include `python: "3.13"`.
- **Parallel pipeline (Phase 4):** Add a `python: "3.8"` lane and a `python: "3.13"` lane simultaneously; do not remove 3.8 until Phase 5.
- **`tox.ini` / `pyproject.toml [tool.tox]`:** TODO — add `py313` to `envlist`.

### IaC / Runtime Environment
- TODO — if Lambda, Cloud Run, App Engine, or similar PaaS is used, verify Python 3.13 runtime availability and update the runtime declaration (e.g., `runtime: python313` in `app.yaml`).

---

## Rollback Strategy

Each phase is independently reversible:

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1** (Audit) | Discard the compatibility report; no code changes made. No rollback action needed. |
| **Phase 2** (Dependency upgrades) | Restore `requirements.txt` / `pyproject.toml` / `Pipfile.lock` from version control. Re-run `pip install` against the restored lockfile on Python 3.8. |
| **Phase 3** (Code remediation) | Revert commits via `git revert <range>` or restore from the pre-Phase-3 branch. The 3.8 CI pipeline remains green throughout and serves as the rollback signal. |
| **Phase 4** (Parallel CI) | Remove the Python 3.13 CI job. The 3.8 job continues uninterrupted. No production change has occurred. |
| **Phase 5** (Cutover) | **Docker/container:** re-tag and redeploy the last known-good 3.8 image. **PaaS runtime:** revert the runtime declaration field and redeploy. **CI:** re-enable the 3.8 pipeline as primary. Rollback window: TODO (define SLA with team before cutover). |

---

## Testing Strategy

### Test Pyramid

```
         [Performance]
        [Regression E2E]
      [Integration Tests]
    [Unit Tests — majority]
```

| Layer | Tooling | Coverage Target | CI Gate |
|-------|---------|----------------|---------|
| **Unit** | `pytest` (+ `pytest-cov`) | ≥80% line coverage (TODO — confirm existing baseline) | Fail build if coverage drops below baseline |
| **Integration** | `pytest` with real or containerized dependencies | Key service boundaries covered | Required to pass before merge to main |
| **Regression / E2E** | TODO — specify framework (e.g., `playwright`, `httpx` test client, `behave`) | Critical user paths | Run on staging post-deploy (Phase 5) |
| **Performance** | TODO — specify tool (e.g., `locust`, `k6`, `pytest-benchmark`) | No >10% regression vs 3.8 baseline | Run in Phase 5 staging validation |
| **Compatibility (static)** | `pyupgrade --py313-plus`, `ruff`, `mypy --python-version 3.13` | Zero errors | Added to CI in Phase 4 |
| **Deprecation warnings** | `pytest -W error::DeprecationWarning` | Zero unhandled deprecation warnings | Added to CI in Phase 3 |

### Additional Tooling
- **`vermin`** or **`pyupgrade`** — statically detect minimum Python version requirements and auto-fix syntax.
- **`mypy`** — run with `python_version = 3.13` in `mypy.ini` / `pyproject.toml [tool.mypy]`.
- **`tox`** — matrix across `py38` and `py313` during Phase 4.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Compatibility audit report complete | Phase 1 | TODO | TODO |
| All dependencies confirmed 3.13-compatible | Phase 2 | TODO | TODO |
| All code remediation commits merged | Phase 3 | TODO | TODO |
| Python 3.13 CI pipeline green (parallel) | Phase 4 | TODO | TODO |
| Staging validation signed off | Phase 5 | TODO | TODO |
| Python 3.8 pipeline retired; production on 3.13 | Phase 5 | TODO | TODO |

> **Note:** All estimated completion dates and owner assignments are marked TODO. Populate using the person-days breakdown from the `moderate` upgrade option once that detail is available, and assign owners based on team structure.

---

*Document status: DRAFT — requires population of TODO items from codebase scan, infrastructure review, and upgrade option person-days before Phase 1 begins.*