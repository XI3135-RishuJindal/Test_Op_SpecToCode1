WHAT
- Create an authoritative inventory of all API routes exposed by the ApiGateway service and ensure no payment-related endpoints or webhooks are present in the MVP.
- Introduce automated guardrail tests that fail the build if any payment-related routes or SDK dependencies appear.
- Provide a human-readable document capturing current routes, methods, and authentication requirements.

WHY
- Prevent accidental inclusion of payment functionality in the MVP.
- Ensure future changes cannot regress by adding payment routes or dependencies.
- Provide clarity for downstream teams regarding the approved public API surface.

User story narrative
- As a platform architect, I need to audit the ApiGateway’s routes so that I can verify and enforce that no payment endpoints or webhooks are exposed in the MVP.

Current context summary
- Controllers present: AuthController (/api/auth/token), HealthController (/api/health), TestController (/api/test).
- No visible payment or webhook routes, and no payment SDK dependencies.

Acceptance criteria
1) Route inventory
- A document at openspec/audits/api-route-inventory.md lists every route with:
  - HTTP method
  - Path
  - Authentication requirement inferred from [Authorize] attributes
- Inventory reflects current code:
  - GET /api/health (no auth)
  - POST /api/auth/token (no auth)
  - POST /api/test (auth required)

2) Automated guardrails (tests)
- A unit test enumerates all controller routes via reflection and asserts:
  - No route contains any banned segments: payment, payments, billing, checkout, webhook, webhooks, stripe, paypal, braintree, square, adyen.
- A separate unit test asserts the ApiGateway.csproj does not contain package references or text containing the above banned terms.
- Tests run as part of the existing test project and fail fast with actionable messages.

3) Documentation hygiene
- README.md contains a link to the route inventory document and a brief note about the guardrail tests.
- Swagger shows only the inventoried endpoints; no payment-related tags or routes are present.

4) No functional changes
- No runtime behavior change is introduced; only tests and documentation are added/updated.

Out of scope
- Implementing, modifying, or removing business endpoints beyond the scope of documenting and asserting their presence/absence.
- Adding new API features or modifying authentication/authorization behavior.
- Creating or editing external CI pipelines beyond ensuring tests can run.

Dependencies and interactions
- Internal only; relies on .NET 8, xUnit, and reflection against the ApiGateway assembly.
- No external services or data stores impacted.