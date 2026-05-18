Title: Zero-Payment-UI Constitution for US-001

Purpose
- Enforce that the MVP ships with zero payment-related user interface elements. For this API-only repository, “UI elements” include any public/API affordance or documentation that exposes, hints at, or enables payment actions (e.g., controllers, routes, DTOs, Swagger-visible endpoints, README instructions).

Quality Principles
- Zero payment surface: No Payment/Billing/Checkout references in controllers, routes, public models, or API docs.
- Least surprise: Existing non-payment behavior remains unchanged; no regression to Health, Auth, Test endpoints.
- Security-first: No secrets in code; no logs suggesting payment flows.
- Observability: Logs remain informative but must not reference payment capabilities.
- Simplicity: Prefer guardrails (tests/policies) over complex conditional compilation or feature flags.

Coding Standards
- Naming: Do not introduce classes, files, routes, or namespaces containing Payment, Billing, Checkout, or Pay in user-exposed layers.
- API surface: Do not add payment-related DTOs, headers, query parameters, or response fields.
- Comments/docs: Avoid references implying future payment capabilities in user-facing docs; internal technical notes may track this spec only.
- Swagger: No tags or endpoints that could be construed as payment-related.

Architecture Guardrails
- No payment controllers or endpoints under Controllers/.
- No payment launch URLs or dedicated UI setup.
- Automated detection: Unit tests enforce the absence of payment UI artifacts in Controllers and route attributes.
- Backward compatibility: No changes to existing endpoints’ contracts.

Non-Functional Requirements
- Build integrity: dotnet build/test must pass locally and in CI.
- Test coverage: New policy test must execute in the ApiGateway.Tests project and fail on violations.
- Documentation: README explicitly states the MVP excludes payment UI.

Review Standards and Stakeholder Expectations
- PR checklist includes: zero payment UI verification, passing policy tests, README update.
- Stakeholders (PO/Eng Lead) validate acceptance criteria: no Swagger-visible payment endpoints; repository scan free of payment UI.
- Any later introduction of payment capabilities requires an explicit new spec and removal/adjustment of this constitution and tests.