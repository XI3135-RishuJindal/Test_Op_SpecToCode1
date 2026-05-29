# CONSTITUTION — Introduce Structured Logging

> **Project source of truth.** All specs, plans, and tasks must conform to this document.

---

## Project Identity

**Name:** Introduce Structured Logging

**Purpose:** Replace or augment the existing logging approach with structured logging — emitting log records as machine-parseable data (e.g. JSON) rather than freeform strings — to improve observability, searchability, and operational insight.

**High-level goal:** Deliver a consistent, structured logging foundation across the codebase under a moderate effort envelope, without disrupting existing functionality.

---

## Guiding Principles

1. **Prefer structured (key-value / JSON) log output over freeform string concatenation** because unstructured logs cannot be reliably queried or alerted on in modern observability platforms.
2. **Prefer a single, project-wide logging library/facade over ad-hoc logging calls** because inconsistent logging patterns create maintenance debt and make log correlation across components unreliable.
3. **Prefer additive changes over rewriting call sites in bulk** because the runtime and language are currently unconfirmed (TODO), minimising blast radius reduces regression risk during the transition.
4. **Prefer log-level discipline (DEBUG / INFO / WARN / ERROR) over logging everything at one level** because undifferentiated log volume increases noise and raises ingestion costs.
5. **Prefer context propagation (request ID, trace ID, user/session identifiers) as first-class log fields** because without correlation identifiers, structured logs lose most of their diagnostic value.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate — exact person-days TODO (upgrade option detail not provided); scope must stay within a moderate effort band and not expand into unrelated refactors. |
| **Language / Runtime** | TODO — language and runtime are unconfirmed; the chosen logging library must be validated against the confirmed stack before implementation begins. |
| **Build tool** | TODO — dependency addition must be compatible with the confirmed build tool. |
| **Scope freeze** | This project covers logging instrumentation only. Log aggregation infrastructure, alerting rules, and dashboard configuration are out of scope unless explicitly re-scoped. |
| **Backward compatibility** | Existing log consumers (files, sidecar shippers, CI log capture) must not break; output format changes must be coordinated or feature-flagged. |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Test coverage** | Any new logging utility/wrapper must have unit tests covering at least the happy path and error-level emission; no net reduction in overall test coverage. |
| **Code review** | All logging changes require at least one peer review approval before merge; reviewer must verify structured fields are present and correctly typed. |
| **No secrets in logs** | CI gate must include a scan (grep or linter rule) confirming that passwords, tokens, and PII field names are not logged; zero violations to pass. |
| **Log-level correctness** | PR checklist item: every new log call must declare an explicit level; `DEBUG` calls must not appear in production-default configuration. |
| **Documentation** | A `LOGGING.md` (or equivalent) must be committed alongside the implementation, documenting: chosen library, log format/schema, required context fields, and how to add a new log call. |
| **Deployment gate** | Smoke test in staging must confirm structured output is valid JSON (or chosen format) for at least one request path before production rollout. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Adopt structured logging as the target logging standard | Core objective of this modernization task; medium urgency tech debt reduction. | Accepted |
| ADR-002 | Defer logging library selection until language/runtime is confirmed | Language and runtime are currently unknown; selecting a library now risks rework. | Accepted |
| ADR-003 | Keep log aggregation infrastructure changes out of scope | Moderate effort ceiling does not accommodate infrastructure work; separation of concerns. | Accepted |
| ADR-004 | Require a `LOGGING.md` conventions document as a delivery artifact | Ensures the structured logging pattern is reproducible by future contributors without tribal knowledge. | Accepted |

---

*Unknowns marked **TODO** must be resolved before implementation specs are written.*