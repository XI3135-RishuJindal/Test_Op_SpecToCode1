# Spec: HTTPS Enforcement, Health-Check Endpoint, and DataAnnotations Input Validation

---

## Summary

This spec covers three targeted security and reliability improvements to the existing web application: enforcing HTTPS for all incoming traffic, exposing a standardized health-check endpoint for infrastructure monitoring, and applying DataAnnotations-based input validation to API request models. The expected outcome is a more secure transport layer, observable service health, and consistent server-side rejection of malformed or invalid input — all without altering existing business logic or data models beyond what is strictly required.

---

## Motivation

| Driver | Detail | Urgency |
|---|---|---|
| Transport security | HTTP traffic is currently accepted without redirect or rejection, exposing sessions and credentials to interception. | Medium |
| Operational observability | No dedicated health-check endpoint exists; load balancers and orchestrators cannot reliably determine service liveness or readiness. | Medium |
| Input integrity | API endpoints accept and process unvalidated input, increasing risk of malformed-data errors and potential injection vectors. | Medium |

Upgrade urgency is rated **medium** per the provided tech analysis. No specific CVE identifiers or EOL dates were supplied in the tech analysis; see Open Questions.

---

## Current State

> **Note:** The tech analysis did not supply language, runtime, build tool, or framework version details. The items below describe the behavioural and interface state inferred from the task description. Specific class names, config keys, and schema elements are marked TODO where absent from context.

- **HTTPS enforcement:** The application currently accepts plain HTTP requests. No redirect middleware or HSTS header policy is configured. Relevant configuration key(s): TODO.
- **Health-check endpoint:** No `/health` or equivalent route exists. Infrastructure probes (load balancer, container orchestrator) have no dedicated target. Relevant startup/routing registration: TODO.
- **Input validation:** Request model classes exist but carry no DataAnnotations attributes (e.g., `[Required]`, `[MaxLength]`, `[Range]`). Validation is either absent or performed ad-hoc inside controller/handler logic. Affected model classes: TODO. Automatic model-state checking before handler execution is not confirmed to be enabled: TODO.

---

## Proposed Changes

| Component | Before | After | Breaking? |
|---|---|---|---|
| HTTP transport policy | HTTP requests accepted without redirect | All HTTP requests redirected to HTTPS; HSTS header applied to HTTPS responses | N — existing HTTPS callers unaffected; HTTP callers receive 301/308 redirect |
| Health-check endpoint | No endpoint exists | `GET /health` returns service liveness status and HTTP 200 (healthy) or HTTP 503 (unhealthy) | N — new surface, no existing route conflict (TODO: confirm no route collision) |
| Request model validation | No DataAnnotations on request models; no automatic validation gate | DataAnnotations attributes added to all request models; automatic validation returns HTTP 400 with error details on constraint violation | Y — callers sending previously-accepted invalid payloads will receive HTTP 400 |
| Validation error response shape | No standardised error body for invalid input | Consistent error response body returned on HTTP 400 (schema: TODO) | Y — callers must handle new 400 response body |

---

## Compatibility & Breaking Changes

### 1. HTTP → HTTPS Redirect
- **Change:** Plain HTTP requests receive a redirect response rather than being served directly.
- **Impact:** Clients that do not follow redirects or that construct absolute HTTP URLs will fail to reach the service.
- **Migration path for callers:** Update all client base URLs to use `https://`. Clients using standard HTTP libraries with redirect-following enabled require no code change.

### 2. Input Validation — HTTP 400 on Invalid Payloads
- **Change:** Request payloads that violate DataAnnotations constraints are rejected before reaching handler logic.
- **Impact:** Any caller currently sending payloads that omit required fields, exceed length limits, or violate range constraints will receive HTTP 400 instead of a processed (possibly erroneous) response.
- **Migration path for callers:** Callers must ensure payloads conform to the documented constraints. Constraint definitions for each model field: TODO.

### 3. Validation Error Response Body Shape
- **Change:** HTTP 400 responses will include a structured error body describing which fields failed and why.
- **Impact:** Callers that parse HTTP 400 response bodies must update their error-handling logic to match the new schema.
- **Migration path for callers:** Adopt the new error response schema (TODO — schema to be defined during implementation and published in API documentation).

---

## Acceptance Criteria

1. **Given** the service is running, **when** an HTTP request is sent to any endpoint, **then** the response status code is 301 or 308 and the `Location` header points to the equivalent HTTPS URL.

2. **Given** the service is running over HTTPS, **when** any HTTPS response is received, **then** the response includes a `Strict-Transport-Security` header with a `max-age` of at least 31536000 (one year).

3. **Given** the service is running, **when** a `GET /health` request is sent, **then** the response status code is 200 and the response body indicates a healthy state.

4. **Given** the service has a dependency that is unavailable (TODO: identify specific dependencies covered by the health check), **when** a `GET /health` request is sent, **then** the response status code is 503.

5. **Given** a request model field is annotated as required, **when** a request is submitted with that field absent or null, **then** the response status code is 400 and the response body identifies the missing field by name.

6. **Given** a request model field has a maximum-length constraint, **when** a request is submitted with a value exceeding that length, **then** the response status code is 400 and the response body identifies the offending field and constraint.

7. **Given** a request model field has a range constraint, **when** a request is submitted with a value outside that range, **then** the response status code is 400 and the response body identifies the offending field and constraint.

8. **Given** a fully valid request payload, **when** the request is submitted over HTTPS, **then** the response status code is not 400 and the request is processed normally by handler logic.

9. **Given** the CI pipeline runs, **when** all tests execute, **then** test cases covering criteria 1–8 above pass with no failures.

---

## Open Questions

| # | Question | Owner | Due Date |
|---|---|---|---|
| 1 | What is the specific runtime, language, and framework (including versions) in use? This is required to confirm the correct middleware/attribute APIs for HTTPS enforcement and DataAnnotations. | TODO | TODO |
| 2 | Are there any CVEs or EOL dates associated with the current transport or validation configuration that should be referenced in the Motivation section? | TODO | TODO |
| 3 | Which specific request model classes require DataAnnotations, and what are the field-level constraints for each? | TODO | TODO |
| 4 | What is the agreed error response body schema for HTTP 400 validation failures? | TODO | TODO |
| 5 | Does the health-check endpoint need to verify any downstream dependencies (database, cache, external services), or is a simple liveness ping sufficient? | TODO | TODO |
| 6 | Is there an existing route registered at `/health` that would conflict with the new endpoint? | TODO | TODO |
| 7 | Are there internal or legacy clients that send plain HTTP and cannot be updated to follow redirects? If so, a grace period or parallel-support policy may be needed. | TODO | TODO |
| 8 | Should HSTS preloading be enabled, and is the domain eligible for HSTS preload lists? | TODO | TODO |