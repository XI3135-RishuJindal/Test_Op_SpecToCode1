# CONSTITUTION: Add Structured JSON Logging

> **Project source of truth.** All specs, plans, and tasks must conform to this document.

---

## Project Identity

**Name:** Add Structured JSON Logging

**Purpose:** Replace or augment the existing logging implementation with structured JSON output, enabling machine-readable log ingestion, improved observability, and consistent log schema across the application.

**High-Level Goal:** Deliver a working structured JSON logging layer — with consistent field schema, appropriate log levels, and integration into the existing codebase — without breaking existing functionality.

---

## Guiding Principles

1. **Prefer structured key-value JSON fields over free-form string messages** because unstructured logs cannot be reliably parsed by log aggregation systems (e.g., Datadog, Splunk, CloudWatch).
2. **Prefer additive changes over rewrites of existing log call sites** because the runtime and framework are currently unknown, minimising blast radius reduces regression risk.
3. **Prefer a single logging library/facade over ad-hoc solutions** because inconsistent log formats across modules defeat the purpose of structured logging.
4. **Prefer explicit log-level discipline (DEBUG / INFO / WARN / ERROR)** over blanket logging because noisy logs increase storage cost and obscure signal.
5. **Prefer backward-compatible output** (i.e., JSON logging enabled via configuration flag) over hard-cutover because it allows staged rollout and rollback without a code change.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Timeline / Effort** | Moderate effort ceiling — exact person-days not specified; scope must remain limited to logging layer only. No ancillary refactors. |
| **Technology mandates** | TODO: Confirm target language, runtime version, and approved logging libraries before implementation begins. |
| **Scope freeze** | This project covers logging only. Log aggregation pipeline configuration, alerting rules, and dashboard setup are out of scope. |
| **Breaking changes** | Existing log output contracts (if any downstream system depends on current format) must not be silently broken. Migration path required. |
| **Budget** | TODO: No budget figure provided. Assume no new paid third-party services without explicit approval. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Schema consistency** | Every log line must contain at minimum: `timestamp`, `level`, `message`, and `service` fields. Verified by a schema-validation test. |
| **Test coverage** | All new logging utility/wrapper code must have ≥ 80% unit test coverage. |
| **No silent log loss** | Integration test must assert that a representative ERROR log call produces valid, parseable JSON on stdout/stderr. |
| **Code review** | Minimum 1 peer review approval required before merge; reviewer must verify field naming conventions match the agreed schema. |
| **Documentation** | A `LOGGING.md` (or equivalent) must document: the JSON schema, available log levels, how to enable/disable JSON mode, and how to add a new log call site. |
| **Deployment gate** | CI pipeline must run log-output parsing smoke test; pipeline fails if any log line emitted during test suite is not valid JSON (when JSON mode is enabled). |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Structured JSON logging will be the target output format | Enables machine-readable ingestion; aligns with stated modernization goal | Accepted |
| ADR-002 | JSON logging mode will be togglable via configuration (not hard-coded on) | Allows rollback and local developer experience to remain human-readable | Proposed |
| ADR-003 | Specific logging library selection deferred until runtime/language is confirmed | Language and runtime are currently unknown; premature selection risks rework | Proposed |
| ADR-004 | Log schema fields (`timestamp`, `level`, `message`, `service`) defined as minimum required set | Provides a consistent baseline without over-specifying before full context is known | Proposed |

---

> **TODO items blocking finalisation:** Confirm language, runtime, build tool, and any compliance requirements for log data (e.g., PII redaction obligations) before ADR-003 can be resolved and implementation specs written.