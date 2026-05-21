# Tasks: Replace Unity IoC with Microsoft.Extensions.DependencyInjection

> **Scope:** Migrate all Unity IoC container registrations, resolution calls, and bootstrapping code to `Microsoft.Extensions.DependencyInjection` (MSDI). No other modernization work is in scope.

---

## Prerequisites

- [ ] [XS] Confirm target `Microsoft.Extensions.DependencyInjection` package version (e.g., 8.x) and record it in a `DECISIONS.md` file at the repo root
- [ ] [XS] Verify all developers and CI agents have .NET SDK installed at the version required to consume the chosen MSDI package
- [ ] [XS] Confirm write access to the main branch and permission to create feature branches and pull requests in the repository
- [ ] [XS] Identify and document every project (`.csproj` / solution) in the repository that references `Unity` or `Unity.Container` NuGet packages — record findings in `DECISIONS.md`

---

## Phase 1 — Preparation

- [ ] [XS] Create a long-lived feature branch `feature/replace-unity-with-msdi` from the current default branch
- [ ] [S] Audit all `.csproj` files for Unity-related package references (`Unity`, `Unity.Container`, `Unity.Abstractions`, `Unity.Microsoft.DependencyInjection`, `CommonServiceLocator`) and record exact versions in `DECISIONS.md`
- [ ] [S] Locate and list every file that contains `using Unity;`, `using Microsoft.Practices.Unity;`, `IUnityContainer`, `UnityContainer`, or `container.RegisterType` — output the list to `DECISIONS.md` as the migration inventory
- [ ] [S] Capture the current passing test suite as a baseline — record test count, pass rate, and code coverage percentage in `DECISIONS.md` before any code changes
- [ ] [XS] Configure a CI gate (pipeline step or branch protection rule) that fails the build if any Unity NuGet package reference is re-introduced after removal

---

## Phase 2 — Core Upgrade

- [ ] [S] Add `Microsoft.Extensions.DependencyInjection` and `Microsoft.Extensions.DependencyInjection.Abstractions` NuGet references to each affected `.csproj`, replacing Unity package references — do not remove Unity references yet
- [ ] [M] Create a new `CompositionRoot` class (or equivalent bootstrapper file) that builds an `IServiceCollection` / `ServiceProvider`, mirroring every `container.RegisterType` / `RegisterInstance` / `RegisterSingleton` call found in the Unity bootstrapper
- [ ] [M] Migrate constructor-injection registrations: replace all `container.RegisterType<IFoo, Foo>()` calls with `services.AddTransient<IFoo, Foo>()` (or `AddScoped` / `AddSingleton` as appropriate) in the new `CompositionRoot`
- [ ] [M] Migrate singleton and instance registrations: replace all `container.RegisterInstance<IFoo>(instance)` and `RegisterSingleton<IFoo, Foo>()` calls with `services.AddSingleton<IFoo, Foo>()` in `CompositionRoot`
- [ ] [S] Replace all `container.Resolve<IFoo>()` service-locator call sites with constructor-injected dependencies, updating affected class constructors and their registrations in `CompositionRoot`
- [ ] [S] Remove Unity-specific lifetime managers (`TransientLifetimeManager`, `ContainerControlledLifetimeManager`, `HierarchicalLifetimeManager`) and map each to the correct MSDI lifetime in `CompositionRoot`
- [ ] [S] Remove Unity interception / policy injection configuration blocks (if present in the bootstrapper) and document any AOP replacements needed in `DECISIONS.md`
- [ ] [S] Delete all `using Unity;` and `using Microsoft.Practices.Unity;` directives and remove `IUnityContainer` / `UnityContainer` type references from every file in the migration inventory
- [ ] [S] Remove all Unity NuGet package references from every `.csproj` file and confirm the solution builds cleanly with zero Unity dependencies

---

## Phase 3 — Testing & Validation

- [ ] [M] Update unit tests that directly instantiate or mock `IUnityContainer` — replace with `IServiceCollection` / `IServiceProvider` test doubles or `ServiceCollection` instances
- [ ] [S] Run the full test suite and compare pass count and coverage against the baseline recorded in `DECISIONS.md` — all previously passing tests must continue to pass
- [ ] [S] Perform a manual smoke test of each application entry point (e.g., startup, host builder, console main) to verify the `ServiceProvider` resolves the full object graph without runtime exceptions
- [ ] [XS] Confirm no `InvalidOperationException: Unable to resolve service` errors appear in application logs during smoke testing
- [ ] [XS] Run a `dotnet list package --include-transitive` check across all projects and verify zero Unity packages remain in the dependency graph

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [XS] Update the CI pipeline definition to remove any Unity-specific restore sources, environment variables, or build flags that are no longer needed
- [ ] [XS] Enforce the CI gate added in Phase 1 — confirm the pipeline fails on a test branch that re-introduces a Unity package reference, then remove the test branch

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `CHANGELOG.md` with a breaking-change entry describing the Unity → MSDI migration, listing removed packages and the new registration pattern
- [ ] [S] Update any developer onboarding or architecture documentation that references Unity container setup to reflect the new `CompositionRoot` / `IServiceCollection` pattern
- [ ] [XS] Open a pull request from `feature/replace-unity-with-msdi` to the default branch, request review from at least one other engineer, and address feedback
- [ ] [XS] After merge, monitor application logs and error-tracking tooling for any `InvalidOperationException` or dependency-resolution failures for a minimum of one business day post-deployment