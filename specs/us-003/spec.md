Story summary
- Jira: JT-5951 (30313)
- Story ID: US-003
- Type: Technical
- Title: Audit API route inventory
- As a Solution Architect, I want to audit the API route inventory, so that we confirm no payment endpoints or webhooks exist.

Problem/Why
- The MVP must not include any payment processing surfaces or inbound webhooks. We need an authoritative route inventory and automated guardrails to prevent accidental inclusion.

In-scope
- Produce a current inventory of all HTTP routes exposed by the API Gateway.
- Define criteria that classify payment- or webhook-related endpoints.
- Automate verification that no such endpoints or dependencies exist.
- Update repository documentation to include the route inventory.

Out of scope
- Adding, removing, or refactoring business endpoints unrelated to audit.
- Introducing payment capabilities or webhook frameworks.
- Modifying authentication/authorization flows.

Current route inventory (expected)
- GET /api/health
- POST /api/auth/token
- POST /api/test (requires authorization)

Acceptance criteria
- AC1: The documented API route inventory contains no endpoints whose path, controller, or action name match prohibited payment/webhook patterns.
- AC2: No package references in the API project include known payment/webhook SDKs.
- AC3: Automated tests enforce AC1 and AC2; CI fails on violation.
- AC4: Route inventory documentation is added and linked from the README.
- AC5: Stakeholder approval of the audit deliverable.

Payment/webhook detection criteria
- Route intent keywords (case-insensitive): payment, pay, billing, charge, checkout, invoice, refund, transaction, wallet, subscription, webhook, webhooks, callback.
- Provider keywords (case-insensitive): stripe, paypal, braintree, square, razorpay, adyen, mollie, authorize.net, worldpay.
- Project package names containing the above provider names.

Constraints
- No new externally accessible routes introduced by this story.
- Only tests and documentation changes are expected.

Dependencies
- None across repositories; changes confined to XI3135-RishuJindal/Test_Op_SpecToCode1.

Definition of Ready
- API routes documented and accessible for audit.
- Criteria for payment endpoints is defined (see above).

Definition of Done
- All acceptance criteria pass; updated documentation reflecting route inventory; stakeholder approval.