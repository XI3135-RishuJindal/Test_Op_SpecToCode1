# PLAN: Add ASP.NET Core Health-Check Endpoint

## Overview

**Migration Strategy: Feature-Flag Gated / Incremental Addition**

This plan covers the addition of a standard ASP.NET Core health-check endpoint to the existing application. Because this is a net-new, additive capability with no breaking changes to existing routes or business logic, a **feature-flag gated** incremental approach is appropriate. The endpoint can be registered behind a configuration toggle, validated in lower environments, and promoted to production without requiring a coordinated cutover.

**Justification:**
- Risk is low — health-check registration is a well-understood, non-destructive ASP.NET Core pattern.
- The upgrade option is rated **moderate** effort; no large-scale refactoring is required.
- Rollback is trivial: removing the service registration and middleware line fully reverts the change.
- Runtime, language version, and build tooling are not fully specified in the provided context (see TODOs below), so a conservative, self-contained implementation minimizes surface area.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 — Discovery & Baseline | Confirm target runtime, existing `Program.cs` / `Startup.cs` structure, existing middleware pipeline, and any load-balancer or orchestrator health-probe requirements. | Access to codebase and deployment config | TODO (derive from actual codebase audit) |
| 2 — Implementation | Register `AddHealthChecks()` service, map `/health` (liveness) and `/health/ready` (readiness) endpoints, add any custom health-check probes (DB, dependencies). | Phase 1 complete | TODO (moderate estimate — see note below) |
| 3 — Testing & Validation | Unit-test custom check logic; integration-test endpoint responses (200/503); add CI gate. | Phase 2 complete | TODO |
| 4 — Deployment & Promotion | Deploy behind feature flag; validate in staging; enable in production; update load-balancer / k8s probe config. | Phase 3 complete; infra access | TODO |

> **Note on effort:** The upgrade option is described as "moderate" but no person-days figure was provided in the input. Effort cells are marked TODO pending that figure and a codebase audit. A typical ASP.NET Core health-check addition of this scope is **1–3 person-days** end-to-end, but this must be confirmed against actual context.

---

## Component Changes

### `Program.cs` / `Startup.cs`

**What changes:** Two additions to the ASP.NET Core pipeline.

1. **Service registration** (in `ConfigureServices` or the top-level builder section):
   ```csharp
   builder.Services.AddHealthChecks()
       // Add custom checks here, e.g.:
       // .AddSqlServer(connectionString, name: "sql", tags: new[] { "ready" })
       ;
   ```

2. **Middleware mapping** (in `Configure` or after `app.Build()`):
   ```csharp
   app.MapHealthChecks("/health", new HealthCheckOptions
   {
       Predicate = _ => false   // liveness: no checks, just "alive"
   });

   app.MapHealthChecks("/health/ready", new HealthCheckOptions
   {
       Predicate = check => check.Tags.Contains("ready")
   });
   ```

**Files affected:**
- `Program.cs` **or** `Startup.cs` — TODO: confirm which pattern the project uses (minimal API vs. classic `Startup`).

---

### Custom Health-Check Class (if needed)

**What changes:** If any dependency (database, external service, cache) must be probed, a custom class implementing `IHealthCheck` should be added.

**Suggested file:** `HealthChecks/DatabaseHealthCheck.cs` (name is illustrative — TODO: align with project naming conventions).

```csharp
public class DatabaseHealthCheck : IHealthCheck
{
    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context,
        CancellationToken cancellationToken = default)
    {
        // TODO: implement actual probe logic
        return HealthCheckResult.Healthy();
    }
}
```

**APIs modified:** None — this is purely additive.

---

### Feature-Flag Configuration

**What changes:** A configuration key (e.g., `FeatureFlags:HealthChecks`) guards endpoint registration during rollout.

**Files affected:**
- `appsettings.json` / `appsettings.Production.json` — add flag key.
- `Program.cs` / `Startup.cs` — wrap `MapHealthChecks` calls in a conditional read of the flag.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `Microsoft.Extensions.Diagnostics.HealthChecks` | TODO — not provided in tech analysis | TODO — not provided in tech analysis | None expected (additive package) | Ships in-box with `Microsoft.AspNetCore.App` shared framework; explicit package reference may not be needed. Confirm against project's SDK version. |
| Additional check packages (e.g., `AspNetCore.HealthChecks.SqlServer`) | N/A — not currently referenced | TODO — select version matching target runtime | N/A | Only add if custom dependency probes are required. Version must be confirmed against actual runtime version — not sourced from training data. |

> **All version numbers are marked TODO** because the tech analysis did not supply current or target version information. These must be populated from the actual project file (`.csproj`) before implementation begins.

---

## Infrastructure Changes

| Area | Change Required | Notes |
|------|----------------|-------|
| Docker base image | TODO — base image not specified in context | Verify the image exposes the health-check port; no base image change is expected for this feature. |
| Kubernetes liveness probe | TODO — k8s manifests not provided | Add `httpGet` probe targeting `/health` on the container port. |
| Kubernetes readiness probe | TODO — k8s manifests not provided | Add `httpGet` probe targeting `/health/ready` on the container port. |
| Load balancer / reverse proxy | TODO — not specified in context | Configure health-probe path to `/health` or `/health/ready` as appropriate. |
| CI/CD pipeline | Add integration-test step that asserts HTTP 200 from `/health` after deployment | TODO: identify pipeline tool (GitHub Actions, Azure DevOps, etc.) |

---

## Rollback Strategy

### Phase 1 — Discovery
- No code changes; nothing to roll back.

### Phase 2 — Implementation
1. Revert `Program.cs` / `Startup.cs` to remove `AddHealthChecks()` service registration.
2. Remove `MapHealthChecks(...)` middleware calls.
3. Delete any added `HealthChecks/` directory and custom check classes.
4. Remove the feature-flag key from `appsettings.json`.
5. Rebuild and redeploy — existing application behavior is fully restored.

### Phase 3 — Testing & Validation
- If a CI gate fails, the feature-flag remains `false` in production; no production impact.
- Revert test additions via PR close/revert if they introduce instability.

### Phase 4 — Deployment & Promotion
1. Set `FeatureFlags:HealthChecks = false` in production configuration — endpoint stops responding immediately without redeployment.
2. If a full revert is needed, redeploy the previous artifact (pre-Phase 2 build).
3. Remove or revert any Kubernetes probe configuration added in this phase to avoid probe failures on the rolled-back pod.

---

## Testing Strategy

### Unit Tests
- **Target:** Custom `IHealthCheck` implementations (e.g., `DatabaseHealthCheck.CheckHealthAsync`).
- **Tool:** TODO — confirm test framework (xUnit / NUnit / MSTest).
- **Coverage target:** 100% of custom check logic branches (healthy / degraded / unhealthy paths).

### Integration Tests
- **Target:** Full middleware pipeline; assert:
  - `GET /health` → HTTP 200 when application is running.
  - `GET /health/ready` → HTTP 200 when all "ready"-tagged checks pass; HTTP 503 when any fail.
- **Tool:** `Microsoft.AspNetCore.Mvc.Testing` (`WebApplicationFactory<T>`) — no external dependencies required.
- **Coverage target:** Both endpoint paths; both healthy and unhealthy states for each registered check.

### Regression Tests
- Verify no existing routes are shadowed or affected by the new endpoint registrations.
- Run full existing test suite as a regression gate.

### Performance Tests
- Health-check endpoints must respond within **< 200 ms** under normal load (typical SLO for probe endpoints).
- **Tool:** TODO — confirm if k6, NBomber, or similar is already in use.

### CI Gates
- All unit and integration tests must pass before merge to main.
- Health-check endpoint smoke test must pass in staging before production promotion.
- TODO: specify pipeline tool and gate configuration once CI/CD context is available.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Codebase audit complete; runtime/SDK version confirmed | 1 — Discovery | TODO | TODO |
| Feature-flag config key merged | 2 — Implementation | TODO | TODO |
| `AddHealthChecks` + `MapHealthChecks` merged | 2 — Implementation | TODO | TODO |
| Custom health-check probes implemented (if required) | 2 — Implementation | TODO | TODO |
| Unit + integration tests passing in CI | 3 — Testing | TODO | TODO |
| Staging validation complete | 3 — Testing | TODO | TODO |
| Feature flag enabled in production | 4 — Deployment | TODO | TODO |
| Kubernetes / load-balancer probes updated | 4 — Deployment | TODO | TODO |

> **All dates are TODO.** The upgrade option did not supply a person-days estimate, and the runtime/build context was not provided. Dates must be set once Phase 1 discovery is complete and team capacity is known.