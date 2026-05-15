US-008: Create deferred Payments epic

Summary (WHAT)
Create and document a backlog epic for Payments that captures the problem statement, intended outcomes, prerequisites, deferrals, risks, non-functional requirements, and cross-service dependencies. The epic must be explicitly marked as out of scope for the current MVP and introduce no runtime behavior.

Why (business value)
- Clarifies the end-to-end scope of taking and managing payments without blocking the MVP.
- Aligns stakeholders on dependencies (identity, order/ledger, provider selection, compliance).
- Reduces delivery risk by front-loading constraints (PCI, idempotency, reconciliation).
- Enables progressive elaboration and sequencing for a later milestone.

Narrative
As a product and engineering team, we need a well-defined Payments epic that documents how customers will authorize, capture, refund, and reconcile payments, so that we can plan and de-risk future delivery without introducing any payment functionality in the current MVP.

Actors and stakeholders
- Customer: initiates and reviews payments/refunds.
- API Gateway: entry point for authenticated clients; no payment routes in MVP.
- Payment Orchestrator (new service, future): handles provider interactions and state.
- Finance/Ops: oversees reconciliation, disputes, settlements.
- External payment providers: Stripe/Adyen/Braintree, bank rails, webhooks.

In scope for this epic (documentation only)
- Proposed domain model (PaymentIntent, Payment, Refund).
- Proposed API surface (draft endpoints) to be implemented later.
- Prerequisites and deferrals list.
- Risk register and compliance considerations.
- Cross-service dependencies and sequencing plan.

Out of scope (for MVP and for this story)
- Any code that processes or exposes payment routes in API Gateway.
- Any data model or database schema changes.
- Provider integration code, keys, webhooks, or credentials.
- UI/payment form, card data collection, tokenization in the gateway.

Acceptance criteria
- The epic is documented at specs/create-deferred-payments-epic/spec.md with:
  - Problem statement, goals, non-goals.
  - Draft API endpoints and payloads (for reference only).
  - Domain concepts and state transitions at a high level.
  - Explicit statement: “Payments are out of scope for the current MVP.”
- A plan exists at specs/create-deferred-payments-epic/plan.md that:
  - Selects a target architecture (separate Payment Orchestrator behind the API Gateway).
  - Lists prerequisites with owners and sequencing.
  - Enumerates deferrals (what will NOT ship with the first payments release).
  - Identifies observability, reliability, and security controls.
- A disabled feature flag is introduced in appsettings.json under Payments.Enabled = false with Provider = "none"; no code paths read or act on it yet.
- README.md includes a “Payments Epic (Deferred)” section linking to these specs and reiterating the out-of-scope status.
- No new controllers, routes, or tests are added that expose payments.
- openspec/changes/api-gateway/tasks.md and openspec/changes/api-gateway/specs/spec