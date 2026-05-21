# CONSTITUTION

## Project Identity

**Name:** Security & Reliability Hardening — HTTPS, Health-Check, and Input Validation
**Purpose:** Modernize the existing application by enforcing HTTPS on all traffic, exposing a standard health-check endpoint, and applying DataAnnotations-based input validation across relevant entry points.
**High-Level Goal:** Eliminate clear-text HTTP exposure, enable operational observability via health checks, and prevent malformed or malicious input from reaching business logic — with minimal disruption to existing functionality.

---

## Guiding Principles

1. **Prefer HTTPS enforcement at the application/middleware layer over relying solely on infrastructure redirects, because unencrypted HTTP traffic represents a direct security risk that must be closed regardless of hosting environment.**
2. **Prefer a dedicated, unauthenticated health-check endpoint over repurposing existing routes, because operational tooling (load balancers, orchestrators) requires a predictable, low-overhead liveness signal.**
3. **Prefer declarative DataAnnotations validation over ad-hoc manual checks, because consistent, attribute-driven validation reduces human error and ensures uniform enforcement across all input models.**
4. **Prefer returning structured validation error responses over silent failures or unhandled exceptions, because callers need actionable feedback and unhandled validation errors degrade reliability.**
5. **Prefer non-breaking changes to existing API contracts over refactoring, because the scope is hardening, not redesign — regressions must be avoided.**

---

## Constraints

- **Timeline/Effort:** Moderate effort ceiling (exact person-days TODO — not specified in upgrade option). Scope is limited strictly to the three named features; no additional refactoring is in scope.
- **Technology Mandates:**
  - DataAnnotations validation implies a .NET-based runtime. Exact runtime version: **TODO — confirm target framework (e.g., .NET 6, .NET 8).**
  - HTTPS enforcement must use the platform's standard middleware/configuration mechanism (e.g., `UseHttpsRedirection`, HSTS headers).
  - Health-check endpoint must respond at a conventional path (e.g., `/health`).
- **Scope Freeze:** No changes to data models beyond adding validation attributes. No authentication/authorization changes. No database migrations.
- **Budget:** TODO — not specified.

---

## Quality Standards

- **Test Coverage:** All three features must have at least one automated test each: (1) HTTP→HTTPS redirect returns `301`/`308`, (2) `/health` returns `200 OK`, (3) invalid input returns `400 Bad Request` with a validation error body. Coverage floor for modified files: **≥ 80% line coverage.**
- **Code Review:** Every change requires at least one peer review approval before merge. Security-related changes (HTTPS, validation) require explicit sign-off confirming no regression to existing endpoints.
- **Documentation:** A brief inline comment or README note must explain the HTTPS redirect policy, the health-check path, and how to add DataAnnotations to new models.
- **Deployment Gates:** CI pipeline must pass all existing tests plus the three new feature tests before merge to main. No manual bypasses permitted.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use DataAnnotations for input validation | Task explicitly specifies DataAnnotations; consistent with .NET ecosystem conventions | Accepted |
| ADR-002 | Expose health-check at `/health` | Industry-standard path; compatible with common orchestration and load-balancer defaults | Accepted |
| ADR-003 | Enforce HTTPS via application middleware | Ensures enforcement is portable across hosting environments without relying on external infrastructure config | Accepted |
| ADR-004 | Limit scope to three named features only | Upgrade option is "moderate"; no evidence of broader refactoring mandate | Accepted |
| ADR-005 | Exact runtime/framework version | Not determinable from provided tech analysis — requires confirmation before implementation begins | Proposed (TODO) |