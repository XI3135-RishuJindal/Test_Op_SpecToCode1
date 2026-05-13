Title
US-001: Remove payment UI elements

Epic linkage
- Epic: EP-001
- JIRA: JT-5958 (30320)
- Story type: Functional

What
- Ensure the application exposes absolutely no payment UI elements in the MVP. This includes links, buttons, forms, or routes that would surface a payment capability in any UI or API documentation surface.
- For this repository (API Gateway, backend), enforce absence of payment-related API routes, tags, and names that could appear in Swagger or client generation as implicit UI elements.
- Add invariant tests that fail the build if controllers or routes contain payment-related terminology.

Why
- Maintain MVP scope focused on core functionality, explicitly excluding payment to reduce risk and complexity.

User story
As a Product Owner, I want to ensure there are no payment UI elements in the MVP, so that we maintain the focus on core functionalities.

Acceptance criteria
- No payment UI artifacts (links, buttons, forms) in any product UI.
- For this backend repository:
  - No payment-related routes, controllers, action names, or Swagger-visible paths containing banned payment terms.
  - Automated tests enforce the absence of banned payment terms in routes and known UI directories (if present).
- Stakeholder sign-off confirming no payment UI elements exist.

Gherkin-ready examples (repository-scoped)
- Scenario: No payment-related routes are defined
  Given the API assembly is scanned for controller and action routes
  When route templates and action names are compared to the banned terms list
  Then no matches are found

- Scenario: No payment UI assets exist
  Given standard UI folders (Views, Pages, wwwroot, ClientApp) are scanned if present
  When file contents are compared to the banned terms list
  Then no matches are found

Constraints
- Do not introduce stubs or placeholders for payment.
- Do not introduce feature flags pointing to payment features.
- Preserve existing non-payment behavior and tests.

Out of scope
- Removal or refactoring of backend payment domain logic in other services (none exists in this repo).
- Any UI-level repository changes (web/mobile apps) not included here; they are tracked separately.

Cross-repo dependency notes
- If separate web/mobile UI repositories exist, they must remove or omit any payment UI elements and pass equivalent guardrail tests.
- No known direct dependencies for this repo; this work is self-contained and preventive.

Definition of ready
- Business value documented: Payments excluded from MVP.
- Testable AC defined and captured as invariant tests.

Definition of done
- All AC pass; UI is free from payment elements; stakeholders sign-off.
- Guardrail tests merged and running in CI.