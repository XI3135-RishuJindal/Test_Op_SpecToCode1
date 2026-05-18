Implementation approach

Architecture decisions
- No code removal is currently needed because the repo contains no payment UI or routes; instead, we add automated guards to prevent regressions.
- We enforce two layers of protection:
  1) Reflection-based test scanning all controller types and route attributes for payment-related terms.
  2) Filesystem-based test verifying that no UI folders/files (Views, Pages, wwwroot, *.cshtml, *.razor, *.html) exist with payment-related content.
- Documentation is updated to declare payments are explicitly out of scope for MVP.

Testing strategy
- Create Tests/Guards/NoPaymentEndpointsTests.cs to:
  - Load the ApiGateway assembly, enumerate [ApiController] classes, inspect RouteAttribute and HttpMethodAttributes.
  - Aggregate route templates, controller/action names, and assert none contain forbidden terms.
- Create Tests/Guards/NoPaymentUiAssetsTests.cs to:
  - Resolve repository root relative to the test assembly directory.
  - Assert that Views, Pages, wwwroot do not exist, and scan for any .cshtml/.razor/.html files; verify none contain payment-related terms.
- Keep tests fast, deterministic, and OS-agnostic.

Documentation updates
- Update README.md with a short “Non-payment MVP” section clar