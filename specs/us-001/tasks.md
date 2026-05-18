## Tasks (auto-derived from plan — review and refine)

- [ ] No code removal is currently needed because the repo contains no payment UI or routes; instead, we add automated guards to prevent regressions.
- [ ] We enforce two layers of protection:
- [ ] Documentation is updated to declare payments are explicitly out of scope for MVP.
- [ ] Create Tests/Guards/NoPaymentEndpointsTests.cs to:
- [ ] Load the ApiGateway assembly, enumerate [ApiController] classes, inspect RouteAttribute and HttpMethodAttributes.
- [ ] Aggregate route templates, controller/action names, and assert none contain forbidden terms.
- [ ] Create Tests/Guards/NoPaymentUiAssetsTests.cs to:
- [ ] Resolve repository root relative to the test assembly directory.
- [ ] Assert that Views, Pages, wwwroot do not exist, and scan for any .cshtml/.razor/.html files; verify none contain payment-related terms.
- [ ] Keep tests fast, deterministic, and OS-agnostic.
- [ ] Update README.md with a short “Non-payment MVP” section clar