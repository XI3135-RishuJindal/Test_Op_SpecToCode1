# ApiGateway — Authoritative API Route Inventory

Current, approved public API surface for the MVP. Authentication requirements are inferred from [Authorize]/[AllowAnonymous] attributes.

Routes:
- GET /api/health — no auth
- POST /api/auth/token — no auth
- POST /api/test — auth required

Note:
- This inventory is maintained manually and is cross-checked by automated guardrail tests that validate the public API surface and fail the build if discrepancies or out-of-scope (e.g., payment-related) routes are introduced.