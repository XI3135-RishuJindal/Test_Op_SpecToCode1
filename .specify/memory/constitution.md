# CONSTITUTION
## Project: Add ASP.NET Core Health-Check Endpoint

---

## Project Identity

**Name:** ASP.NET Core Health-Check Endpoint Addition
**Purpose:** Introduce a standardised `/health` (or equivalent) HTTP endpoint to the existing ASP.NET Core application so that infrastructure tooling (load balancers, container orchestrators, monitoring systems) can programmatically verify service liveness and readiness.
**High-Level Goal:** Deliver a production-ready health-check endpoint with minimal disruption to the existing codebase, following ASP.NET Core's built-in `Microsoft.Extensions.Diagnostics.HealthChecks` infrastructure.

---

## Guiding Principles

1. **Prefer the built-in `IHealthChecksBuilder` API over custom middleware** because reinventing health-check plumbing increases maintenance surface and bypasses framework-managed status aggregation.
2. **Prefer additive changes over modifications to existing startup/middleware pipeline** because the tech analysis flags unknown runtime and framework versions — invasive changes risk breaking undocumented dependencies.
3. **Prefer explicit, named health-check registrations over a single catch-all check** because granular checks (liveness vs. readiness) give operators actionable signal without requiring code changes later.
4. **Prefer returning standard HTTP status codes (`200 OK` / `503 Service Unavailable`) over custom response schemas** because downstream infrastructure tooling expects the ASP.NET Core default contract.
5. **Prefer feature-flagged or route-isolated endpoint registration** over global middleware insertion because it limits blast radius if the host application's routing configuration is partially unknown.

---

## Constraints

- **Timeline / Effort:** Moderate option — treat as a bounded, single-engineer task. No multi-sprint re-architecture is in scope.
- **Scope Freeze:** Only the health-check endpoint feature is in scope. Refactoring unrelated startup code, upgrading NuGet packages beyond what health-checks require, or adding dashboards are explicitly out of scope.
- **Technology Mandates:**
  - Must use `Microsoft.Extensions.Diagnostics.HealthChecks` (ships in-box with ASP.NET Core 2.2+). No third-party health-check frameworks unless the existing project already depends on one.
  - Target runtime version: **TODO** — confirm the project's current `<TargetFramework>` before selecting package versions.
  - Build tool: **TODO** — confirm whether the project uses `dotnet CLI`, MSBuild scripts, or a CI pipeline gate before defining the build/deploy step.
- **No Breaking Changes:** The existing API surface and middleware order must remain unchanged for all routes outside `/health*`.

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| Unit test coverage | At least one passing unit/integration test per registered health check, verifying both `Healthy` and `Unhealthy` response paths. |
| Integration test | One `WebApplicationFactory`-based test confirming the endpoint returns `200` when all checks pass and `503` when any check fails. |
| Code review | All changes require at least one peer-review approval before merge; reviewer must verify middleware order is preserved. |
| Documentation | A `HEALTHCHECK.md` (or inline XML doc) describing the endpoint URL, response schema, and how to add new checks — committed alongside the code. |
| Deployment gate | CI pipeline must run all health-check tests and return green before merge to the main branch. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use `Microsoft.Extensions.Diagnostics.HealthChecks` as the implementation foundation | Ships in-box with ASP.NET Core; no additional licensing or dependency risk. | Accepted |
| ADR-002 | Expose endpoint at `/health` (default route) | Industry-standard path expected by Kubernetes, AWS ALB, and most monitoring agents. Override path is a config value if the host requires a different route. | Accepted |
| ADR-003 | Separate liveness and readiness checks if the host supports ASP.NET Core 3.0+ endpoint routing | Allows orchestrators to distinguish "restart the pod" from "remove from load balancer" scenarios. Conditional on confirmed runtime version. | Proposed |
| ADR-004 | Runtime and build-tool versions to be confirmed before implementation begins | Tech analysis lists both as unknown; wrong assumptions could cause silent package incompatibilities. | **TODO** |