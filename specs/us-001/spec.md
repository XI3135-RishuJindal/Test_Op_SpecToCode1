Title
US-001: Remove payment UI elements

Why
Payments are out-of-scope for MVP. Any visible payment affordances (links, buttons, forms) or discoverable API/UI elements create scope creep and user confusion. We must ensure the application presents no payment UI.

Scope (this repository)
- Repo: XI3135-RishuJindal/Test_Op_SpecToCode1 (ApiGateway)
- This is an API gateway without front-end templates. We will:
  - Verify no payment-related discoverability via controller names, routes, Swagger metadata, or source files.
  - Add automated tests to prevent regressions.
  - No functional API changes required.

User story
As a Product Owner, I want to ensure there are no payment UI elements in the MVP, so that we maintain the focus on core functionalities.

Acceptance criteria
- AC1: No payment-related route segments, controller/action names, or Swagger operation metadata exist in the API Gateway. Forbidden tokens: payment, payments, payout, billing, invoice, invoices, checkout, creditcard, debitcard, cardnumber, cvv, stripe, paypal, applepay, googlepay, wallet.
- AC2: A guardrail test suite exists that fails the build if any forbidden token is found in:
  - Controller names, route templates, action method names, or HTTP verb attribute templates.
  - Source/content files (*.cs, *.cshtml, *.html, *.js, *.ts, *.css).
- AC3: No references to payment UI are present in repository documentation.
- AC4: Stakeholder sign-off confirming absence of payment UI discoverability for this repo.

Gherkin-ready scenarios
- Scenario: No forbidden tokens in controller and route metadata
  Given the ApiGateway assembly is loaded
  When scanning all ControllerBase types and their route/HTTP attributes
  Then no forbidden token is found in controller names, action names, or route templates

- Scenario: No forbidden tokens in source/content files
  Given the repository source files are scanned (*.cs, *.cshtml, *.html, *.js, *.ts, *.css)
  Then no forbidden token is found (case-insensitive)

Constraints
- Do not remove Swagger or auth endpoints; they are not payment UI.
- No changes to API contracts or behavior unless a payment element is detected (none expected).
- Tests must not require live network or external services.

Out of scope
- Removing payment backends, processors, or data models (none exist here).
- Feature flags for future payment enablement.
- UI changes in other repositories.

Dependencies and cross-repo notes
- Other UI/front-end repositories must also remove payment UI; tracked separately.
- This repo adds only automated checks; no cross-repo code dependency.

Definition of done
- All acceptance criteria pass.
- Guardrail tests are merged and run in CI.
- Documentation updated to state payments are out of MVP.