US-003: Audit API route inventory

What
- Produce a definitive inventory of all API routes exposed by the ApiGateway service and verify that no payment-related endpoints or webhooks are present in the MVP.
- Add an automated test guard that fails the build if any prohibited payment/webhook routes are introduced.
- Document the current inventory and governance rules to guide future PR reviews.

Why
- To ensure scope control and compliance: the MVP must not include any payment processing or webhook integration surfaces.
- To prevent regressions: a test-enforced contract is necessary to avoid accidental introduction of out-of-scope routes.

Context snapshot (from current source)
- Controllers/HealthController.cs
  - GET api/health (no auth)
- Controllers/AuthController.cs
  - POST api/auth/token (no auth; generates JWT for testing)
- Controllers/TestController.cs
  - POST api/test (requires [Authorize])
- Swagger is enabled only in Development (Program.cs).

Acceptance criteria
1) Route inventory artifact
- A documented list of all routes discovered from controller/action attributes that includes:
  - HTTP method, resolved route template, controller.action, and whether [Authorize] is required.
- The document is stored in-repo and references the commit SHA and date of inventory.

2) No payment/webhook routes present
- The inventory contains no endpoints whose controller name, action name, or route template contains any of the prohibited keywords (case-insensitive):
  - payment, payments, pay, billing, checkout, invoice, card, stripe, paypal, webhook, hooks, callback, subscription, charge, refund.
- If any are found, the story is blocked until they are removed.

3) Automated enforcement
- An xUnit test in the Tests project reflects over the ApiGateway assembly, resolves route templates, and fails if any prohibited keywords are detected.
- The test output includes a readable list of discovered routes for PR review logs.

4) Documentation
- This specification and the generated inventory are committed.
- README is updated with a short “Route Inventory Guard” note explaining the intent and where to find the inventory and test.

Out of scope
- Implementing or integrating any payment provider or webhook handler.
- Changing authentication/authorization logic beyond inventory and documentation.
- Non-API surfaces (e.g., message buses) unless they manifest as HTTP endpoints.

Dependencies and cross-service notes
- No external service dependency for the audit. Uses reflection on ApiGateway assembly.
- CI is assumed to run dotnet test; adding the test ensures gating without needing additional CI config.
- Swagger is not used for the guard (dev-only); reflection makes the guard environment-agnostic.