# API Gateway — Change Tasks and Records

This document tracks scoped change records for the API Gateway. Entries must clearly state runtime impact and route changes. For MVP safety, documentation-only updates must not introduce any routes or behavior.

## Change Record: US-008 — Create deferred Payments epic (documentation-only)

- Type: Documentation-only change; no code, no routes, no runtime behavior.
- Summary: Register the Payments epic as deferred for MVP and point to its detailed specification and plan.
- Epic references:
  - Spec: ../../../specs/create-deferred-payments-epic/spec.md
  - Plan: ../../../specs/create-deferred-payments-epic/plan.md
- Runtime impact (MVP):
  - No controllers, handlers, or middleware added or modified.
  - No new API routes introduced; no changes to Swagger/OpenAPI in the gateway.
  - No behavior changes at runtime.
- Configuration note:
  - Introduce inert feature flags in configuration (documentation-only reference):
    - appsettings.json:
      - Payments.Enabled = false
      - Payments.Provider = "none"
  - No code paths read or act on these flags in MVP.
- Rationale:
  - Clarify deferred scope, dependencies, and risks without blocking MVP delivery.
- Verification:
  - Confirm no payment-related endpoints appear in Swagger.
  - Confirm no references to payments are executed at runtime.
  - Documentation links above are reachable in-repo.

Status: Recorded