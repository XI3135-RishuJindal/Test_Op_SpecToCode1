# Plan: Upgrade Python Runtime from 3.8 to 3.13

## Overview

**Migration Strategy: Feature-Flag Gated / Strangler-Fig**

The upgrade from Python 3.8 to 3.13 spans five minor versions, introducing several deprecation removals and behavioral changes (notably in typing, `asyncio`, `ssl`, `distutils`, and the removal of legacy APIs). Given that the tech analysis does not surface a specific framework stack or build tooling, and the upgrade urgency is rated **medium**, a **strangler-fig / incremental approach** is appropriate:

1. Establish a parallel Python 3.13 environment alongside the existing 3.8 environment.
2. Validate compatibility layer by layer (dependencies → application code → integration points).
3. Cut over once all gates pass, retaining the ability to revert to 3.8 at any phase boundary.

A big-bang cutover is avoided because the version gap (3.8 → 3.13) includes breaking changes across multiple minor versions that require staged validation. The medium urgency score does not justify the risk of a single-step migration without incremental checkpoints.

> **NOTE:** Because the provided tech analysis does not specify the runtime host, build tool, framework, or existing dependency versions, several sections below are marked **TODO** pending a full codebase and dependency audit.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Audit & Inventory** — Enumerate all Python files, `requirements*.txt` / `pyproject.toml` / `setup.cfg`, CI configs, and Docker base images. Identify usage of removed/deprecated APIs across 3.9–3.13 changelogs. | None | TODO (derive from codebase size once audit tooling runs) |
| 2 | **Dependency Compatibility Resolution** — Pin or upgrade all third-party dependencies to versions that support Python 3.13. Run `pip-audit` and `pipdeptree` against target runtime. | Phase 1 complete | TODO |
| 3 | **Code Remediation** — Fix all incompatibilities surfaced in Phase 1 (typing changes, removed stdlib modules, syntax deprecations). Apply automated codemods where available (`pyupgrade`, `autoflake`). | Phase 2 complete | TODO |
| 4 | **Parallel Validation** — Run full test suite against both Python 3.8 and 3.13 in CI. Resolve any remaining failures. Conduct performance baseline comparison. | Phase 3 complete | TODO |
| 5 | **Cutover & Cleanup** — Update all environment definitions (Docker, CI, IaC) to Python 3.13 as the sole target. Remove 3.8 compatibility shims. Tag release. | Phase 4 gates passed | TODO |

> **Effort Note:** The upgrade option is identified as `moderate` but no person-days figure was provided. Effort cells are marked TODO and must be populated after the Phase 1 audit produces a concrete incompatibility count and lines-of-code scope.

---

## Component Changes

### Runtime Declaration Files

| File | Change |
|------|--------|
| `pyproject.toml` | Update `requires-python = ">=3.8"` → `requires-python = ">=3.13"` |
| `setup.cfg` | Update `python_requires = ">=3.8"` → `python_requires = ">=3.13"` (if present) |
| `setup.py` | Same as above (if present) |
| `.python-version` (pyenv) | Change pinned version to `3.13.x` |
| `tox.ini` | Update `envlist` to include `py313`; remove `py38` after cutover |
| `.tool-versions` (asdf) | Update Python version entry (if present) |

### Known Python 3.8 → 3.13 Breaking Changes to Remediate

The following are the primary code-level changes required across this version span. Specific file names are **TODO** pending Phase 1 audit.

| Area | Change Required |
|------|----------------|
| `typing` module | Replace `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Optional`, `typing.Union` with built-in generics (`list[...]`, `dict[...]`, `tuple[...]`, `X \| None`, `X \| Y`). Use `pyupgrade --py313-plus` to automate. |
| `distutils` | Removed in 3.12. Replace any `from distutils import ...` with `setuptools` equivalents. |
| `asyncio` coroutine decorators | `@asyncio.coroutine` and `yield from` coroutine style removed in 3.11. Migrate to `async def` / `await`. |
| `collections` ABCs | `collections.Callable`, `collections.Mapping`, etc. removed in 3.10. Use `collections.abc.*`. |
| `ssl` | `ssl.wrap_socket()` removed in 3.12. Use `ssl.SSLContext.wrap_socket()`. |
| `unittest.mock` | Behavioral changes in `AsyncMock`; audit mock usage in tests. |
| `imghdr`, `cgi`, `cgitb`, `aifc`, `chunk`, `crypt`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib` | All removed in 3.11–3.13. Audit imports and replace with third-party equivalents or refactor. |
| `int` bit-length / `str` `removeprefix`/`removesuffix` | Available since 3.9 — no action needed, but can remove any backport shims. |
| `ExceptionGroup` / `except*` | New in 3.11 — no breaking change, but test harnesses may need updates. |
| `tomllib` | Available in stdlib since 3.11 — can remove `tomli` dependency if used. |

> **TODO:** Run `vermin`, `pyupgrade --py313-plus --check`, and `pylint --py-version=3.13` across the full source tree in Phase 1 to produce a complete file-level impact list.

---

## Dependency Upgrade Plan

> **NOTE:** The tech analysis did not provide current dependency names or versions. The table below lists **categories** of dependencies known to require attention for Python 3.13 compatibility. Specific package names, current versions, and target versions must be populated after the Phase 1 `pip freeze` / `pipdeptree` audit.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| TODO: Web framework (e.g., Django, Flask, FastAPI) | TODO | TODO | TODO | Verify Python 3.13 classifier in package metadata |
| TODO: ORM / database driver | TODO | TODO | TODO | C-extension packages often lag; check for 3.13 wheels |
| TODO: Test framework (e.g., pytest) | TODO | TODO | TODO | `pytest` ≥ 8.x required for 3.13 support |
| TODO: Linter / formatter (e.g., pylint, black, ruff) | TODO | TODO | TODO | Pin to versions with 3.13 grammar support |
| TODO: Type checker (e.g., mypy, pyright) | TODO | TODO | TODO | mypy ≥ 1.8 for 3.13 support |
| TODO: `setuptools` | TODO | TODO | Replaces removed `distutils` | Must be present if any code used `distutils` |
| TODO: `cryptography` / `pyOpenSSL` | TODO | TODO | `ssl` API changes | Verify wheel availability for 3.13 |
| TODO: Any C-extension packages | TODO | TODO | ABI changes between minor versions | Check PyPI for `cp313` wheels; may require source builds |

**Audit commands to run in Phase 1:**
```bash
pip install pip-audit pipdeptree
pip-audit
pipdeptree --warn fail
pip index versions <package>  # for each dep, confirm 3.13 wheel exists
```

---

## Infrastructure Changes

### Docker

```dockerfile
# Before
FROM python:3.8-slim

# After
FROM python:3.13-slim
```

- Verify base image tag availability on Docker Hub / internal registry.
- Re-run `docker build` with `--no-cache` to ensure clean layer resolution.
- TODO: If a custom or distroless base image is used, identify the equivalent 3.13 variant.
- TODO: If multi-stage builds reference `python:3.8`, update all stages.

### CI/CD Pipeline

| Item | Change |
|------|--------|
| Python version matrix | Add `3.13`; keep `3.8` in parallel during Phase 4; remove `3.8` in Phase 5 |
| `actions/setup-python` (GitHub Actions) | Set `python-version: '3.13'` |
| TODO: Other CI platform (Jenkins, GitLab CI, CircleCI) | Update `image:` or `runtime:` field to Python 3.13 |
| Cache keys | Invalidate pip cache keyed on Python version (update cache key string) |
| Lint / type-check jobs | Ensure tools are pinned to 3.13-compatible versions (see Dependency table) |

### Virtual Environments / Local Dev

```bash
# Recreate virtual environment
deactivate
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

- Update any `Makefile` or `justfile` targets that hardcode `python3.8` or `python3`.
- TODO: Update `devcontainer.json` if a VS Code dev container is in use.
- TODO: Update Kubernetes pod specs if Python version is specified in container image tags.
- TODO: Update IaC (Terraform, Pulumi, Helm values) if base image is parameterized.

---

## Rollback Strategy

Each phase boundary is an independently reversible checkpoint.

### Phase 1 Rollback
- No code changes made; rollback is a no-op.
- Discard audit artifacts if the project decides not to proceed.

### Phase 2 Rollback
- Revert `requirements*.txt` / `pyproject.toml` dependency pins to pre-Phase-2 state via `git revert` or branch deletion.
- Restore original virtual environment from `pip freeze` snapshot taken at Phase 1 start.

### Phase 3 Rollback
- All code changes should be on a dedicated branch (e.g., `upgrade/python-3.13`).
- `git revert` or branch deletion restores 3.8-compatible code.
- No production environment has been changed at this point.

### Phase 4 Rollback
- CI matrix still includes Python 3.8; simply remove the 3.13 job from the matrix and re-run.
- No deployment artifact has changed.

### Phase 5 Rollback (Post-Cutover)
- Revert Docker base image tag to `python:3.8-slim` in `Dockerfile`.
- Revert CI `python-version` to `3.8`.
- Revert `requires-python` in `pyproject.toml` / `setup.cfg`.
- Redeploy previous container image (tagged pre-cutover) from registry.
- TODO: Define registry image retention policy to ensure the last 3.8-based image is not garbage-collected before the stabilization window closes (recommended: 30 days post-cutover).

---

## Testing Strategy

### Test Pyramid

| Layer | Tooling | Coverage Target | CI Gate |
|-------|---------|----------------|---------|
| **Unit** | TODO (pytest assumed) | ≥ 80% line coverage (maintain existing baseline) | Fail build if coverage drops |
| **Integration** | TODO | Key integration paths covered | Fail build on any failure |
| **Regression** | Full existing test suite run against Python 3.13 | 100% of existing tests must pass | Hard gate before Phase 5 |
| **Performance** | TODO | No regression > 5% on critical paths vs. 3.8 baseline | Advisory gate; block cutover if exceeded |

### Specific Testing Requirements

1. **Compatibility Smoke Test (Phase 2 entry):**
   ```bash
   python3.13 -c "import <top_level_package>"
   ```
   Confirms the application is importable under 3.13 before full test run.

2. **Deprecation Warning Capture (Phase 3):**
   Run test suite with `-W error::DeprecationWarning` to surface all remaining deprecations as errors:
   ```bash
   pytest -W error::DeprecationWarning
   ```

3. **Parallel CI Matrix (Phase 4):**
   Run the full test suite against both `3.8` and `3.13` in the same CI pipeline. Any test passing on 3.8 but failing on 3.13 is a blocking issue.

4. **Type Checking (Phase 3):**
   ```bash
   mypy --python-version 3.13 <source_dir>
   ```
   TODO: Confirm mypy is in use; substitute pyright if applicable.

5. **Dependency Vulnerability Scan:**
   ```bash
   pip-audit --require-hashes
   ```
   Run after Phase 2 dependency upgrades.

### CI Gates Summary

| Gate | Blocks |
|------|--------|
| All unit + integration tests pass on 3.13 | Phase 4 → Phase 5 promotion |
| Zero `DeprecationWarning` errors under `-W error` | Phase 3 completion |
| `pip-audit` clean | Phase 2 completion |
| Performance baseline within threshold | Phase 5 cutover |

---

## Timeline

> **Note:** The upgrade option is `moderate` but no person-days figure was supplied. All durations are marked TODO and must be estimated after the Phase 1 audit produces a concrete scope. The table below provides the sequencing and ownership structure.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Audit complete; incompatibility report produced | Phase 1 | TODO | TODO |
| All dependencies resolved for Python 3.13 | Phase 2 | TODO | TODO |
| All code incompatibilities remediated; type checks pass | Phase 3 | TODO | TODO |
| Full test suite green on Python 3.13 in CI | Phase 4 | TODO | TODO |
| Docker / CI / IaC updated; 3.8 references removed | Phase 5 | TODO | TODO |
| Post-cutover stabilization window closes | Phase 5 | TODO (recommended: 30 days post-cutover) | TODO |

---

*Document status: DRAFT — pending Phase 1 audit to populate all TODO items.*