Quality principles
- MVP scope fidelity: No payment functionality or UI must exist in the MVP. Any payment-related affordances are prohibited.
- Least surprise: Remove or hide any references that could imply payment capability.
- Explicit negative assurance: Add tests and CI checks that fail on accidental introduction of payment UI/back-end endpoints.
- Security and privacy: Never collect or expose payment or billing data. Avoid logging secrets or sensitive data.
- Observability: Keep structured logging; do not log secrets.
- Backward compatibility: Do not break existing non-payment APIs, tests, or integrations.
- Testability: Add deterministic, low-flake tests that assert absence of payment-related elements.

Tech guardrails
- Forbidden terms in public surface for MVP: payment, payments, billing, checkout, subscription, invoice, card, creditcard, stripe, paypal.
- OpenAPI/Swagger must not expose any endpoint path or tag containing these terms.
- UI repos (web/mobile) must not render payment-related links, buttons, forms, or menu items. Instead, show no element or a non-interactive placeholder only if explicitly approved.
- Configuration must not include payment provider keys, endpoints, or toggles that enable payment features.

Coding standards
- C#: Use nullable reference types, async/await, structured logging with Serilog.
- Controllers should be annotated with [ApiController] and explicit route attributes; keep routes descriptive and non-ambiguous.
- Do not leave commented-out payment code or TODOs implying future payment work within MVP code branches.
- Tests: Prefer reflection-based checks for negative assurance when the feature is intentionally absent.

Non-functional requirements
- Compliance: No storage or processing of PCI data.
- Performance: No change—MVP focus is non-payment; ensure added checks are lightweight.
- Reliability: Added tests must run in <2s locally/CI to avoid pipeline bloat.
- CI quality gates: Fail build if forbidden terms appear in API controller names, routes, or action names.