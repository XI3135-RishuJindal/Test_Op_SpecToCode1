# US-008: Deferred Payments Epic — Specification

Summary (WHAT)
Create and document a backlog epic for Payments that captures the problem statement, intended outcomes, prerequisites, deferrals, risks, non-functional requirements, and cross-service dependencies. The epic must be explicitly marked as out of scope for the current MVP and introduce no runtime behavior.

Explicit scope statement
“Payments are out of scope for the current MVP.”

Problem statement
We will need to securely accept, authorize, capture, refund, and reconcile customer payments across providers in a future milestone. Today, the MVP must launch without any payment processing surface area or runtime behavior, but we need a clear and shared understanding of the future Payments scope, risks (PCI, idempotency, reconciliation), dependencies (identity, order/ledger, provider selection, compliance), and non-functional requirements to reduce delivery risk and enable sequencing.

Goals
- Establish a clear domain model for payments (PaymentIntent, Payment, Refund) and high-level state transitions.
- Define a reference-only API surface for future implementation, explicitly not part of the MVP.
- Identify prerequisites, deferrals, risks, and compliance considerations to de-risk delivery.
- Map cross-service dependencies and outline a sequencing plan for a later milestone.

Non-goals
- No runtime code, controllers, routes, database schemas, provider credentials, or webhooks in the MVP.
- No commitment to a specific payment provider integration in the MVP.
- No UI/payment forms or card data collection pathways in the API Gateway in the MVP.
- No stateful components or infrastructure provisioning for payments in the MVP.

Actors and stakeholders
- Customer: initiates and reviews payments/refunds.
- API Gateway: entry point for authenticated clients; no payment routes in MVP.
- Payment Orchestrator (new service, future): coordinates provider interactions and lifecycle.
- Finance/Ops: reconciliation, settlements, disputes, reporting.
- External providers: PSPs (e.g., Stripe/Adyen/Braintree), bank rails; send webhooks for state changes.
- Compliance/Security: oversee PCI-DSS, SCA/PSD2, data protection.
- Data/BI: reporting and analytics on payment outcomes and reconciled data.
- Customer Support: investigates payment issues, refunds, and disputes.

Proposed domain model and concepts
- PaymentIntent
  - Purpose: Represents the intent to collect a specific amount from a customer using a selected payment method, typically created before authorization.
  - Key attributes: id, orderId, currency, amount, customerId, paymentMethodHint/tokenRef, providerSelection, status, expiresAt, idempotencyKey, metadata.
  - Status (high-level transitions):
    - created → requires_authorization
    - requires_authorization → authorized | requires_action (e.g., 3DS) | failed | canceled | expired
    - requires_action → authorized | failed | canceled | expired
    - authorized → canceled (pre-capture) | expired (if not captured within window)

- Payment
  - Purpose: Represents an authorization and/or captured funds against a PaymentIntent.
  - Key attributes: id, paymentIntentId, providerChargeId, currency, amountAuthorized, amountCaptured, captureMode (automatic|manual), status, capturedAt, failureReason, metadata, auditTrail.
  - Status (high-level transitions):
    - pending → authorized | failed
    - authorized → captured | canceled | expired
    - captured → refunded_partially | refunded | chargeback
    - refunded_partially → refunded (after final refund) | chargeback
    - failed, canceled, expired are terminal for the authorization flow

- Refund
  - Purpose: Returns funds to the customer for a captured Payment (full or partial).
  - Key attributes: id, paymentId, providerRefundId, amount, currency, reason, status, createdAt, processedAt, failureReason, metadata.
  - Status (high-level transitions):
    - pending → succeeded | failed | canceled

Reference API surface (DO NOT IMPLEMENT IN MVP)
Important: The following endpoints and payloads are reference-only to align stakeholders on the intended future design. DO NOT IMPLEMENT IN MVP. No routes must be added to the API Gateway at this time.

Conventions
- Base path (future): /payments
- Versioning: v1 in future (e.g., /v1/payments)
- Idempotency: All write operations require an Idempotency-Key header.
- Auth: JWT with granular scopes (future).
- Errors: Standardized error schema with internal taxonomy (future).

1) Create PaymentIntent (reference only)
- POST /payments/intents
- Headers: Idempotency-Key: <uuid>
- Request:
  {
    "orderId": "ord_123",
    "amount": 4999,
    "currency": "USD",
    "customerId": "cus_789",
    "captureMode": "manual",
    "paymentMethodHint": "card",
    "metadata": { "source": "web", "campaign": "spring" }
  }
- Response 201:
  {
    "id": "pi_abc",
    "orderId": "ord_123",
    "amount": 4999,
    "currency": "USD",
    "status": "requires_authorization",
    "captureMode": "manual",
    "expiresAt": "2026-05-22T12:00:00Z",
    "clientSecrets": { "publicToken": "seti_..." },
    "metadata": { "source": "web", "campaign": "spring" }
  }

2) Authorize or create Payment (reference only)
- POST /payments
- Headers: Idempotency-Key: <uuid>
- Request:
  {
    "paymentIntentId": "pi_abc",
    "paymentMethodToken": "pm_tok_123",
    "amount": 4999,
    "currency": "USD",
    "confirm": true
  }
- Response 201:
  {
    "id": "pay_123",
    "paymentIntentId": "pi_abc",
    "status": "authorized",
    "amountAuthorized": 4999,
    "amountCaptured": 0,
    "provider": "stripe",
    "providerChargeId": "ch_456",
    "nextAction": null,
    "createdAt": "2026-05-15T10:00:00Z"
  }

3) Capture Payment (reference only)
- POST /payments/{id}/capture
- Headers: Idempotency-Key: <uuid>
- Request:
  {
    "amount": 4999
  }
- Response 200:
  {
    "id": "pay_123",
    "status": "captured",
    "amountAuthorized": 4999,
    "amountCaptured": 4999,
    "capturedAt": "2026-05-15T10:10:00Z"
  }

4) Refund Payment (reference only)
- POST /payments/{id}/refunds
- Headers: Idempotency-Key: <uuid>
- Request:
  {
    "amount": 2000,
    "reason": "customer_request",
    "metadata": { "ticketId": "ts_001" }
  }
- Response 201:
  {
    "id": "rf_789",
    "paymentId": "pay_123",
    "status": "pending",
    "amount": 2000,
    "currency": "USD",
    "createdAt": "2026-05-15T10:20:00Z"
  }

5) Get Payment (reference only)
- GET /payments/{id}
- Response 200:
  {
    "id": "pay_123",
    "paymentIntentId": "pi_abc",
    "status": "captured",
    "amountAuthorized": 4999,
    "amountCaptured": 4999,
    "provider": "stripe",
    "providerChargeId": "ch_456",
    "history": [
      { "at": "2026-05-15T10:00:00Z", "event": "authorized" },
      { "at": "2026-05-15T10:10:00Z", "event": "captured" }
    ]
  }

6) Get Refund (reference only)
- GET /refunds/{id}
- Response 200:
  {
    "id": "rf_789",
    "paymentId": "pay_123",
    "status": "succeeded",
    "amount": 2000,
    "currency": "USD",
    "processedAt": "2026-05-15T10:25:00Z"
  }

Prerequisites (for future implementation)
- Identity/Auth:
  - JWT scopes and roles for payments (create_intent, authorize, capture, refund, read).
  - Service-to-service auth between API Gateway and Payment Orchestrator.
- Order/Ledger:
  - Stable Order domain with amounts, currency, taxes, discounts.
  - Financial ledger or accounting integration for postings, settlements, and refunds.
- Provider selection:
  - Evaluate PSP(s) for initial launch (e.g., Stripe vs Adyen).
  - Sandbox accounts, API keys/secrets in centralized secret store.
- Compliance and security:
  - PCI-DSS scoping decision and boundary definition (avoid scoping API Gateway if possible).
  - Data protection impact assessment; GDPR data minimization and retention policy.
  - Webhook signature verification design.
- Infrastructure:
  - Eventing/messaging for outbox/inbox and webhook processing (DLQ support).
  - Observability blueprint (traces/metrics/logs, correlation IDs).
- Financial operations:
  - Reconciliation process (automatic vs manual), provider reports ingestion.
  - Dispute/chargeback handling process.

Deferrals (not in first payments release)
- Multi-provider smart routing and failover.
- Stored payment methods and vaulting (cards on file).
- Partial capture (beyond single full capture).
- SCA/3DS2 flows and challenge handling.
- ACH/bank transfer, SEPA, local payment methods.
- Subscriptions/recurring billing, scheduled payments.
- Complex split settlements/marketplace payouts.
- Multi-currency presentment and conversion.
- Advanced fraud scoring and risk rules.

Risk register (selected)
- PCI scope creep:
  - Risk: Accidental introduction of card data into API Gateway or logs.
  - Mitigation: Tokenization with provider vault; strict logging hygiene; architectural boundary to keep Gateway out of PCI zone.
- Idempotency and duplicate charges:
  - Risk: Retries cause double authorization/capture.
  - Mitigation: Idempotency-Key on all write operations; outbox pattern; provider idempotency usage.
- Reconciliation gaps:
  - Risk: Settlement reports mismatch; manual write-offs.
  - Mitigation: Daily automated reconciliation; immutable audit trail; exception queue.
- Webhook reliability and ordering:
  - Risk: Out-of-order or missing webhooks corrupts state.
  - Mitigation: