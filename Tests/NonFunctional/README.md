Purpose
- Enforce MVP scope by preventing accidental introduction of payment-related endpoints, routes, or action names in the API Gateway.

What this test covers
- Scans the ApiGateway assembly via reflection to ensure none of the following contain forbidden payment-related terms (case-insensitive):
  - Controller names
  - Class-level route templates ([Route] attributes)
  - Action method names
  - Method-level route templates (HttpGet/HttpPost/etc. attributes)

Forbidden terms
- payment, payments, billing, checkout, subscription, invoice, card, creditcard, stripe, paypal

How it works
- Tests/NonFunctional/NoPaymentEndpointsTests.cs uses reflection to find controllers and route templates implementing IRouteTemplateProvider. It fails the build with a clear list of violations if any forbidden terms are found.

Why reflection
- Keeps tests fast, deterministic, and independent of hosting, Swagger generation, or any external services.

How to run
- dotnet test

Maintenance
- Extend the ForbiddenTerms list if new prohibited terms are identified.
- Keep the test deterministic; do not introduce network or hosting dependencies.
- If a violation occurs, rename the offending controller/action or adjust the route template to remove the prohibited term.

Scope note
- This negative assurance test is the backend guardrail for the “Remove payment UI elements” MVP scope.
- Frontend repositories must also ensure no payment UI affordances exist.