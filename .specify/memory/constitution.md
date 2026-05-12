Quality principles
- Auditability as a first-class requirement: every API route must be discoverable, documented, and test-verifiable.
- Security by default: no payment-capable endpoints or inbound webhooks are permitted in MVP.
- Traceability: acceptance criteria must be enforced with automated tests that fail the build on violations.
- Minimal attack surface: expose only necessary routes; ban unsolicited callback/webhook surfaces.

Tech guardrails for this story
- Prohibited route intents: payment, billing, charge, checkout, invoice, refund, transaction, wallet, subscription, webhook(s), provider-specific (stripe, paypal, braintree, square, razorpay, adyen).
- Prohibited dependencies: any payment SDKs or webhook handler packages (e.g., Stripe.net, PayPalCheckoutSdk, BraintreeHttp, Square, Razorpay, Adyen).
- CI gate: unit tests must scan compiled controllers/actions and project package references to assert the absence of prohibited items.
- Documentation: maintain a human-readable route inventory artifact aligned with the codebase.

Coding standards
- Controllers must use attribute routing and follow the convention [Route("api/[controller]")] and method-level verb attributes.
- Route names are lowercase, hyphen-separated if adding segments (none added in this story).
- Do not add new controllers or endpoints for this story.

Non-functional requirements
- Evidence: a route inventory document exists and is up to date for the MVP.
- Repeatability: audits are automated via tests and run in CI.
- Observability: do not log secrets, tokens, PII; authentication flows already implemented remain unchanged.