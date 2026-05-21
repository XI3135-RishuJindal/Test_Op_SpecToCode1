# CONSTITUTION
## ASP.NET Web API 2 → ASP.NET Core Controller & Model Migration

---

## Project Identity

**Name:** ASP.NET Web API 2 to ASP.NET Core Migration
**Purpose:** Migrate existing controllers and models from ASP.NET Web API 2 to ASP.NET Core, replacing legacy `System.Web`-based hosting with the ASP.NET Core middleware pipeline.
**High-Level Goal:** Deliver a functionally equivalent API surface running on ASP.NET Core, eliminating dependency on the EOL Web API 2 / `System.Web` stack while preserving all existing route contracts and model behavior.

---

## Guiding Principles

1. **Prefer preserving existing route contracts over refactoring routes**, because breaking URL or HTTP-verb contracts would require coordinated changes in all API consumers, which is out of scope.
2. **Prefer direct attribute-routing equivalents over convention-based routing**, because Web API 2 projects typically rely on explicit `[Route]`/`[HttpGet]` attributes that map cleanly to ASP.NET Core equivalents with minimal risk.
3. **Prefer `Microsoft.AspNetCore.Mvc` controller base types over custom base classes**, because the legacy `ApiController` base class does not exist in ASP.NET Core; all controllers must derive from `ControllerBase` or `Controller`.
4. **Prefer incremental, controller-by-controller migration over a big-bang rewrite**, because the upgrade urgency is medium, allowing a staged approach that reduces regression risk.
5. **Prefer retaining existing model class structures over redesigning them**, because model changes introduce validation and serialization risk beyond the stated scope of this task.
6. **Prefer built-in ASP.NET Core model validation (`[ApiController]` + `ModelState`) over manual validation logic**, because the attribute automates 400-response behavior that previously required explicit `ModelState.IsValid` checks in Web API 2.

---

## Constraints

| Constraint | Detail |
|---|---|
| **Effort ceiling** | Moderate option selected; effort and timeline specifics are TODO — confirm person-days with project lead before planning begins. |
| **Target runtime** | TODO — confirm target .NET version (e.g., .NET 8 LTS). Must be an actively supported ASP.NET Core release. |
| **Scope freeze** | Limited to controllers and models only. Hosting infrastructure, authentication middleware, database layer, and client-side code are out of scope. |
| **Route contract freeze** | Existing API routes must not change. Any route change requires explicit sign-off. |
| **No new features** | No new endpoints or model fields may be introduced during this migration. |
| **Build tool** | TODO — confirm whether MSBuild/`dotnet CLI` target is already established in the receiving project. |

---

## Quality Standards

- **Functional parity:** Every migrated endpoint must return identical HTTP status codes, response shapes, and headers as the Web API 2 baseline for all documented inputs. Verified by integration tests before merge.
- **Test coverage floor:** Migrated controllers must have ≥ 80% line coverage via automated tests (unit + integration) at the time of PR submission.
- **No `System.Web` references:** CI pipeline must include a build-time check (e.g., grep or Roslyn analyzer) that fails if any `System.Web` namespace is referenced in migrated files.
- **Code review:** Every controller migration PR requires at least one reviewer with ASP.NET Core experience. No self-merges.
- **Regression gate:** All pre-existing passing tests must remain green. A PR that breaks existing tests cannot be merged regardless of new coverage.
- **Documentation:** Each migrated controller must have its public action methods documented with XML doc comments (`<summary>`) before the PR is considered complete.

---

## Decision Log

| ID | Decision | Rationale | Status |
|---|---|---|---|
| ADR-001 | Replace `ApiController` base class with `ControllerBase` + `[ApiController]` attribute | `ApiController` does not exist in ASP.NET Core; `[ApiController]` attribute restores automatic model validation and binding behaviors. | Accepted |
| ADR-002 | Migrate `HttpResponseMessage` return types to `IActionResult` / `ActionResult<T>` | `HttpResponseMessage` is a Web API 2 / `System.Web.Http` construct; ASP.NET Core uses `IActionResult` natively. | Accepted |
| ADR-003 | Replace `System.Web.Http` namespace imports with `Microsoft.AspNetCore.Mvc` | Direct namespace swap required for all controller and filter attributes. | Accepted |
| ADR-004 | Scope limited to controllers and models only | Hosting, auth, and data layers are separate concerns; mixing them increases risk and exceeds the moderate effort ceiling. | Accepted |
| ADR-005 | Target .NET version | TODO — pending confirmation of runtime target. | Proposed |