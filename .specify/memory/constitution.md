# CONSTITUTION

## Project Identity

**Name:** ASP.NET Core 8 SDK-Style Project Structure Migration

**Purpose:** Establish a modern, SDK-style project structure targeting ASP.NET Core 8, replacing or bootstrapping from the existing project layout.

**High-Level Goal:** Deliver a clean, buildable ASP.NET Core 8 SDK-style project scaffold that serves as the authoritative foundation for all subsequent modernization work.

---

## Guiding Principles

1. **Prefer SDK-style `.csproj` format over legacy/verbose project files** because SDK-style projects reduce XML noise, enable implicit file globbing, and are required for .NET 8 tooling compatibility.
2. **Prefer targeting `net8.0` explicitly over any unversioned or multi-target configuration** because the goal is a single, well-defined runtime target; ambiguity in TFM leads to inconsistent build behavior.
3. **Prefer minimal, framework-provided defaults over custom boilerplate** because ASP.NET Core 8's minimal hosting model reduces ceremony and aligns with current Microsoft guidance.
4. **Prefer preserving existing behavior over introducing new features** because this task is structural, not functional — scope creep risks destabilizing downstream work.

---

## Constraints

- **Timeline/Effort:** Moderate effort ceiling (exact person-days TODO — not provided in upgrade option). No gold-plating; structural work only.
- **Runtime Mandate:** Target framework must be `net8.0`. No downgrade to earlier TFMs is permitted.
- **Tooling Mandate:** Project files must use SDK-style format (`<Project Sdk="Microsoft.NET.Sdk.Web">`). Legacy `.csproj` or `packages.config` formats are not acceptable outputs.
- **Scope Freeze:** This task covers project structure only. Business logic changes, dependency upgrades beyond what the new scaffold requires, and feature additions are out of scope.
- **Source Language:** TODO — original language/runtime not confirmed in tech analysis. Verify before finalizing project type (`Sdk.Web` vs `Sdk`).

---

## Quality Standards

- **Build Gate:** The new project structure must produce a clean `dotnet build` with zero errors and zero warnings on a stock .NET 8 SDK installation before the task is considered complete.
- **No Orphaned Files:** All files included in the project must be reachable via SDK glob patterns or explicit `<Include>` entries; no stale references permitted.
- **Code Review:** At least one peer review required on the `.csproj`, `Program.cs`, and solution file before merge.
- **Documentation:** A `README` entry or inline comment must explain any non-default SDK property set in the project file.
- **No Secrets in Scaffold:** `appsettings.json` must contain only placeholder/structural content; no credentials or environment-specific values.

---

## Decision Log

| ID | Decision | Rationale | Status |
|----|----------|-----------|--------|
| ADR-001 | Use `Microsoft.NET.Sdk.Web` as the project SDK | Target is an ASP.NET Core 8 web project; this SDK provides web-specific defaults and tooling | Accepted |
| ADR-002 | Use minimal hosting model (`WebApplication.CreateBuilder`) in `Program.cs` | Aligns with ASP.NET Core 6+ conventions; reduces startup boilerplate | Accepted |
| ADR-003 | Set `<Nullable>enable</Nullable>` and `<ImplicitUsings>enable</ImplicitUsings>` | .NET 8 SDK defaults; omitting them would diverge from platform baseline | Accepted |
| ADR-004 | Original runtime/language stack left as TODO | Tech analysis reports runtime and language as unknown; must be confirmed before migration begins | Proposed |