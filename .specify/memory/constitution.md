Quality principles and guardrails for US-003 — Audit API route inventory

Scope and MVP boundaries
- MVP must not expose any payment or billing capabilities. No endpoints, webhooks, or 3rd-party payment vendor SDKs are permitted.
- No references to payment nomenclature (payment, payments, billing, checkout, stripe, paypal, braintree, square, adyen) in routes, Swagger, or package dependencies.

Security and privacy
- Authentication endpoints are limited to token issuance for local testing only; do not enable or add scopes related to payment operations.
- Authorization attributes must not be used to imply payment permissions or scopes.
- No secrets or payment keys in configuration or environment variables.

API and routing standards
- Attribute routing only; routes must be explicit and human-readable.
- Route templates should be lowercase and kebab/snake-case compatible; avoid business-domain leakage that is out of MVP scope.
- Swagger must not display payment-related categories/tags.

Observability
- Log any route inventory audit outcomes at info level.
- No PII or sensitive financial references in logs.

Testing and quality gates
- Add positive guardrails (unit tests) to fail CI if:
  - Any route contains banned segments: payment, payments, billing, checkout, webhook, webhooks, stripe, paypal, braintree, square, adyen.
  - Any dependency/package introduces payment SDKs by name.
- Snapshot-style inventory test must enumerate all routes via reflection so reviewers can verify the effective API surface.
- Tests should be deterministic and not rely on network or live runtime hosting.

Documentation and traceability
- Create and maintain openspec/audits/api-route-inventory.md listing all routes, methods, and auth requirements.
- PRs introducing routes must update the inventory document and pass guardrail tests.

Review expectations
- Reviewers verify the route inventory document matches reflection-derived inventory.
- Confirm no payment/webhook terminology in code, tests, comments, or docs.
- Ensure Swagger surface area matches inventory and excludes out-of-scope domains.

Non-functional requirements
- No functional behavior changes; this is an audit plus automated guardrails.
- Keep new tests fast (<2s locally).
- No new runtime dependencies; tests use reflection and file I/O only.