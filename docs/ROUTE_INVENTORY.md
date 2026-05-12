# API Route Inventory — US-003 Audit

Context
- Story: US-003 (JT-5951) — Audit API route inventory to confirm absence of payment endpoints and inbound webhooks.
- Generated: 2026-05-12T00:00:00Z
- Commit: <commit-sha-here>

Current HTTP routes (method and path)
- GET /api/health
- POST /api/auth/token
- POST /api/test (requires authorization)

Compliance statement
- No payment endpoints or inbound webhooks exist in the MVP.
- Verified against defined detection criteria (intent keywords such as payment, pay, billing, charge, checkout, invoice, refund, transaction, wallet, subscription, webhook/webhooks, callback; and provider keywords such as stripe, paypal, braintree, square, razorpay, adyen, mollie, authorize.net, worldpay). None of these appear in route paths, controller/action names, or package references.

Enforcement
- Automated tests located at Tests/Compliance/RouteInventoryTests.cs enumerate effective routes and scan package references to enforce this contract. Any violations will fail CI.