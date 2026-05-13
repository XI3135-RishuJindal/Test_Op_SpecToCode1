Title
Remove payment UI elements (US-001 / JT-5958)

Why
- To keep the MVP scope focused on core functionality and avoid incomplete or non-compliant payment experiences.
- To reduce risk and surface area by excluding payment UI and dependencies from builds and user journeys.

What (functional scope)
- Remove all payment-related UI from web and mobile clients:
  - Links, buttons, CTAs (e.g., “Billing”, “Upgrade”, “Subscribe”).
  - Forms, inputs, and validation for payment details (e.g., card details).
  - Routes/screens/pages dedicated to billing or subscription management.
  - Modals, toasts, empty states, and banners that reference payments.
- Remove client-side analytics/events related to payments.
- Remove or deprecate client-side API calls referencing payment endpoints; ensure none are invoked from UI code.
- Ensure navigation remains coherent after removals (no dead links).

User story
As a Product Owner, I want to ensure there are no payment UI elements in the MVP, so that we maintain the focus on core functionalities.

Acceptance criteria
- No payment UI (links/buttons/forms) on any screen.
- No navigation items/routes to billing or subscription flows.
- No client calls to payment endpoints triggered by UI actions.
- No payment-related analytics/logs emitted by clients.
- Build, lint, and tests pass with zero references to removed components.

Gherkin-ready acceptance tests
- Scenario: Payment CTAs are absent in navigation
  Given I am an authenticated user
  When I open the main navigation
  Then I do not see any items containing “Billing”, “Upgrade”, or “Subscribe”

- Scenario: Settings has no payment sections
  Given I am on the Settings screen
  Then I do not see any sections or links related to “Payment” or “Subscription”

- Scenario: Payment routes are inaccessible
  When I navigate directly to /billing or /subscribe
  Then I receive the standard 404 page

- Scenario: No payment inputs on any page
  Given I browse all available forms
  Then I do not find inputs for credit card details or payment methods

- Scenario: No payment analytics
  When I perform common user flows
  Then no analytics events with names containing “payment”, “billing”, or “upgrade” are emitted

Constraints
- Do not degrade non-payment features or navigation clarity.
- Do not introduce unused imports or broken type references.
- If a feature flag exists for payments, it must be disabled by default and excluded from bundles.
- Maintain a clean dependency graph; remove third-party payment SDKs only if not required by non-UI code paths.

Out of scope
- Removal of backend payment endpoints or domain logic (unless required by client build).
- Data migration or deletion of historical payment data.
- Pricing pages that purely describe plans without interaction may remain if explicitly non-transactional and approved by Product; otherwise remove links that suggest upgrading or paying.

Dependencies and cross-repo notes
- Web frontend: primary removal of components, routes, and analytics.
- Mobile app: remove screens and menu items; update deep links.
- API service: no functional changes required; optionally mark payment endpoints internal for clients.
- Docs: update user-facing docs to reflect absence of payment features.

Definition of Done
- All AC pass; UI is free from payment elements; stakeholders sign-off.
- CI green: type checks, lints, unit/e2e tests.
- Documentation updated; changelog entry added; removal inventory captured in PR.