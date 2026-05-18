Quality principles and guardrails for US-001: Remove payment UI elements

1) Purpose and scope
- This repository is an API Gateway (ASP.NET Core) without any front-end UI. The story’s objective is to guarantee that no payment-related UI constructs (links, buttons, forms) or discoverable API routes pertaining to payments exist, now or in future regressions.
- We enforce the objective through code-level constraints, contract reviews, and unit test guards.

2) Non-functional requirements
- Zero payment UI footprint: No Razor Views, Pages, wwwroot assets, or client-side code that references payments.
- Zero payment endpoints: No controllers, routes, or action methods that reference payments.
- Observability: Clear logs; no sensitive data exposure. No payment/token data should be logged because such data must not exist.
- Security: JWT auth as configured; no payment scopes/claims.
- Documentation: Repository documentation must explicitly state that payments are out of scope for MVP.

3) Coding standards and conventions
- Naming: Do not introduce classes, methods, namespaces, or routes that include payment-related terms (e.g., payment, payments, billing, checkout, card, subscription, invoice).
- API design: New endpoints must not imply or provide payment capabilities.
- Tests: Introduce “negative” guard tests that fail fast if payment-related constructs are introduced.

4) Architecture guardrails
- No front-end layer should be added to this API Gateway for payments. Any future UI or payment work requires a separate design/approval and MUST NOT land in this repo during MVP.
- Swagger/OpenAPI must not expose payment semantics. Adding such routes is prohibited.
- CI must run guard tests on every PR to prevent regressions.

5) Review and acceptance standards
- Code reviewers validate that no payment semantics are added in code or config.
- Guard tests exist and pass: they scan controller classes and route attributes for payment terms and validate absence of UI asset directories.
- Documentation updated to reflect the non-payment MVP stance.
- Any future proposal that impacts payments is out-of-scope and must be redirected.

6) Stakeholder expectations
- Product: MVP ships with no user payment experiences or payment endpoints.
- Security/Compliance: No PCI-related surface area in this repo.
- Engineering: Automated tests enforce constraints to minimize regressions.