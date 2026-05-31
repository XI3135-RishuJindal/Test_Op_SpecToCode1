# Constitution – API Gateway Service (SVC-001)

This constitution defines enduring principles and guardrails for the API Gateway Service to guide all future changes, specs, and implementations.

## 1. Purpose & Scope

- Act as the **single, centralized entry point** for all client traffic (web, mobile, third-party) into the platform.
- Provide **consistent cross-cutting enforcement** of:
  - Zero Trust authentication & authorization (JWT/OAuth2/OIDC, RBAC/ABAC).
  - Rate limiting & throttling.
  - API versioning and routing.
  - Input validation & OWASP Top 10 mitigations.
  - Observability (logs, metrics, traces) and immutable audit trails.
- Proxy REST and WebSocket traffic to backend domain services (User Profile, MFA, Reporting, Payments, Notifications).

## 2. Quality & Architecture Principles

1. **Zero Trust by Default**
   - Every request is authenticated and authorized, regardless of origin or network zone.
   - No “trusted internal caller” shortcuts.
   - JWT/OIDC verification and RBAC must occur before routing or business logic.

2. **Stateless Gateway**
   - Gateway instances must remain stateless; any shared state (rate limits, token cache, MFA challenges) lives in Redis or other external stores.
   - Enables safe horizontal scaling and rolling upgrades.

3. **Defense in Depth**
   - Input validation and sanitization at the edge for all payloads and parameters.
   - CORS and security headers enforced globally.
   - Downstream services can assume validated, sanitized inputs but must still validate their own invariants.

4. **Separation of Concerns**
   - Clear layering:
     - Presentation: controllers, HTTP/WebSocket handling, middleware chain.
     - Application: routing, proxy, auth, RBAC, rate limiting, MFA orchestration.
     - Domain: route configs, policies, clients, audit events.
     - Infrastructure: Redis, Postgres, Kafka, OPA, Auth0/Keycloak, HTTP clients.
   - Cross-cutting concerns (logging, metrics, tracing, error normalization) live in shared components.

5. **Policy-as-Code & Config-Driven Behavior**
   - RBAC/ABAC policies, rate limits, and routing are **data**, not hard-coded logic.
   - Policies are managed centrally (OPA, Vault, config store) and reloaded without redeploys.
   - Admin APIs must safely allow dynamic updates (validation, audit, rollback capability).

6. **Resilience & Backpressure**
   - Circuit breakers, timeouts, retries with backoff for all upstream calls.
   - Rate limits tuned per endpoint class (auth, payments, admin, general).
   - The gateway should **fail fast** and surface clear, standardized errors, never silently degrade security.

7. **Observability & Auditability**
   - Every request gets a **requestId**; correlation IDs are propagated downstream.
   - Structured JSON logging with PII masking.
   - Metrics & traces are mandatory for:
     - Latency histograms per route.
     - Error and rate limit counters.
     - Upstream dependency health.
   - Security-sensitive actions must emit immutable audit events.

8. **Backward-Compatible Evolution**
   - Versioning via `/api/v{n}` path prefixes and/or headers.
   - Non-breaking changes preferred; breaking changes must go into new versions with deprecation headers and clear timelines.

## 3. Security & Compliance Guardrails

- **JWT/OIDC**
  - Only accept tokens from configured OIDC issuers (Auth0/Keycloak).
  - RS256 asymmetric signing; keys fetched via JWKS and cached with rotation support.
  - Enforce audience, issuer, expiry, and required claims.

- **MFA**
  - Login is a two-step flow (first factor → MFA verification).
  - No access/refresh token issuance before MFA completion.
  - Pluggable MFA strategies (TOTP, SMS, Email) behind the same contract.

- **RBAC/ABAC**
  - Fine-grained scopes and roles (user, admin, auditor, payment_manager, report_viewer).
  - Gateway **must** reject out-of-scope actions with 403, not 404, unless threat modeling requires resource-hiding.

- **Sensitive Domains**
  - Payment endpoints follow PCI-DSS: no PAN/CVV in any request, logs, or headers; only tokenized methods.
  - Idempotency for payments is mandatory; duplicate key conflicts must be clearly surfaced.

- **Transport Security**
  - TLS 1.3 for client-facing; minimum TLS 1.2 for service-to-service.
  - HSTS and modern secure headers enforced.

## 4. Performance & Scalability Principles

- Target **low-latency** request handling:
  - JWT validation with caching.
  - Efficient Redis usage (batching, Lua scripts for atomics).
- Avoid per-request blocking IO in the hot path where possible.
- Support WebSocket fan-out for notifications without starving regular HTTP traffic.
- Pagination and query bounds must be enforced at the edge to protect downstream services.

## 5. Error Handling & UX Principles

- Uniform error schema (aligned with `ErrorResponse` and/or RFC7807 Problem+JSON).
- Error messages:
  - Precise enough to guide clients.
  - Avoid leaking internal implementation or sensitive details.
- Use **specific** HTTP status codes (422 vs 400, 429 vs 503, 402 for payment declines).
- Deprecation communicated via standard headers and documentation links.

## 6. Technology Guardrails

- Runtime: Node.js / TypeScript with Express/NestJS-style architecture; or managed API gateway (Kong/AWS API Gateway) where defined.
- Data/Infra:
  - Redis: rate limits, token cache, MFA challenges.
  - Postgres (or equivalent): persistent configs (clients, routes, policies) where applicable.
  - Kafka (or equivalent): audit event sink.
  - OPA: externalized policy decisioning.
- Infra: Docker + Kubernetes for deployment; health/readiness endpoints must adhere to K8s expectations.

## 7. Testing & Validation Principles

- **Coverage Expectations**
  - Unit tests for middleware, routing, auth, RBAC, and rate limiting logic.
  - Contract tests against OpenAPI spec for all public endpoints.
  - Integration tests for critical flows: login+MFA, payments with idempotency, report scheduling, WebSocket notification session.

- **Security Testing**
  - Automated tests for known OWASP Top 10 vectors.
  - Regular pen-testing of the gateway endpoints.

- **Performance Testing**
  - Load tests for high-volume endpoints (auth, notifications, common profile reads).
  - Stress tests for rate limiting and circuit breaker behavior.

---

This constitution applies to all specs and plans under the API Gateway Service. Any deviation should be documented with rationale and risk assessment.

---