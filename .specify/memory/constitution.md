Quality principles
- MVP scope integrity: No payment functionality or UI must exist in the MVP. Prevent accidental introduction via invariant tests and policy checks.
- Simplicity: Prefer removal or omission over stubbing. Do not add placeholders such as “Payment coming soon.”
- Security and privacy: No collection, storage, or transmission of payment-related data. No PII in logs.
- Observability: Maintain structured logging; no logs should reference payment concepts.
- Backward compatibility: Do not introduce breaking changes to existing non-payment endpoints.
- Testability: Acceptance criteria must be Gherkin-ready and enforced by automated tests that fail on any payment UI artifact reintroduction.
- Documentation accuracy: README and specs must clearly state payments are excluded from MVP.

Tech guardrails
- Deny-list policy for payment-related UI terms enforced via tests (reflection on routes and optional static scan for UI asset folders).
- No new controllers, routes, or Swagger operations containing payment-related routes or names.
- Feature flags must not include or reference payment features.
- CI must run tests to enforce guardrails.

Coding standards
- Controllers: Attribute routing must be explicit and descriptive. Avoid ambiguous route segments that could be confused with payment (e.g., avoid “pay” abbreviations).
- Tests: Add invariant, non-functional tests that scan assemblies for forbidden patterns. Keep the forbidden term list centralized in a policy file.
- Configuration: No payment-related configuration keys (e.g., PaymentProvider, StripeKey).

Non-functional requirements
- Performance: New tests are lightweight and should add negligible runtime to the test suite.
- Reliability: Guardrail tests must be deterministic and not rely on network or environment.
- Maintainability: Centralized banned-term list to ease updates without code changes.
- Compliance: Exclude any references to payment platforms (Stripe, PayPal, Apple Pay, Google Pay, Adyen, etc.).