US-001 — Remove payment UI elements

What
- Ensure the application contains no payment-related UI constructs (links, buttons, forms) and no discoverable routes/endpoints that pertain to payments.
- Because this repository is an API Gateway without a front-end, “UI elements” translates into:
  - No web assets or view technologies (Razor Views/Pages, Blazor, wwwroot) that expose or imply payments.
  - No controllers, routes, or Swagger-exposed endpoints that indicate payment functionality.
- Introduce automated guardrails (tests) to prevent future introduction of payment UI/routes.

Why
- MVP is defined as non-payment. Eliminating any payment-related footprint reduces compliance scope, attack surface, and confusion for integrators.
- Guard tests institutionalize the constraint and avoid rework from accidental re-introduction.

User story narrative
- As a product owner, I need to ensure the MVP has no payment flows, screens, or endpoints so that we can ship a focused, low-risk first release.

Acceptance criteria
1) No payment endpoints
   - There are no controllers, route templates, or action names containing payment-related terms (case-insensitive: payment, payments, billing, checkout, card, subscription, invoice).
   - A unit test scans controllers and their Route/HTTP method attributes and fails if any such terms appear.

2) No payment UI assets
   - The repository contains no Views, Pages, Blazor, or wwwroot assets implementing or referencing payments.
   - A unit test asserts that no UI folders exist and that no .cshtml/.razor/.html files exist in the repo containing payment-related terms.

3) Documentation clarity
   - README explicitly states that payments are out of scope for MVP and that no payment UI or endpoints exist.

4) Regression prevention
   - The new guard tests are part of the test suite and run in CI (dotnet test). PRs introducing payment semantics will fail.

Out of scope
- Removing or altering payment logic in other repositories or services.
- Implementing feature flags for payment functionality.
- Introducing a front-end or modifying Swagger to add new documents. We only ensure no payment semantics are present.

Assumptions
- This API Gateway hosts controllers only; it does not include a UI layer.
- Tests can run with current solution structure; no additional infra is required.

Cross-service dependencies
- None directly. Front-end repositories must independently remove payment UI, but that is outside this repo and story.

Success metrics
- All guard tests pass; grep/search of repo controllers returns no payment terms.
- Build and test remain green with unchanged coverage for existing functionality.

Risks and mitigations
- Risk: False positives from permitted mentions in docs. Mitigation: Guard tests focus on code/routes and UI files only, not general docs except README scope statement.
- Risk: Inconsistent CI environment paths. Mitigation: Tests compute repo root relative to test assembly to check for UI folders safely.