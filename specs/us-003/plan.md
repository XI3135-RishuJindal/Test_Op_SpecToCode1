Approach
- Use reflection within the test project to enumerate all controllers (types deriving from ControllerBase with [ApiController]) and extract:
  - Class-level [Route] template (replace [controller] with controller name sans “Controller” and normalize to lowercase).
  - Method-level HttpMethodAttribute(s) and optional method templates combined with the class route.
  - Presence of [Authorize] at class or method level to infer auth requirement.
- Normalize discovered paths to lowercase and leading slash for stable comparisons.
- Assert that no discovered route contains banned segments: payment, payments, billing, checkout, webhook, webhooks, stripe, paypal, braintree, square, adyen.

Architecture decisions
- Add “guardrail” tests that do not require hosting the app or hitting Swagger; these are compile-time assembly scans, lightweight and deterministic.
- Add a complementary “dependency guard” test that reads ApiGateway.csproj and asserts no banned SDKs are referenced.
- Maintain a human-readable route inventory markdown file under openspec/audits to be reviewed with each PR. The inventory will be created from current code and manually updated if routes change. The reflection test output message will help reconcile differences during review.

Implementation details
- Tests/Guards/RouteInventoryTests.cs
  - Discovers and composes full routes and HTTP verbs.
  - Exposes a failure message listing any offending routes and a pretty-printed inventory to assist remediation.
  - Option