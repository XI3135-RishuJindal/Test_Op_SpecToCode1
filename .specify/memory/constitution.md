Principles and guardrails for US-003: Audit API route inventory

Quality principles
- Principle of least functionality: No payment-related capabilities (endpoints, routes, webhooks) are permitted in the MVP.
- Evidence-based verification: Route inventory must be generated from source-of-truth (controller attributes), not manual recollection.
- Repeatability: The audit must be enforceable by automated tests to prevent regressions.
- Security first: Prohibit accidental exposure of sensitive surfaces such as webhooks, callbacks, payment tokens, or PCI-adjacent terms.
- Traceability: Document inventory with commit SHA and date to anchor the snapshot in time.

Coding and review standards
- Naming: Avoid names or routes containing prohibited payment keywords (payment, payments, billing, checkout, invoice, card, stripe, paypal, webhook, hooks, callback, subscription, charge, refund).
- Controllers should be annotated explicitly with [ApiController] and route templates that do not introduce prohibited segments.
- All new controllers or HTTP actions must be covered by route inventory tests.
- Review checklist for PRs:
  - No payment/webhook-related endpoints added.
  - Route inventory tests pass.
  - Swagger paths do not include prohibited keywords.
  - Authz attributes are intentional and documented for any new routes.

Architecture guardrails
- API surface governance: Only explicitly required MVP endpoints are allowed. Disallow generic catch-all routes that could mask prohibited paths.
- Discovery approach: Prefer compile-time reflection of controller/action attributes to avoid environment-sensitive runtime enumeration.
- Observability: Log route audit results in tests to aid PR reviews.

Non-functional requirements
- CI gate: Tests enforcing prohibited routes must run as part of the test suite and fail fast on violations.
- Maintainability: Route scanner code should be small, dependency-light, and live in the test project.
- Documentation: Route inventory specification must be updated alongside functional changes to routes.

Stakeholder expectations
- Product: Written confirmation that no payment or webhook endpoints exist in the API Gateway for the MVP.
- Security/Compliance: Automated enforcement so prohibited endpoints cannot be merged.
- Engineering: Clear inventory of current routes with HTTP verb, path, and auth requirement.