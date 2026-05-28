# CONSTITUTION
## Structured JSON Logging via Python `logging` Module

---

## Project Identity

**Name:** Structured JSON Logging Modernization

**Purpose:** Introduce structured JSON logging to the existing codebase using Python's built-in `logging` module, replacing or augmenting any current ad-hoc or plaintext logging approach.

**High-Level Goal:** Ensure all application log output is machine-readable, consistently formatted JSON, enabling downstream log aggregation, search, and alerting tooling to operate reliably on structured fields.

---

## Guiding Principles

1. **Prefer Python's standard `logging` module over third-party logging frameworks** because it minimises new dependencies and is universally available across Python runtimes, reducing long-term maintenance risk.
2. **Prefer a custom `logging.Formatter` subclass over monkey-patching or print-based output** because it integrates cleanly with existing handler configuration and preserves compatibility with any logging already in place.
3. **Prefer additive changes over wholesale replacement of existing log call-sites** because the upgrade urgency is medium and scope must remain bounded; existing `logger.info(...)` / `logger.error(...)` calls should continue to work without modification.
4. **Prefer explicit, documented field schemas over ad-hoc key naming** because structured logs only deliver value when consumers can rely on consistent field names (e.g., `timestamp`, `level`, `message`, `logger`, `trace_id`).
5. **Prefer configuration via the standard `logging.config` (dict-config or file-config) over hard-coded handler setup** because it keeps environment-specific behaviour (log level, output destination) outside application code.

---

## Constraints

- **Effort ceiling:** Moderate option — treat as a bounded, single-engineer task. No architectural rework of unrelated systems is in scope.
- **Language/Runtime:** Python (version TODO — confirm minimum supported Python version in the target repo before implementation; formatter must be compatible with that version).
- **Dependency constraint:** No new required runtime dependencies unless the standard library is genuinely insufficient. If a lightweight helper (e.g., `python-json-logger`) is introduced, it must be explicitly approved and pinned.
- **Scope freeze:** Only the logging layer is in scope. Changes to application logic, data models, or infrastructure are out of scope.
- **TODO:** Confirm whether the project has an existing `logging` configuration file or dict-config that must be preserved or migrated.
- **TODO:** Confirm target runtime Python version and deployment environment (container, VM, serverless) to validate handler/output assumptions.

---

## Quality Standards

- **Test coverage:** Every new class and function introduced (formatter, filter, config loader) must have unit tests achieving ≥ 90 % line coverage. Tests must assert on the parsed JSON output, not on raw strings.
- **Schema validation:** At least one test must deserialise log output with `json.loads()` and assert the presence of all mandatory fields (`timestamp`, `level`, `message`, `logger`).
- **Code review:** All changes require at least one peer review approval before merge. Reviewer must verify no plaintext log output paths remain unguarded.
- **Documentation:** A `LOGGING.md` (or equivalent section in the project README) must document the JSON field schema, how to configure log level per environment, and how to add custom fields to a log record.
- **Deployment gate:** CI pipeline must run the logging unit-test suite and fail the build on any test failure or coverage drop below the stated floor before merge to the main branch.
- **No silent failures:** The formatter must never suppress or swallow a log record; if JSON serialisation of a field fails, it must fall back to a string representation and include an `_serialisation_error` field rather than dropping the record.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use Python's built-in `logging` module as the logging backbone | Avoids new mandatory dependencies; universally available in Python standard library | Accepted |
| ADR-002 | Implement JSON formatting as a `logging.Formatter` subclass | Clean integration point; does not require changes to existing log call-sites | Accepted |
| ADR-003 | Expose logging configuration via `logging.config` dict-config | Keeps environment-specific settings (level, handlers) outside source code | Accepted |
| ADR-004 | Third-party JSON logging libraries are optional, not required | Scope and dependency constraints favour stdlib-first approach; external lib requires explicit approval | Accepted |
| ADR-005 | Minimum Python version — **TODO** | Must be confirmed from repo metadata before implementation begins | Proposed |