# CONSTITUTION
## Unity IoC → Microsoft.Extensions.DependencyInjection Migration

---

## Project Identity

**Name:** Unity IoC Replacement  
**Purpose:** Remove the Unity IoC container dependency and replace it with Microsoft.Extensions.DependencyInjection (MS.DI) across the codebase.  
**High-Level Goal:** Achieve a fully functional dependency injection setup using MS.DI, eliminating all Unity-specific APIs, configuration, and packages, while preserving existing application behaviour.

---

## Guiding Principles

1. **Prefer MS.DI lifetime semantics (`Transient`, `Scoped`, `Singleton`) over Unity-specific lifetime managers** because Unity lifetime managers (`ContainerControlledLifetimeManager`, `HierarchicalLifetimeManager`, etc.) have no direct runtime outside Unity and must be translated to avoid silent behavioural regressions.

2. **Prefer explicit service registration over convention-based or reflection-heavy auto-registration** because Unity's `RegisterTypes` with scanning can mask missing registrations; explicit registration makes the dependency graph auditable and testable.

3. **Prefer a single `IServiceCollection` composition root over multiple Unity child containers** because MS.DI does not natively support child containers, and replicating that pattern would re-introduce complexity the migration is intended to remove.

4. **Prefer compile-time resolution verification (integration tests against the built container) over runtime discovery of missing registrations** because Unity silently returns `null` or partial objects in some configurations; MS.DI throws at resolution time, so tests must catch this before production.

5. **Prefer incremental, module-by-module migration over a single big-bang swap** because the scope is moderate and a phased approach reduces regression risk and allows partial rollback if a module proves complex.

6. **Prefer removal of Unity NuGet packages as the final step** because keeping Unity present during migration allows side-by-side validation, but shipping with both containers is not an acceptable end state.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate option — TODO: confirm exact person-days once project sizing is complete |
| **Runtime / SDK** | TODO: confirm target .NET version; MS.DI requires .NET Standard 2.0+ or .NET Core / .NET 5+ |
| **Scope freeze** | Only Unity IoC replacement is in scope; no other framework upgrades, feature work, or architectural changes are permitted under this effort |
| **Package mandate** | `Microsoft.Extensions.DependencyInjection` (and `Microsoft.Extensions.DependencyInjection.Abstractions`) are the only permitted IoC packages post-migration; no third-party container adapters (Autofac, Lamar, etc.) unless explicitly approved |
| **Behaviour parity** | All existing registrations must resolve identically (same lifetimes, same named/keyed bindings where supported) after migration |
| **Named/keyed bindings** | MS.DI does not natively support named registrations; any Unity named registrations must be resolved via a documented pattern (factory delegate, keyed services in .NET 8+, or a small wrapper) — TODO: confirm .NET version to select correct approach |

---

## Quality Standards

| Standard | Measurable Bar |
|---|---|
| **Container smoke tests** | 100% of previously registered types must have a corresponding integration test that resolves the service from the built `IServiceProvider` without throwing |
| **Unit test pass rate** | All pre-existing unit tests must pass without modification (or with only Unity-specific test-helper replacements) |
| **No Unity references at ship** | Zero references to `Unity.*` namespaces or NuGet packages in the final merged code; enforced by a CI build step (e.g., `dotnet list package` grep) |
| **Code review** | Every registration module change requires at least one peer reviewer familiar with MS.DI lifetime rules |
| **Documentation** | A migration notes document must record every non-trivial lifetime or named-binding translation decision before the PR is merged |
| **Deployment gate** | No merge to the main branch until all container smoke tests and unit tests pass in CI |

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Adopt `Microsoft.Extensions.DependencyInjection` as the sole IoC container | Aligns with the stated modernization goal; MS.DI is the .NET ecosystem standard with long-term Microsoft support | Accepted |
| ADR-002 | Migrate incrementally by module rather than in a single commit | Moderate effort ceiling makes risk management essential; incremental approach enables partial rollback | Accepted |
| ADR-003 | Retain Unity packages until final validation pass, then remove | Allows side-by-side comparison of registration behaviour during migration | Accepted |
| ADR-004 | Named/keyed binding strategy to be decided based on confirmed .NET target version | .NET 8 `IKeyedServiceCollection` vs. factory-delegate pattern are materially different; decision deferred until runtime is confirmed | Proposed |
| ADR-005 | Target runtime version | TODO: confirm language, runtime, and build toolchain from project inventory | Proposed |