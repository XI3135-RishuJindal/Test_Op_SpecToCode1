Architecture and approach
- This repository is an API Gateway (.NET 8) with no UI. We will enforce MVP scope via a non-functional test that prevents accidental introduction of payment-related endpoints or action names.
- Use reflection-based scanning over the ApiGateway assembly to:
  - Enumerate controllers ([ApiController] or ControllerBase-derived).
  - Inspect controller names, [Route] templates.
  - Inspect action method names and HttpMethodAttribute templates.
- Assert that none contain forbidden payment-related terms (case-insensitive).

Design decisions
- Reflection vs. live server:
  - Choose reflection to avoid coupling to hosting environment or Swagger generation. It’s fast and deterministic.
- Forbidden terms list is centrally defined in the test to be easily extended.
- We will not modify runtime code since current code has no payment references.

API contracts
- No changes to existing endpoints:
  - AuthController: POST /api/auth/token
  - HealthController: GET /api/health
  - TestController: POST /api/test (authorized)
- OpenAPI/Swagger behavior unchanged; tests guard against future payment routes.

Data model
- No changes.

Integration points
- None added. Tests run as part of ApiGateway.Tests.

Test strategy
- Unit-style non-functional test:
  - Scans ApiGateway assembly for forbidden terms in:
    - Controller type names.
    - Class-level [Route] templates.
    - Method-level HttpMethodAttribute templates.
    - Action method names.
  - Produces a clear violation list on failure.
- Optional extension (documented, not implemented here): A Swagger JSON scan test via Microsoft.AspNetCore.Mvc.Testing to examine generated paths and tags.

Risks and mitigations
- False positives: Keep forbidden list focused on payment domain. Use full-word substrings that are unlikely to clash. Provide actionable failure messages.
- Flakiness: Avoid hosting or network calls. Use pure reflection to keep tests stable and fast.

Rollout plan
- Commit tests and run CI.
- If failures occur (unexpected), investigate for accidental introduction of payment references.

Observability and Ops
- No runtime changes. CI will surface test failures if scope violations appear.