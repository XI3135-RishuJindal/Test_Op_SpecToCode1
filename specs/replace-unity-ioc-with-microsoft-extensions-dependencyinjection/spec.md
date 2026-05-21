# Spec: Replace Unity IoC with Microsoft.Extensions.DependencyInjection

## Summary

This spec covers the replacement of the Unity IoC container with Microsoft.Extensions.DependencyInjection (MS.DI) as the application's dependency injection framework. The expected outcome is a codebase that registers, resolves, and manages object lifetimes exclusively through the MS.DI abstractions (`IServiceCollection`, `IServiceProvider`), with all Unity-specific packages, configuration, and runtime dependencies removed.

---

## Motivation

- **Unity IoC is effectively unmaintained.** The `Unity` and `Unity.Container` NuGet packages have seen no meaningful updates in several years, and the project has no active maintainers, creating long-term supply-chain and security risk.
- **No official security patch path.** Because Unity is community-archived, any future CVEs discovered in the container or its abstractions will not receive vendor patches.
- **Ecosystem alignment.** Microsoft.Extensions.DependencyInjection is the first-class DI container for .NET (Core / 5+) and ASP.NET Core. Adopting it removes friction when integrating with the broader Microsoft and ASP.NET ecosystem (hosted services, options pattern, health checks, etc.).
- **Upgrade urgency:** Medium — the application is not in immediate production crisis, but continued reliance on an unmaintained container increases technical debt and blocks future runtime upgrades.
- **Tech debt reduction.** Removing Unity eliminates a bespoke abstraction layer and reduces the number of third-party dependencies that must be audited.

> **Note:** Specific CVE identifiers and exact Unity package versions are not available in the provided context. See [Open Questions](#open-questions).

---

## Current State

> **Note:** Specific class names, config keys, and schema elements were not supplied in the context. The items below represent the canonical Unity surface area that must be audited in the actual codebase. Owners should annotate each item with concrete names during spec review.

### Container Bootstrap
- A Unity `IUnityContainer` instance is created at application startup (typically in a composition root, `Global.asax`, `Startup.cs`, or a dedicated bootstrapper class).
- Registrations are made via `container.RegisterType<TFrom, TTo>()`, `container.RegisterInstance()`, and/or `container.RegisterFactory()` calls.

### Lifetime Management
- Unity-specific lifetime managers are in use: `TransientLifetimeManager`, `ContainerControlledLifetimeManager` (singleton), `HierarchicalLifetimeManager`, and/or `PerResolveLifetimeManager`.

### Resolution
- Dependencies are resolved via `container.Resolve<T>()` or `container.ResolveAll<T>()` at call sites (service-locator pattern) and/or via constructor injection facilitated by a Unity-backed MVC/Web API dependency resolver.

### Framework Integration Points
- **TODO:** Confirm which integration packages are present (e.g., `Unity.AspNet.Mvc`, `Unity.AspNet.WebApi`, `Unity.Mvc5`, `Unity.WebAPI`, or similar) and the corresponding `IDependencyResolver` / `IHttpControllerActivator` implementations.

### Configuration
- **TODO:** Confirm whether any Unity XML configuration (`<unity>` sections in `web.config` / `app.config`) is in use.

### Abstractions / Interfaces Exposed to Callers
- **TODO:** List any application-defined interfaces that wrap or extend `IUnityContainer` (e.g., a custom `IContainer` facade).

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| DI container package | `Unity` / `Unity.Container` (version TODO) | `Microsoft.Extensions.DependencyInjection` | Y |
| Container abstraction used in code | `IUnityContainer` | `IServiceCollection` (registration) / `IServiceProvider` (resolution) | Y |
| Lifetime: transient | `TransientLifetimeManager` | `ServiceLifetime.Transient` | Y |
| Lifetime: singleton | `ContainerControlledLifetimeManager` | `ServiceLifetime.Singleton` | Y |
| Lifetime: scoped/hierarchical | `HierarchicalLifetimeManager` | `ServiceLifetime.Scoped` | Y |
| Lifetime: per-resolve | `PerResolveLifetimeManager` | `ServiceLifetime.Transient` (closest equivalent — see Compatibility) | Y |
| Framework integration package | `Unity.AspNet.Mvc` / `Unity.WebAPI` / etc. (TODO) | Framework-native DI integration (e.g., `Microsoft.Extensions.DependencyInjection` built-in ASP.NET Core integration, or `Microsoft.Extensions.DependencyInjection` adapter for legacy ASP.NET) | Y |
| Service-locator call sites | `container.Resolve<T>()` | Injected via constructor; or `IServiceProvider.GetRequiredService<T>()` where service-locator is unavoidable | Y |
| XML-based Unity config | `<unity>` config section (TODO — may not exist) | Removed; all registrations in code | Y |
| Custom `IContainer` facade (TODO) | Wraps `IUnityContainer` | Wraps `IServiceProvider` or removed in favour of direct MS.DI usage | Y |
| NuGet package references | Unity packages (TODO: enumerate) | `Microsoft.Extensions.DependencyInjection`, `Microsoft.Extensions.DependencyInjection.Abstractions` | N |

---

## Compatibility & Breaking Changes

| Breaking Change | Impact | Migration Path |
|---|---|---|
| `IUnityContainer` removed from all signatures | Any class that accepts or returns `IUnityContainer` must change | Replace with `IServiceProvider` for resolution or `IServiceCollection` for registration; prefer constructor injection over passing the container directly |
| `container.Resolve<T>()` call sites | Direct resolution calls will not compile | Refactor to constructor injection; where a service-locator is genuinely required, inject `IServiceProvider` and call `GetRequiredService<T>()` |
| `container.ResolveAll<T>()` | Bulk resolution pattern removed | Replace with `IEnumerable<T>` constructor injection, which MS.DI supports natively |
| Unity lifetime managers | All Unity `LifetimeManager` subclasses removed | Map to `ServiceLifetime` enum values per the table above |
| `PerResolveLifetimeManager` | No direct equivalent in MS.DI | Treat as `Transient`; validate that a new instance per resolution graph is acceptable, or introduce a custom `IServiceScope` pattern — TODO: confirm per-resolve semantics needed |
| Unity XML configuration | `<unity>` config section no longer parsed | Migrate all registrations to code-based `IServiceCollection` extension methods |
| Framework `IDependencyResolver` / `IHttpControllerActivator` | Unity-backed resolver removed | Replace with the appropriate MS.DI-backed resolver for the target framework (TODO: confirm framework version and available adapter) |
| Named / keyed registrations | Unity supports named registrations natively | MS.DI does not support named registrations in its base form; migrate to keyed services (available in .NET 8+ via `IKeyedServiceProvider`) or use a factory/strategy pattern — TODO: audit all named registrations |
| Interception / AOP via Unity | Unity supports call interception extensions | MS.DI has no built-in interception; migrate to a decorator pattern or a compatible AOP library — TODO: confirm whether Unity interception is in use |
| Child containers / `CreateChildContainer()` | Unity supports child container hierarchies | Replace with `IServiceScope`; validate that scope boundaries match the original child-container semantics — TODO: confirm usage |

---

## Acceptance Criteria

1. **Given** the solution is built from a clean checkout, **when** the build is executed, **then** it completes with zero errors and zero warnings related to Unity or missing DI registrations.
2. **Given** the updated codebase, **when** a static analysis or `grep`-equivalent scan is run for Unity package references (`Unity`, `Unity.Container`, `Unity.Abstractions`, and related integration packages), **then** no references are found in any project file or lock file.
3. **Given** the updated codebase, **when** a scan is run for `IUnityContainer`, `UnityContainer`, `UnityConfigurationSection`, and `LifetimeManager` type references, **then** no occurrences are found in production code.
4. **Given** the application is started, **when** the composition root executes, **then** all services are registered without exception and `IServiceProvider` is successfully built (i.e., `BuildServiceProvider()` or host build completes without error).
5. **Given** a request or operation that previously relied on Unity-resolved dependencies, **when** that operation is executed end-to-end, **then** all dependencies are resolved correctly and the operation completes with the same observable result as before the migration.
6. **Given** a singleton-lifetime service registration, **when** the service is resolved twice within the same application lifetime, **then** both resolutions return the same instance.
7. **Given** a scoped-lifetime service registration, **when** the service is resolved twice within the same scope and once in a separate scope, **then** the two resolutions within the same scope return the same instance and the resolution in the separate scope returns a different instance.
8. **Given** a transient-lifetime service registration, **when** the service is resolved twice, **then** two distinct instances are returned.
9. **Given** any previously named/keyed Unity registrations, **when** the equivalent keyed or factory-based resolution is invoked in the migrated code, **then** the correct implementation is returned for each key.
10. **Given** the full automated test suite, **when** all tests are executed against the migrated codebase, **then** the pass rate is equal to or greater than the pass rate recorded on the last commit before migration begins.
11. **Given** the application is running, **when** a scope is created and disposed (e.g., per HTTP request), **then** all `IDisposable` scoped services registered are disposed at scope boundary, with no resource leaks detectable in the test environment.
12. **Given** the CI pipeline, **when** a pull request is submitted containing any re-introduction of a Unity package reference, **then** the pipeline fails with a clear diagnostic message.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What are the exact Unity NuGet package names and versions currently referenced across all projects? | TODO | TODO |
| 2 | Which framework integration packages are in use (e.g., `Unity.Mvc5`, `Unity.WebAPI`, `Unity.AspNet.WebApi`)? | TODO | TODO |
| 3 | Is Unity XML configuration (`<unity>` section in `web.config`/`app.config`) present and active? | TODO | TODO |
| 4 | Are Unity named/keyed registrations in use? If so, how many and for which services? | TODO | TODO |
| 5 | Is Unity interception (AOP) used anywhere in the codebase? | TODO | TODO |
| 6 | Are child containers (`CreateChildContainer()`) used, and what are their intended scope semantics? | TODO | TODO |
| 7 | What is the target runtime and framework version (e.g., .NET Framework 4.x, .NET 6, .NET 8)? This determines which MS.DI features (e.g., keyed services) are available. | TODO | TODO |
| 8 | Are there any `PerResolveLifetimeManager` registrations, and is the per-resolve-graph semantic required or can transient be substituted? | TODO | TODO |
| 9 | Are there any application-defined interfaces or facades wrapping `IUnityContainer` that are exposed to external consumers or shared libraries? | TODO | TODO |
| 10 | Are there any CVEs currently tracked against the Unity packages in use that would elevate urgency? | TODO | TODO |
| 11 | Is there an existing integration test suite that exercises the DI composition root, or does one need to be created as part of this effort? | TODO | TODO |