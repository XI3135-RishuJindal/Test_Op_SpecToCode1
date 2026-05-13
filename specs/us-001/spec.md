Title
Remove payment UI elements

Epic/Traceability
- Epic: EP-001
- Story: US-001 (JT-5958 / 30320)
- Type: Functional

Problem/Why
Payments are excluded from the MVP to keep focus on core capabilities. Any payment-related UI elements (links, buttons, forms) or implied support must be absent to avoid scope creep, user confusion, and compliance risks.

What (functional specification)
- Remove/avoid any payment-related UI affordances in all user-facing surfaces (web, mobile).
- Ensure backend public API surface does not expose payment-related endpoints that could be wired to UI inadvertently.
- Provide negative assurance tests in backend repositories to prevent accidental introduction of payment endpoints during MVP.

Acceptance criteria
- AC1: No payment UI (links/buttons/forms) on any screen.
- AC2: OpenAPI/Swagger for backend services must not contain paths or tags with payment-related terms: payment, payments, billing, checkout, subscription, invoice, card, creditcard, stripe, paypal.
- AC3: CI includes an automated test that fails if any controller name, route template, or action name contains forbidden payment-related terms.
- AC4: Stakeholders review and sign off that MVP shows no payment affordances.

Gherkin scenarios (conceptual; UI repos apply)
- Scenario: User cannot see payment options
  Given I am on any screen in the application
  Then I do not see any payment, checkout, or billing links, buttons, or forms

- Scenario: API does not expose payment endpoints
  Given the OpenAPI specification for the API Gateway
  Then there are no paths containing payment-related terms

Scope and constraints
- In-scope:
  - Backend negative assurance test to ensure no payment-related API endpoints are introduced in API Gateway.
  - Documentation of guardrails.
- Out-of-scope:
  - Implementing any alternative monetization or subscription flows.
  - Payment feature flags (they must not exist in MVP).
  - Data migrations (no payment data should exist).
- Constraints:
  - Do not break existing controllers/tests.
  - Keep test lightweight and independent of network or external services.

Cross-repo dependency notes
- Frontend web/mobile repos must remove payment UI. This spec only impacts XI3135-RishuJindal/Test_Op_SpecToCode1 by adding negative assurance tests and documentation.
- If other services expose OpenAPI, they must adopt a similar negative assurance test.

Definition of Ready
- Business value documented: Payments excluded from MVP.
- Testable acceptance criteria defined.

Definition of Done
- All AC pass.
- Test suite contains negative assurance checks and is green.
- Stakeholder sign-off that UI (in UI repos) is payment-free.