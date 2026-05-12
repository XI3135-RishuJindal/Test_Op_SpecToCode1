Quality principles
- MVP scope integrity: No payment-related user interface or discoverable surface area until explicitly reintroduced post-MVP.
- Least surprise: Remove/avoid affordances suggesting payment (buttons, links, forms, routes, tags).
- Safety by default: Add automated guardrails to prevent accidental reintroduction.
- Test-first: Guardrails must be enforced by unit/integration tests that fail builds when violated.
- Observability: Keep existing logs; do not add payment logs or events.
- Security: Do not include keys/providers for payment processors in configs.
- Documentation honesty: README and specs must not instruct or reference payment UI.

Tech guardrails
- Forbidden tokens in UI/API surface: payment, payments, payout, billing, invoice, invoices, checkout, creditcard, debitcard, cardnumber, cvv, stripe, paypal, applepay, googlepay, wallet.
- Swagger/OpenAPI: No paths/tags/operationIds containing forbidden tokens.
- Controllers and routes must not include forbidden tokens in names, attributes, or summaries.
- Static/web assets (html/cshtml/js/css) must not include forbidden tokens.
- Add test(s) that scan source and controller metadata for forbidden tokens.

Coding standards
- C# 12/.NET 8.0, nullable enabled, implicit usings enabled.
- Follow SOLID, small focused tests. No dead code, no commented-out payment placeholders.
- Logging via Serilog; no secrets or tokens in logs.
- Consistent naming; no “Payment*” types or members.

Non-functional requirements
- Build must fail if forbidden tokens are detected by tests.
- No runtime performance change expected.
- Maintain current test coverage; new tests must be deterministic and fast (<1s).
- No breaking API changes for non-payment functionality.