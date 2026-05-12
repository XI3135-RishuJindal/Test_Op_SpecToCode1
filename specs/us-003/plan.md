Architecture and approach
- Strategy: Create an automated guardrail in the test project to:
  1) Reflect over controllers/actions to enumerate effective route templates and assert no prohibited keywords are present.
  2) Inspect ApiGateway.csproj package references to assert no payment/webhook SDKs are present.
- Documentation: Add a ROUTE_INVENTORY.md capturing current routes and explicit confirmation that no payment endpoints or webhooks exist.
- CI: Tests run as part of existing test suite; no pipeline modification required.

Component design
- Route inventory scanner (test-only):
  - Discover controllers: Types assignable to ControllerBase with [ApiController].
  - Determine base route: Read [Route] attributes; resolve token [controller] to controller name minus "Controller", lowercased.
  - Determine action routes: Check for Http{Verb}Attribute(s) and optional templates (e.g., "token"). If none, use controller base route.
  - Compose effective route: join base route and action route; normalize to "/api/...".
  - Collect (method, path) pairs for assertions and for human-readable logging on failure.

- Package reference scanner (test-only):
  - Load ApiGateway.csproj as XML.
  - Iterate <PackageReference Include="..."> items.
  - Assert none contain known provider/payment keywords (case-insensitive).

API contracts
- No new or changed API endpoints. This is an audit/verification-only change.

Data model
- No changes.

Integration points
- None added.

Test cases
- RouteInventory_HasNoPaymentOrWebhookEndpoints
  - Arrange: load assembly ApiGateway.
  - Act: enumerate routes.
  - Assert: no route path, controller name, or action name contains any prohibited keyword.

- PackageReferences_DoNotContainPaymentProviders
  - Arrange: open ApiGateway.csproj.
  - Assert: no package name includes prohibited provider/payment tokens.

Operationalization
- Document the route inventory in docs/ROUTE_INVENTORY.md with timestamp and commit hash placeholder to update on change.
- Link the document from README.md for quick discovery.

Risk and mitigations
- False negatives due to unconventional routing: Mitigate by scanning both controller-level and method-level attributes, and checking names as a fallback.
- Future regressions: Guardrail tests ensure CI fail-fast on prohibited additions.