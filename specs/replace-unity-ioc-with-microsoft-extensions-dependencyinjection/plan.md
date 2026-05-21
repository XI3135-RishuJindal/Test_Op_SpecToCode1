# PLAN: Replace Unity IoC with Microsoft.Extensions.DependencyInjection

---

## Overview

**Migration Strategy: Strangler-Fig (incremental replacement)**

Unity IoC will be replaced with Microsoft.Extensions.DependencyInjection (MS.DI) incrementally, module by module, rather than in a single big-bang swap. This approach is chosen because:

- The upgrade urgency is **medium**, indicating the system is functional but accumulating tech debt — a full freeze for big-bang replacement is not justified.
- A strangler-fig pattern allows the application to remain deployable at each phase boundary, reducing release risk.
- Unity and MS.DI can coexist temporarily via an adapter/bridge pattern, allowing individual registration modules to be migrated and verified independently before Unity is fully removed.

> **Note:** Because the tech analysis does not specify the runtime, build tool, or framework versions, several infrastructure and tooling details are marked **TODO** below. These must be resolved during Phase 0 discovery before implementation begins.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| **0 – Discovery & Inventory** | Audit all Unity container registrations, resolve calls (`Resolve<T>`, `ResolveAll<T>`), lifetime configurations (`TransientLifetimeManager`, `ContainerControlledLifetimeManager`, `HierarchicalLifetimeManager`), and Unity-specific extensions (interceptors, child containers). Produce a registration map. | None | TODO (derive from registration count once inventory is complete) |
| **1 – Introduce MS.DI alongside Unity** | Add `Microsoft.Extensions.DependencyInjection` package. Create a new `ServiceCollection`-based composition root. Wire MS.DI as the primary container for **new** registrations only. No existing Unity registrations are moved yet. | Phase 0 complete | TODO |
| **2 – Migrate Registrations (module by module)** | Port each registration module from Unity `UnityContainer` / `IUnityContainer` to `IServiceCollection` extension methods. Replace lifetime managers with MS.DI equivalents (`Transient`, `Singleton`, `Scoped`). Remove Unity-specific factory delegates and replace with `ImplementationFactory` lambdas. | Phase 1 complete | TODO |
| **3 – Replace Resolve Call Sites** | Replace all `container.Resolve<T>()` / `container.ResolveAll<T>()` call sites with constructor injection or `IServiceProvider.GetRequiredService<T>()`. Eliminate service-locator anti-patterns where feasible. | Phase 2 complete | TODO |
| **4 – Remove Unity** | Delete Unity NuGet references (`Unity`, `Unity.Abstractions`, `Unity.Container`, any `Unity.*` extension packages). Remove `UnityConfig`, `UnityContainerExtensions`, and any bootstrapper classes that referenced `IUnityContainer`. Delete Unity configuration sections from `web.config` / `app.config` if present. | Phase 3 complete | TODO |
| **5 – Validation & Hardening** | Full regression test pass, performance baseline comparison, code review of composition root, update documentation. | Phase 4 complete | TODO |

> **Effort note:** The upgrade option is identified as "moderate" but person-day estimates were not provided in the supplied context. Effort cells are marked TODO and must be populated after the Phase 0 inventory is complete, as total effort scales directly with the number of Unity registrations and resolve call sites discovered.

---

## Component Changes

### Composition Root / Bootstrapper

- **What changes:** The central Unity bootstrapper (commonly named `UnityConfig`, `UnityContainerFactory`, `Bootstrapper`, or `DependencyConfig`) is replaced with an `IServiceCollection`-based composition root.
- **Files affected:** TODO — specific filenames not available from context; identify during Phase 0.
- **API modifications:**
  - Remove: `IUnityContainer`, `UnityContainer`, `new UnityContainer()`
  - Remove: `.RegisterType<TFrom, TTo>()`, `.RegisterInstance<T>()`, `.RegisterFactory<T>()`
  - Add: `IServiceCollection.AddTransient<TFrom, TTo>()`, `.AddSingleton<T>()`, `.AddScoped<T>()`, `.AddSingleton<T>(instance)`

### Lifetime Manager Mapping

| Unity Lifetime Manager | MS.DI Equivalent |
|------------------------|-----------------|
| `TransientLifetimeManager` | `AddTransient` |
| `ContainerControlledLifetimeManager` (singleton) | `AddSingleton` |
| `HierarchicalLifetimeManager` | `AddScoped` |
| `PerResolveLifetimeManager` | `AddTransient` (closest equivalent) |
| `PerThreadLifetimeManager` | TODO — no direct MS.DI equivalent; evaluate custom `IServiceScopeFactory` pattern |

### Resolve Call Sites

- **What changes:** All direct container resolution calls are replaced.
- **Files affected:** TODO — enumerate during Phase 0 inventory.
- **API modifications:**
  - Remove: `container.Resolve<T>()` → Replace with constructor injection (preferred) or `serviceProvider.GetRequiredService<T>()`
  - Remove: `container.ResolveAll<T>()` → Replace with `IEnumerable<T>` constructor injection
  - Remove: `container.IsRegistered<T>()` → Replace with `serviceProvider.GetService<T>() != null` or redesign

### Unity Interceptors / AOP (if present)

- **What changes:** Unity interception (`IInterceptionBehavior`, `VirtualMethodInterceptor`, `InterfaceInterceptor`) has no direct MS.DI equivalent.
- **Migration Notes:** TODO — if interceptors are in use, evaluate replacement with:
  - `Castle.DynamicProxy` + `Scrutor` for decoration
  - `Microsoft.Extensions.DependencyInjection` decorator pattern via `.Decorate<TService, TDecorator>()`
  - Middleware pipeline (if ASP.NET Core is the host)

### Child Containers (if present)

- **What changes:** Unity child containers (`CreateChildContainer()`) map to MS.DI `IServiceScope`.
- **Migration Notes:** Replace child container creation with `IServiceScopeFactory.CreateScope()`.

---

## Dependency Upgrade Plan

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| `Unity` (NuGet) | TODO — not specified in tech analysis | **Remove entirely** | Full removal | All registrations must be migrated before removal |
| `Unity.Abstractions` | TODO | **Remove entirely** | Full removal | `IUnityContainer` interface removed from codebase |
| `Unity.Container` | TODO | **Remove entirely** | Full removal | Core container removed |
| `Unity.*` extension packages | TODO | **Remove entirely** | Full removal | Enumerate all `Unity.*` transitive packages during Phase 0 |
| `Microsoft.Extensions.DependencyInjection` | Not present (new) | TODO — specify target version aligned to host framework version | N/A (new addition) | Use version compatible with target runtime; TODO — runtime version not specified in tech analysis |
| `Microsoft.Extensions.DependencyInjection.Abstractions` | Not present (new) | TODO | N/A (new addition) | Provides `IServiceCollection`, `IServiceProvider` abstractions |

> **Version note:** All target version numbers are marked TODO because the tech analysis did not supply current or target runtime/framework versions. These must be confirmed during Phase 0 and pinned before Phase 1 begins.

---

## Infrastructure Changes

TODO — The tech analysis does not specify Docker, Kubernetes, CI/CD pipeline, or IaC configuration. The following items should be investigated during Phase 0:

- **CI/CD pipeline:** TODO — confirm whether build scripts reference Unity package restore steps that need updating.
- **Docker base image:** TODO — not specified in context.
- **Kubernetes manifests:** TODO — not specified in context.
- **IaC:** TODO — not specified in context.
- **NuGet package source / lock files:** Ensure `packages.lock.json` or `packages.config` is updated when Unity packages are removed and MS.DI packages are added. Verify private feed configuration if Unity was sourced from an internal feed.

---

## Rollback Strategy

Each phase is independently reversible because Unity is not removed until Phase 4.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 0** | No code changes made; rollback is N/A. Discard inventory artifacts if project is cancelled. |
| **Phase 1** | Remove the newly added `Microsoft.Extensions.DependencyInjection` NuGet reference. Delete the new composition root file. Restore the original Unity bootstrapper entry point if it was modified. Revert via source control (`git revert` the Phase 1 commit range). |
| **Phase 2** | Revert migrated registration modules to their Unity equivalents via source control. Unity container is still present and functional. Re-enable Unity bootstrapper as the active composition root. |
| **Phase 3** | Revert resolve call-site changes via source control. Re-wire constructor injection removals back to `container.Resolve<T>()` calls. Unity container is still present. |
| **Phase 4** | Restore Unity NuGet packages from source control (`packages.config` / `.csproj` references). Restore deleted `UnityConfig` / bootstrapper files from source control history. Re-enable Unity configuration sections in `web.config` / `app.config` if they were removed. |
| **Phase 5** | No structural changes; rollback is N/A. Address any regressions found as bug fixes. |

**General principle:** Each phase should be committed to source control as a discrete, reviewable PR. This ensures any phase can be reverted with a single `git revert` without affecting other phases.

---

## Testing Strategy

### Test Pyramid

```
         [ Performance ]
        [ Regression / E2E ]
      [ Integration Tests ]
    [ Unit Tests ]          ← broadest base
```

#### Unit Tests
- **Scope:** Verify that individual classes receive their dependencies correctly via constructor injection after migration. No container involvement.
- **Tools:** TODO — test framework not specified in tech analysis (likely xUnit, NUnit, or MSTest; confirm during Phase 0).
- **Approach:** For each migrated class, assert that constructor parameters are satisfied and that behavior is unchanged. Use mocking (TODO — confirm Moq, NSubstitute, or FakeItEasy is available).
- **Coverage target:** Maintain or exceed existing unit test coverage baseline. TODO — establish baseline during Phase 0.
- **CI gate:** Unit tests must pass at 100% before any PR is merged.

#### Integration Tests
- **Scope:** Verify that the MS.DI composition root resolves the full object graph without errors. Catch missing registrations, circular dependencies, and lifetime mismatches.
- **Tools:** TODO — confirm integration test project exists.
- **Approach:**
  - Write a "container validation" test that calls `serviceProvider.GetRequiredService<T>()` for every root-level service registered in the composition root.
  - Use `IServiceCollection.BuildServiceProvider(validateOnBuild: true)` (MS.DI built-in validation) to catch scope violations at startup.
- **CI gate:** Integration tests must pass before Phase 2 is considered complete for each module.

#### Regression Tests
- **Scope:** Full application behavior must be unchanged after migration.
- **Tools:** TODO — confirm whether existing regression/E2E suite exists (Selenium, Playwright, Postman/Newman, SpecFlow, etc.).
- **Approach:** Run the full existing regression suite at the end of Phase 3 and Phase 5. Compare results against the pre-migration baseline captured in Phase 0.
- **CI gate:** Zero new regression failures permitted before Phase 4 (Unity removal) begins.

#### Performance Tests
- **Scope:** Confirm that container resolution time and application startup time are not degraded by the migration.
- **Tools:** TODO — confirm tooling (BenchmarkDotNet, k6, JMeter, etc.).
- **Approach:** Capture startup time and a representative set of resolution benchmarks under Unity (Phase 0 baseline). Re-run the same benchmarks after Phase 3. MS.DI is generally faster than Unity for standard scenarios; flag any regression > 10% for investigation.
- **CI gate:** Performance gate on startup time; TODO — define threshold after baseline is established.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Registration inventory and resolve call-site map complete | Phase 0 – Discovery | TODO | TODO |
| MS.DI package introduced; new composition root scaffolded | Phase 1 – Introduce MS.DI | TODO | TODO |
| All Unity registration modules ported to `IServiceCollection` | Phase 2 – Migrate Registrations | TODO | TODO |
| All `container.Resolve<T>()` call sites eliminated | Phase 3 – Replace Resolve Calls | TODO | TODO |
| Unity packages and bootstrapper code deleted; build green | Phase 4 – Remove Unity | TODO | TODO |
| Full regression pass complete; performance baseline confirmed | Phase 5 – Validation | TODO | TODO |

> **Timeline note:** All completion dates and owners are marked TODO. The upgrade option was identified as "moderate" but no person-day estimates were supplied in the provided context. Dates must be set after Phase 0 produces the registration inventory, which is the primary driver of total effort. Assign owners based on team structure at planning kickoff.