---
Title: API Gateway PCI DSS Scope Statement (MVP)
Version: 1.0
Owner: Rishu Jindal (Security/Compliance Lead)
Approvers:
  - Product Owner
  - Engineering Lead
  - Security/Compliance Lead
  - DevOps Lead
Effective Date: 2026-05-15
Next Review: 2026-08-15
---

1) Executive summary
- Assertion: No CHD/SAD is stored, processed, or transmitted by the MVP.
- Scope position: The current API Gateway MVP is out of PCI DSS scope. The system provides authentication, health, and test utility endpoints only. There are no payment endpoints, no PSP integrations, and no code paths that accept, proxy, or log cardholder data.

2) Definitions
- Cardholder Data (CHD)
  - Primary Account Number (PAN)
  - PAN in combination with any of: cardholder name, expiration date, service code
- Sensitive Authentication Data (SAD) — must never be stored after authorization
  - Full track data (Track 1, Track 2, magnetic-stripe or equivalent on chip)
  - CAV2/CVC2/CVV2/CID (card verification values/codes)
  - PIN and PIN block

3) Current architecture and data flows
- Component: API Gateway (this repository) built on ASP.NET Core 8 with:
  - Authentication endpoint issuing test JWT tokens
  - Health endpoint for service liveness
  - Test endpoint demonstrating request/response handling
  - Swagger for API exploration in development only
  - Serilog sinks for console and file logging (metadata/events only)
- Data flows:
  - Client -> API Gateway (HTTPS/TLS 1.2+) for JWT issuance and test operations
  - No payment providers, PSP redirects, or tokenization services are integrated
  - No databases or queues persist or transport payment data in this MVP
- There are no routes, models, or background jobs that accept CHD/SAD.

4) Scope boundaries
- In scope (for this statement and evidence review):
  - Source code, configuration, and build artifacts under this repository
  - Runtime configuration in appsettings.json and appsettings.Development.json
  - Controllers: AuthController, HealthController, TestController
  - Dependency manifests: ApiGateway.csproj, Tests/ApiGateway.Tests.csproj
  - Logging configuration and usage (Serilog integration)
- Explicitly out of scope (not present in MVP):
  - Any storage, processing, or transmission of CHD/SAD
  - Any payment pages, “checkout” flows, or direct PSP integrations (e.g., Stripe, Adyen, Braintree, Checkout.com)
  - Any server-side acceptance or proxying of PAN/cvv/expiry/track data or PINs

5) Evidence
5.1 Code search for CHD/SAD indicators
- Method: Searched repository for common CHD/SAD terms and patterns.
- Terms/patterns: cardNumber, pan, cvv, cvc, expiry, track1, track2, pin, payment, checkout
- Example command:
  - grep -Rni -E "(cardNumber|[^a-z]pan[^a-z]|cvv|cvc|expiry|track1|track2|[^a-z]pin[^a-z]|payment|checkout)" .
- Result: None relevant to CHD.
  - No occurrences of PAN, CVV/CVC, expiry fields, track data, PIN/PIN block, or payment/checkout flows.
  - False positives: none observed.

5.2 Endpoint inventory (from Controllers)
- AuthController
  - POST /api/auth/token — issues a demo JWT; does not accept or process any CHD/SAD.
- HealthController
  - GET /api/health — returns service status; no request body; no CHD/SAD.
- TestController
  - POST /api/test — requires JWT; accepts a TestRequest with message and optional MedicationDTO; no fields resembling CHD/SAD.
- Confirmation: None of the above endpoints handle payments, card data, or checkout flows.

5.3 Logging and configuration review
- Program.cs configures Serilog with Console and File sinks. There is no Serilog RequestLogging middleware enabled and no custom middleware that logs HTTP request or response bodies.
- Controllers log metadata (e.g., requestId, route-level status). No code logs full request bodies, headers, or sensitive payloads. The TestController logs the Message field only; there are no CHD-like fields in any model.
- appsettings.json and appsettings.Development.json contain:
  - Standard Logging levels, JWT settings, and Serilog MinimumLevel configuration
  - No payment-related configuration keys or endpoints
  - No telemetry settings that capture payload content
- Production posture: Request/response bodies are not logged. There are no configurations enabling body capture in production.

5.4 Third-party dependency review
- ApiGateway.csproj packages:
  - Microsoft.AspNetCore.Authentication.JwtBearer (JWT)
  - Microsoft.AspNetCore.Authorization
  - Serilog.AspNetCore, Serilog.Sinks.Console, Serilog.Sinks.File (logging)
  - Swashbuckle.AspNetCore (Swagger/OpenAPI)
- Tests/ApiGateway.Tests.csproj packages:
  - Microsoft.NET.Test.Sdk, xUnit, xunit.runner.visualstudio, coverlet.collector, Microsoft.AspNetCore.Mvc.Testing, Moq
-