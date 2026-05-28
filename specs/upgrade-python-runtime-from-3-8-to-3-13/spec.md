# Spec: Upgrade Python Runtime from 3.8 to 3.13

## Summary

This spec covers the upgrade of the Python runtime from version 3.8 to version 3.13. The goal is to move off an end-of-life Python release onto a currently supported, long-term-maintained version, eliminating security exposure and enabling access to language and standard-library improvements introduced across the 3.9–3.13 release series. The expected outcome is a fully operational application running on Python 3.13 with all tests passing and no regressions in existing behaviour.

---

## Motivation

- **End-of-life status:** Python 3.8 reached end-of-life on **2024-10-07**. No further security patches or bug fixes are being issued by the CPython core team for this version.
- **Security exposure:** Running an EOL runtime means any CVEs discovered after the EOL date will remain unpatched at the interpreter level, creating compliance and operational risk.
- **Upgrade urgency:** Rated **medium** — the application is not yet in an actively exploited state, but continued operation on an EOL runtime increases risk over time and may conflict with organisational security policies or audit requirements.
- **Python 3.13 support window:** Python 3.13 is the current stable release (released October 2024) and will receive full support through approximately 2029, providing a multi-year runway before the next required upgrade.
- **Standard library and performance improvements:** Versions 3.9 through 3.13 include meaningful performance improvements (notably the specialising adaptive interpreter in 3.11+), typing system enhancements, and deprecation removals that are better addressed proactively than reactively.

---

## Current State

- **Runtime version in use:** Python 3.8 (EOL as of 2024-10-07)
- **Specific classes, config keys, and schema elements:** TODO — no codebase context was provided. A full audit of runtime-version-pinned configuration (e.g., CI pipeline runtime selectors, container base image tags, virtual environment tooling configuration, and dependency lock files) is required before changes are made.
- **Dependency versions:** TODO — the current set of third-party dependencies and their Python 3.13 compatibility status is not available in the provided context. A dependency compatibility matrix must be produced as part of planning.
- **Known use of deprecated/removed APIs:** TODO — usage of Python 3.8-era APIs that were deprecated and subsequently removed in 3.9–3.13 (e.g., `collections` aliases, `loop` parameter in `asyncio` functions, `distutils`, `imghdr`, `cgi`, `aifc`, etc.) has not been audited.
- **Build and packaging tooling:** TODO — build tool and packaging configuration are not specified in the provided context.
- **Frameworks in use:** TODO — no framework information was provided.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| Python interpreter version | 3.8 (EOL) | 3.13 (stable) | Y |
| Runtime version pin (CI/CD, containers, tooling config) | 3.8 | 3.13 | Y |
| Third-party dependencies | Versions compatible with Python 3.8 | Versions compatible with Python 3.13 | TODO — depends on audit |
| Standard library API usage | May include APIs removed in 3.9–3.13 | Updated to current supported APIs | Y (where removed APIs are in use) |
| Type annotation syntax | May use `typing` module shims required for 3.8 (e.g., `typing.List`, `typing.Dict`, `typing.Optional`) | Can adopt built-in generic types and `X \| Y` union syntax available from 3.10+ | N (backwards-compatible if not changed; optional modernisation) |
| `distutils` usage (if any) | Available in 3.8 | Removed in 3.12 | Y |
| `asyncio` `loop` parameter usage (if any) | Deprecated in 3.8, accepted | Removed in 3.10 | Y |

---

## Compatibility & Breaking Changes

| Breaking Change | Affected Area | Migration Path |
|---|---|---|
| Python 3.8 EOL — no further patches | Entire runtime | Upgrade interpreter to 3.13 |
| `distutils` removed (3.12) | Build/packaging scripts that import `distutils` | Replace with `setuptools` equivalents or standard `packaging` library |
| `asyncio` `loop` keyword argument removed from high-level APIs (3.10) | Any async code passing `loop=` to `asyncio.sleep`, `asyncio.wait`, etc. | Remove the `loop` argument; the running loop is obtained implicitly |
| `collections.abc` aliases removed from `collections` (3.10) | Code using `collections.Callable`, `collections.Mapping`, etc. | Replace with `collections.abc.Callable`, `collections.abc.Mapping`, etc. |
| `cgi` and `cgitb` modules removed (3.13) | Any code importing `cgi` or `cgitb` | TODO — assess usage; migrate to framework-level request handling |
| `imghdr`, `aifc`, `chunk`, `crypt`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`, `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu`, `xdrlib` removed (3.13) | Any code importing these modules | TODO — assess usage; replace with third-party equivalents or remove |
| Third-party dependency incompatibilities | TODO — requires dependency audit | TODO — update each incompatible dependency to a Python 3.13-compatible release |
| Runtime version pins in CI, containers, and tooling | All environment configuration files pinning `3.8` | Update all pins to `3.13` |
| `typing` shims no longer needed (optional) | Type annotations using `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Optional` | Optionally replace with built-in generics (`list[...]`, `dict[...]`, `X \| None`); not a breaking change if left as-is |

---

## Acceptance Criteria

1. **Given** the application's CI pipeline, **when** the build is triggered, **then** the Python interpreter version reported at runtime is `3.13.x`.
2. **Given** the full test suite, **when** executed against Python 3.13, **then** all tests that passed on Python 3.8 pass on Python 3.13 with no new failures.
3. **Given** the dependency installation step, **when** all dependencies are installed on Python 3.13, **then** the installation completes without errors and no dependency reports a Python version incompatibility warning or error.
4. **Given** a static analysis scan (e.g., linter or compatibility checker) targeting removed APIs, **when** run against the codebase, **then** zero uses of APIs removed between Python 3.9 and 3.13 are reported.
5. **Given** the application startup sequence, **when** the application is started on Python 3.13, **then** it starts successfully with no `DeprecationWarning` or `ImportError` related to removed or relocated standard library modules.
6. **Given** the container or deployment environment, **when** the runtime image or environment is inspected, **then** no Python 3.8 interpreter is present and the active interpreter is Python 3.13.
7. **Given** the CI pipeline configuration, **when** reviewed, **then** all runtime version pins, base image references, and tooling configuration reference Python 3.13 and no reference to Python 3.8 remains.
8. **Given** the application under its normal workload, **when** exercised through its standard acceptance or smoke test suite on Python 3.13, **then** all functional outcomes match those produced on Python 3.8 (no behavioural regressions).

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the complete list of third-party dependencies and their current pinned versions? A Python 3.13 compatibility matrix cannot be produced without this. | TODO | TODO |
| 2 | What build tool and packaging system is in use (e.g., pip + requirements.txt, Poetry, PDM, Hatch, setuptools)? This affects how dependency and runtime pins are updated. | TODO | TODO |
| 3 | What CI/CD platform and container base images are in use? Runtime version pins exist in these environments and must be identified. | TODO | TODO |
| 4 | Are any of the standard library modules removed in 3.13 (`cgi`, `aifc`, `imghdr`, etc.) actively used in the codebase? | TODO | TODO |
| 5 | Is `distutils` used directly anywhere in the codebase or in custom build scripts? | TODO | TODO |
| 6 | Are there any compiled extension modules (C extensions, Cython, etc.) that must be rebuilt or have separate Python 3.13 compatibility concerns? | TODO | TODO |
| 7 | What is the target deployment environment (OS, architecture)? Python 3.13 availability must be confirmed for that environment. | TODO | TODO |
| 8 | Are there any external service integrations or SDKs whose Python 3.13 support status is unknown or unconfirmed? | TODO | TODO |
| 9 | Is there a requirement to support Python 3.8 in parallel during a transition period, or is a hard cutover acceptable? | TODO | TODO |