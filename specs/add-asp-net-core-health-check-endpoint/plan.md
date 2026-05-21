# PLAN: Add ASP.NET Core Health-Check Endpoint

## Overview

**Migration Strategy: Feature-Flag Gated / Incremental Addition**

This plan covers the addition of a standard ASP.NET Core health-check endpoint to the existing application. Because this is a net-new, additive capability with no breaking changes to existing functionality, a feature-flag gated (or simple incremental) approach is appropriate. The endpoint can be introduced behind a route (`/health` or `/healthz`) without modifying any existing request pipeline behavior.

**Justification:**
- Risk score is low — no existing code paths are altered.
- Effort is minimal (moderate option, estimated at a small number of person-days).
- Rollback is trivial: remove the registration and route mapping.
- No parallel infrastructure is required.

> **NOTE:** The tech analysis did not supply language, runtime, build tool, or framework version details. All version references and file names below follow standard ASP.NET Core conventions. Where project-specific context is absent, items are marked **TODO**.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | Audit existing `Program.cs` / `Startup.cs` and identify service registration and middleware pipeline entry points | None | 0.25 person-days |
| 2 | Add `Microsoft.Extensions.Diagnostics.HealthChecks` service registration and map `/health` endpoint | Phase 1 complete | 0.5 person-days |
| 3 | Implement custom health-check probes (database, dependency, etc.) if required | Phase 2 complete; TODO: identify dependencies to probe | 0.5–1 person-days |
| 4 | Wire up infrastructure consumers (Kubernetes liveness/readiness probes, load balancer, monitoring) | Phase 2 complete | 0.25 person-days |
| 5 | Testing and CI gate validation | Phases 2–4 complete | 0.5 person-days |

**Total estimated effort:** ~2 person-days (moderate option baseline)

---

## Component Changes

### `Program.cs` / `Startup.cs`

**What changes:** Add `AddHealthChecks()` to the service collection and `MapHealthChecks()` (or `UseHealthChecks()`) to the middleware pipeline.

**Affected files:**
- `Program.cs` (top-level statements style) **or** `Startup.cs` (`ConfigureServices` + `Configure` methods) — **TODO: confirm which pattern the project uses**

**API modifications:**

*Service registration (in `ConfigureServices` or before `builder.Build()`):**
```csharp
builder.Services.AddHealthChecks()
    // TODO: chain custom checks here, e.g.:
    // .AddSqlServer(connectionString, name: "sql-db")
    // .AddUrlGroup(new Uri("https://dependency/"), name: "external-api")
    ;
```

*Endpoint mapping (in `Configure` or after `app.Build()`):**
```csharp
app.MapHealthChecks("/health");
// Optional: separate liveness vs. readiness
app.MapHealthChecks("/health/live",  new HealthCheckOptions { Predicate = _ => false });
app.MapHealthChecks("/health/ready", new HealthCheckOptions { /* tag filter TODO */ });
```

### Custom Health-Check Class(es) *(if needed)*

**What changes:** One or more classes implementing `IHealthCheck` may be added for application-specific probes.

**Affected files:**
- `HealthChecks/DatabaseHealthCheck.cs` — **TODO: create if DB probe is required**
- `HealthChecks/ExternalDependencyHealthCheck.cs` — **TODO: create per dependency**

**Interface to implement:**
```csharp
public class DatabaseHealthCheck : IHealthCheck
{
    public Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    { ... }
}
```

### `appsettings.json` / `appsettings.{Environment}.json`

**What changes:** Add any connection strings or URLs needed by custom health-check probes.

**Config keys to add (TODO — confirm actual keys):**
```json
{
  "HealthChecks": {
    "SqlConnectionString": "TODO",
    "ExternalApiUrl": "TODO"
  }
}
```

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `Microsoft.Extensions.Diagnostics.HealthChecks` | TODO | TODO (match installed ASP.NET Core version) | None — additive | Ships in-box with ASP.NET Core; no separate NuGet package needed for basic checks |
| `AspNetCore.HealthChecks.SqlServer` *(optional)* | TODO | TODO | TODO | Only needed if SQL Server probe is required; verify version compatibility with runtime |
| `AspNetCore.HealthChecks.Uris` *(optional)* | TODO | TODO | TODO | Only needed if HTTP dependency probes are required |

> **NOTE:** The tech analysis did not provide current or target version numbers. All version values above are marked **TODO** and must be resolved against the project's `.csproj` / `global.json` before implementation begins.

---

## Infrastructure Changes

### Kubernetes Manifests

If the application runs on Kubernetes, add or update liveness and readiness probe definitions in the Deployment manifest:

```yaml
# TODO: confirm manifest file path (e.g., k8s/deployment.yaml)
livenessProbe:
  httpGet:
    path: /health/live
    port: 8080   # TODO: confirm application port
  initialDelaySeconds: 10
  periodSeconds: 15

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8080   # TODO: confirm application port
  initialDelaySeconds: 5
  periodSeconds: 10
```

### Docker

- **TODO:** Confirm base image and whether `EXPOSE` directive needs updating.
- No base image change is required solely for health checks; the existing HTTP port is reused.

### CI/CD Pipeline

- **TODO:** Confirm CI/CD tooling (GitHub Actions, Azure DevOps, Jenkins, etc.).
- Add a smoke-test step post-deployment that calls `GET /health` and asserts HTTP `200`.
- Example (GitHub Actions pseudo-step):
  ```yaml
  - name: Health check smoke test
    run: curl --fail http://localhost:${{ env.APP_PORT }}/health
  ```

### Load Balancer / API Gateway

- **TODO:** If a load balancer or API gateway (e.g., NGINX, Azure Application Gateway) is in use, configure its health probe to target `/health`.

---

## Rollback Strategy

Each phase is independently reversible:

| Phase | Rollback Steps |
|-------|---------------|
| 1 (Audit) | No code changes; nothing to revert. |
| 2 (Service + endpoint registration) | Remove `AddHealthChecks()` call from service registration. Remove `MapHealthChecks()` / `UseHealthChecks()` call from middleware pipeline. Rebuild and redeploy. |
| 3 (Custom probes) | Delete custom `IHealthCheck` implementation files. Remove `.Add<CustomCheck>()` chain from `AddHealthChecks()`. Rebuild and redeploy. |
| 4 (Infrastructure wiring) | Revert Kubernetes probe fields to previous values (or remove if newly added). Revert CI/CD smoke-test step. Redeploy manifests via `kubectl apply` or equivalent. |
| 5 (Testing) | No production impact; revert test files if needed. |

**General principle:** Because all changes are additive, a single-commit revert of the health-check registration in `Program.cs`/`Startup.cs` is sufficient to fully disable the feature without affecting any other endpoint.

---

## Testing Strategy

### Unit Tests
- **Tool:** xUnit (TODO: confirm test framework in use)
- **Target:** Each custom `IHealthCheck` implementation (`CheckHealthAsync`)
- **Coverage target:** 100% of custom check classes; mock all external dependencies (DB, HTTP)
- **Example:** Assert `HealthCheckResult.Healthy` / `Degraded` / `Unhealthy` for each code path

### Integration Tests
- **Tool:** `Microsoft.AspNetCore.Mvc.Testing` (`WebApplicationFactory<T>`)
- **Target:** `GET /health` returns HTTP `200` with `Content-Type: application/json`
- **Target:** `GET /health/live` and `GET /health/ready` return expected status codes
- **Coverage target:** All mapped health endpoints exercised at least once

### Regression Tests
- **Scope:** Verify no existing endpoints are affected by the middleware addition
- **Tool:** Existing integration/API test suite (TODO: identify suite location)
- **Gate:** All pre-existing tests must continue to pass

### Performance Tests
- **Tool:** TODO (e.g., k6, NBomber, Apache JMeter)
- **Target:** `/health` endpoint p99 latency < 200 ms under normal load
- **Note:** Health-check endpoints should be excluded from application-level rate limiting if any is configured

### CI Gates
- Unit + integration tests must pass before merge to main branch
- Smoke test (`curl --fail /health`) must pass in staging before production promotion
- TODO: configure branch protection rules to enforce these gates

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Codebase audit complete; entry points confirmed | Phase 1 | Day 1 | TODO |
| Health-check endpoint live in development | Phase 2 | Day 1–2 | TODO |
| Custom probes implemented (if required) | Phase 3 | Day 2–3 | TODO |
| Infrastructure probes configured | Phase 4 | Day 3 | TODO |
| All tests passing; CI gates active | Phase 5 | Day 4 | TODO |
| Deployed to production | Post Phase 5 | Day 5 | TODO |

> Effort derived from the moderate upgrade option (~2 person-days of implementation, ~0.5 days testing/infra). All **Owner** fields are marked **TODO** pending team assignment.