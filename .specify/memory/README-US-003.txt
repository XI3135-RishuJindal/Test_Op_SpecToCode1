US-003 internal memory note — Audit guardrails for payment/webhook surfaces

Context
- Jira: JT-5951 (30313)
- Story ID: US-003
- Title: Audit API route inventory
- Goal: Ensure the MVP exposes no payment processing endpoints and no inbound webhooks, and enforce this with automated guardrails.

Scope and intent
- In-scope: Auditing and documenting the current HTTP route inventory; asserting there are no payment/webhook routes; asserting there are no payment/webhook SDK dependencies; and documenting the inventory.
- Out-of-scope: Adding or refactoring business endpoints; introducing any payment or webhook frameworks; changing auth flows.
- Constraint: Do not add any new externally accessible routes as part of this story/MVP.

What the guardrails check (high level)
- Route scan: Reflect over controllers/actions to enumerate effective HTTP routes and assert none match prohibited patterns.
- Dependency scan: Parse ApiGateway.csproj to assert no package references include known payment/webhook provider tokens.
- CI behavior: These tests run in CI. Any violation fails the build.

Prohibited keywords used by tests (case-insensitive)
- Route intent keywords:
  payment, pay, billing, charge, checkout, invoice, refund, transaction, wallet, subscription, webhook, webhooks, callback
- Provider keywords:
  stripe, paypal, braintree, square, razorpay, adyen, mollie, authorize.net, worldpay
- Project package names are also checked for the above provider names.

Guardrail locations (files and docs)
- Tests:
  - Tests/Compliance/RouteInventoryTests.cs
    - Implements:
      - Reflection-based route enumeration across [ApiController] types with [Route]/Http{Verb} attributes.
      - Validation that controller names, action names, and resolved route templates do not contain prohibited keywords.
      - Xml/CSProj inspection of <PackageReference Include="..."> to ensure no provider SDKs are referenced.
- Documentation:
  - docs/ROUTE_INVENTORY.md
    - Human-readable API route inventory confirming no payment endpoints or webhooks in the MVP.

Guidance for contributors
- Do not introduce any routes, controllers, or action names that imply or implement:
  - Payments, billing, checkout flows, transactions, refunds, subscriptions, wallets, callbacks, or webhooks.
- Do not add SDKs or packages for payment or webhook providers (examples: Stripe.net, PayPalCheckoutSdk, BraintreeHttp, Square, Razorpay, Adyen).
- Any addition that includes the prohibited keywords in:
  - Route paths (e.g., /api/payment, /api/checkout, /api/webhooks/callback),
  - Controller/action names (e.g., PaymentController, CreateInvoice, WebhookHandler),
  - Package references (e.g., Stripe, PayPal, Braintree, Square, Razorpay, Adyen, Mollie, Authorize.Net, Worldpay),
  will cause the guardrail tests in Tests/Compliance/RouteInventoryTests.cs to fail, and thus fail CI.
- The MVP must not include any payment processing or inbound webhook surfaces. If your feature requires such capabilities, raise an architectural discussion and a new story outside this MVP scope.

Quick PR checklist (avoid CI failures)
- Verify no new route segments or names include: payment, pay, billing, charge, checkout, invoice, refund, transaction, wallet, subscription, webhook, webhooks, callback.
- Verify no references to provider names in code, configuration, or package references: stripe, paypal, braintree, square, razorpay, adyen, mollie, authorize.net, worldpay.
- Run tests locally (dotnet test) before pushing.

Rationale
- Security and scope control: Prevents expansion of the API surface into payments/webhooks during MVP.
- Auditability: Ensures every route is discoverable and verified.
- Repeatability: Guardrails run automatically in CI to catch regressions early.