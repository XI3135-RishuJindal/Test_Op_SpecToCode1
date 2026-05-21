# CONSTITUTION
## Project: Add ASP.NET Core Health-Check Endpoint

---

## Project Identity

**Name:** ASP.NET Core Health-Check Endpoint Addition
**Purpose:** Introduce a standardized `/health` (or equivalent) HTTP endpoint to the existing ASP.NET Core application, enabling infrastructure components (load balancers, orchestrators, monitoring tools) to observe service liveness and readiness.
**High-Level Goal:** Deliver a production-ready health-check endpoint with minimal disruption to the existing codebase, following ASP.NET Core's built-in `Microsoft.Extensions.Diagnostics.HealthChecks` infrastructure.

---

## Guiding Principles

1. **Prefer the built-in `IHealthChecksBuilder` API over custom middleware** because reinventing health-check plumbing increases maintenance debt and diverges from the ASP.NET Core ecosystem standard.
2. **Prefer additive changes over modifications to existing startup/middleware code** because the upgrade urgency is medium and risk of regression must be kept low.
3. **Prefer explicit liveness and readiness separation over a single combined endpoint** because orchestrators (e.g., Kubernetes) require distinct signals; conflating them reduces operational clarity.
4. **Prefer thin, focused checks over broad dependency sweeps** because a health endpoint that times out or throws is worse than no endpoint — availability of the check itself is a hard requirement.
5. **Prefer configuration-driven thresholds (degraded/unhealthy) over hard-coded values** because operational teams must be able to tune without a code deployment.

---

## Constraints

- **Timeline / Effort:** Moderate option — scope is bounded to adding the health-check feature only. No refactoring of unrelated code is permitted within this work item.
- **Technology Mandates:**
  - Must use `Microsoft.Extensions.Diagnostics.HealthChecks` (ships in-box with ASP.NET Core); no third-party health-check frameworks unless already present in the project.
  - Target runtime version: **TODO** — confirm the project's current ASP.NET Core version before implementation; API surface differs between versions (≥ 2.2 required for `MapHealthChecks`).
  - Build tooling: **TODO** — verify SDK and project file format before adding NuGet references.
- **Scope Freeze:** This task does not include alerting pipelines, metrics exporters, or dashboard configuration. Those are out of scope.
- **No Breaking Changes:** Existing routes, middleware order, and public API contracts must remain unchanged.

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| Unit test coverage | At least one passing unit test per registered health check, verifying `Healthy`, `Degraded`, and `Unhealthy` return paths. |
| Integration test | At least one integration test confirming the endpoint returns HTTP `200` when healthy and HTTP `503` when unhealthy. |
| Code review | All changes require approval from ≥ 1 reviewer before merge; reviewer must verify middleware ordering is correct. |
| Documentation | A `HEALTHCHECK.md` (or equivalent section in existing docs) must describe the endpoint URL(s), response schema, and how to add new checks. |
| Deployment gate | CI pipeline must execute health-check tests and return green before merge to the main branch. |
| Response contract | Endpoint must return `application/json` with at minimum `status` and `results` fields consistent with ASP.NET Core's default `HealthReportEntry` schema. |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Use `Microsoft.Extensions.Diagnostics.HealthChecks` as the implementation foundation | It is the idiomatic, in-box ASP.NET Core solution; avoids new external dependencies. | Accepted |
| ADR-002 | Expose endpoint via `MapHealthChecks` (endpoint routing) rather than `UseHealthChecks` (middleware) | `MapHealthChecks` integrates with authorization and endpoint metadata; preferred in ASP.NET Core ≥ 3.0. | Accepted |
| ADR-003 | Separate `/health/live` and `/health/ready` routes | Supports Kubernetes liveness/readiness probe patterns without coupling them. | Accepted |
| ADR-004 | Runtime/SDK version to target | **TODO** — pending confirmation of existing project's ASP.NET Core version. | Proposed |
| ADR-005 | Authentication/authorization on health endpoints | **TODO** — determine whether endpoints should be publicly accessible or restricted to internal networks/roles. | Proposed |