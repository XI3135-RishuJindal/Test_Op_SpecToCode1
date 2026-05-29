# Spec: Upgrade Python Runtime from 3.8 to 3.13

## Summary

This spec covers the upgrade of the Python runtime from version 3.8 to version 3.13. The goal is to move off an end-of-life Python release onto a currently supported, long-term-maintained version, eliminating security exposure and unlocking language and standard-library improvements available in Python 3.9 through 3.13. The expected outcome is a fully operational codebase running on Python 3.13 with all tests passing and no reliance on removed or deprecated language features from 3.8.

---

## Motivation

- **End-of-Life status:** Python 3.8 reached end-of-life on **October 2024**. No further security patches or bug fixes are being issued by the CPython core team for this version.
- **Security exposure:** Running an EOL runtime means any CVEs discovered after the EOL date will remain unpatched at the interpreter level, creating compliance and operational risk.
- **Upgrade urgency:** Rated **medium** — the codebase is not yet in an acute incident state, but continued operation on an EOL runtime increases risk over time and may conflict with security audit requirements.
- **Language improvements:** Python 3.9–3.13 introduce performance improvements (notably the specializing adaptive interpreter in 3.11+), improved error messages, `match`/`case` structural pattern matching (3.10+), and standard-library additions that reduce third-party dependencies.
- **Ecosystem pressure:** Many actively maintained libraries are dropping Python 3.8 support in their current releases, which will increasingly constrain dependency upgrades if the runtime is not updated.

---

## Current State

> **Note:** The provided context does not include repository-level details (specific class names, config keys, schema elements, or framework versions). All items below reflect the known baseline from the task description. Details that require codebase inspection are marked **TODO**.

- **Current runtime version:** Python 3.8 (exact patch version TODO)
- **Build/packaging tool:** TODO — not specified in the provided context
- **Runtime declaration locations:** TODO (e.g., `.python-version`, `pyproject.toml`, `setup.cfg`, `Pipfile`, `tox.ini`, `Dockerfile`, CI workflow files)
- **Frameworks in use:** TODO — none confirmed in the provided context
- **Key behaviours affected:**
  - Any code relying on `typing` constructs that changed between 3.8 and 3.13 (e.g., `typing.List` vs built-in `list` generics introduced in 3.9)
  - Any use of APIs removed or deprecated across the 3.8→3.13 span (see Compatibility section)
  - Any C-extension or native dependencies pinned to CPython 3.8 ABI
- **Dependency pins:** TODO — full `requirements.txt` / `pyproject.toml` dependency list not provided

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Python runtime version | 3.8.x | 3.13.x | Y |
| Runtime version declaration (`.python-version` or equivalent) | `3.8` | `3.13` | Y |
| CI pipeline Python version matrix | `3.8` | `3.13` | Y |
| Container base image (if applicable) | TODO (`python:3.8-*`) | TODO (`python:3.13-*`) | Y |
| `pyproject.toml` / `setup.cfg` `python_requires` | `>=3.8` | `>=3.13` | Y |
| Third-party dependencies pinned to 3.8-compatible versions | TODO | Updated to 3.13-compatible versions | TODO |
| Any usage of removed stdlib modules (see Compatibility) | Removed APIs | Replacement APIs | Y |
| Type annotation syntax (if using legacy `typing` aliases) | `typing.List`, `typing.Dict`, etc. | Built-in generics (`list`, `dict`, etc.) or retained aliases | N (aliases still present in 3.13 but deprecated) |

---

## Compatibility & Breaking Changes

The following are known breaking changes introduced across the Python 3.9–3.13 release series that must be assessed against the codebase.

| Breaking Change | Introduced | Migration Path |
|---|---|---|
| `collections.abc` types no longer accessible via `collections` directly (e.g., `collections.Callable`) | 3.10 (removed) | Replace with `collections.abc.Callable` etc. |
| `distutils` module removed | 3.12 | Replace with `setuptools` or `packaging` equivalents |
| `imp` module removed | 3.12 | Replace with `importlib` |
| `asynchat`, `asyncore`, `smtpd` modules removed | 3.12 | Replace with `asyncio`-based alternatives |
| `cgi` and `cgitb` modules removed | 3.13 | Replace with framework-specific request handling or `html` module |
| `aifc`, `audioop`, `chunk`, `crypt`, `imghdr`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib` modules removed | 3.13 | TODO — assess usage and identify replacements per module |
| `typing.io` and `typing.re` sub-modules removed | 3.12 | Use `typing.IO`, `typing.Pattern` directly |
| `unittest.TestCase.assertEquals` and other deprecated aliases removed | 3.12 | Use canonical method names (e.g., `assertEqual`) |
| `locale.resetlocale()` removed | 3.13 | Use `locale.setlocale(locale.LC_ALL, "")` |
| Changes to `int` string conversion length limit (default 4300 digits) | 3.11 | Configure or refactor code converting very large integers to strings |
| `ssl` module: deprecated protocols and options removed | 3.10–3.12 | Ensure TLS 1.2+ is used; remove `ssl.PROTOCOL_TLSv1` etc. |
| Third-party packages not yet publishing 3.13 wheels | N/A | TODO — audit all pinned dependencies for 3.13 compatibility |
| C-extension packages requiring recompilation for 3.13 ABI | N/A | TODO — identify and update or replace affected packages |

---

## Acceptance Criteria

1. **Given** the repository is checked out on the target branch, **when** the Python interpreter version is queried in the CI environment, **then** it reports Python 3.13.x (where x is the latest stable patch release at time of upgrade).

2. **Given** the full test suite is executed on Python 3.13, **when** all tests run to completion, **then** zero tests fail and zero tests are skipped due to version incompatibility.

3. **Given** the dependency installation step runs on Python 3.13, **when** all declared dependencies are resolved and installed, **then** the installation completes without errors and no dependency requires a Python version less than 3.13.

4. **Given** a static analysis or automated compatibility scan is run against the codebase, **when** it checks for usage of modules removed in Python 3.9–3.13, **then** zero violations are reported.

5. **Given** the CI pipeline configuration is inspected, **when** the Python version matrix is reviewed, **then** Python 3.8 is no longer present and Python 3.13 is the minimum (and at minimum one) configured version.

6. **Given** the runtime version declaration file(s) (e.g., `pyproject.toml`, `.python-version`, `Dockerfile`), **when** each file is inspected, **then** all references to Python 3.8 have been replaced with Python 3.13.

7. **Given** the application is started on Python 3.13, **when** the startup sequence completes, **then** no `DeprecationWarning` or `PendingDeprecationWarning` related to removed-in-3.13 APIs is emitted.

8. **Given** the `python_requires` field in the package metadata, **when** it is inspected, **then** it specifies `>=3.13` (or a compatible constraint), and no longer permits Python 3.8.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the exact current patch version of Python 3.8 in use (runtime and CI)? | TODO | TODO |
| 2 | What build/packaging tool is in use (`pip`, `poetry`, `hatch`, `pdm`, etc.)? | TODO | TODO |
| 3 | Are there any C-extension or native dependencies that require recompilation or replacement for Python 3.13 ABI compatibility? | TODO | TODO |
| 4 | Is a container/Docker image used, and if so what is the current base image tag? | TODO | TODO |
| 5 | Are there any dependencies that do not yet publish Python 3.13-compatible wheels or have not declared 3.13 support? | TODO | TODO |
| 6 | Are any of the stdlib modules removed in 3.12–3.13 (see Compatibility table) actively used in the codebase? | TODO | TODO |
| 7 | Is there a staging or pre-production environment where the 3.13 runtime can be validated before production rollout? | TODO | TODO |
| 8 | Are there any compliance or audit requirements that mandate a specific timeline for moving off EOL runtimes? | TODO | TODO |
| 9 | Should Python 3.13 free-threaded mode (PEP 703, experimental in 3.13) be evaluated, or is the standard GIL build sufficient? | TODO | TODO |