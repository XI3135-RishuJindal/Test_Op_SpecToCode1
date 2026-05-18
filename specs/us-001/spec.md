US-001: Remove payment UI elements

What
- Remove and/or ensure absence of all payment-related UI components across this application. For this API repository, “UI components” map to HTTP endpoints (controllers/routes), visible API documentation (Swagger), and README guidance that would present or enable payment actions.
- Add automated guardrails so future changes cannot accidentally introduce payment UI artifacts.

Why
- The MVP is explicitly non-payment. Exposing any payment functionality or affordance creates compliance, scope, and user-expectation risks.

User Story
- As a product owner, I need the application to have no payment UI so that users cannot initiate or perceive payment-related actions in the MVP.

Scope and Interpretation for This Repository
- UI = API surface and documentation that are user-visible via Swagger or client integration.
- There are currently no payment controllers or views in this repository; this story confirms the absence and establishes automated checks.

Acceptance Criteria
- AC1: No endpoints, routes, or controllers related to payment exist.
  - No classes/files in Controllers/ named with Payment, Billing, Checkout, Pay.
  - No [Route] or [Http*] attributes containing payment, billing, checkout, pay.
- AC2: Swagger UI (when launched in Development) shows zero payment-related operations.
- AC3: README.md contains an explicit statement that the MVP ships without payment UI.
- AC4: An automated test in ApiGateway.Tests fails if any payment-related artifact appears in Controllers/.
  - Keyword set (case-insensitive): payment, payments, billing, checkout, pay.
  - The test scans file names, class names, and attribute strings within Controllers/.
- AC5: Build and test succeed locally and in CI with no payment UI artifacts detected.

Out of Scope
- Removing or altering any non-payment endpoints (Auth, Health, Test).
- Payment backend logic removal in other services or repositories.
- Data model changes unrelated to UI exposure.

Dependencies and Cross-Service Considerations
- None for this repository. Client/UI applications or other services must independently enforce the same policy.

Risks and Mitigations
- False positives from comments or documentation: keep the automated test scoped to Controllers/ and route attributes; do not scan documentation folders.
- Future feature growth: guard test prevents accidental regression; any payment feature requires a new spec and removal of this guard.