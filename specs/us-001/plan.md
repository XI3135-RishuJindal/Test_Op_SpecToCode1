Approach
- Since no payment UI exists in this repository, we will establish a permanent guard. Add a policy test in the ApiGateway.Tests project that scans Controllers/ for disallowed payment-related keywords in file names, class names, and route attributes. Update README.md to state that the MVP excludes payment UI.
- No API contract, data model, or runtime behavior changes are required. We will not disable Swagger (it is not payment-specific).
- Provide process documentation (this spec) and a clear PR checklist to ensure future changes keep the zero-payment-UI guarantee.

Architecture Decisions
- ADR: Introduce “negative policy tests” to enforce absence of payment UI at compile/test time, rather than feature flags or runtime switches.
- Test scope: Only scan Controllers/ to avoid blocking technical documentation that uses the word “payment” (e.g., this spec).
- Keep Swagger enabled in Development; it must display no payment-related endpoints by virtue of AC1.

Implementation Details
- Add Tests/Policies/NoPaymentUiElementsTests.cs:
  - Enumerate files under Controllers/.
  - Assert that file names and contents do not match case-insensitive keywords: payment, payments, billing, checkout, pay.
  - Additionally, parse [Route] and [Http*] attribute lines to detect keyword leaks in routes.
- Update README.md:
  - Add a short statement under Overview indicating MVP has no payment UI and the repository enforces this via automated tests.
- Documentation:
  - Commit this spec, plan, tasks, and constitution files to the repo.

Testing and Rollout
- Run dotnet test locally to confirm the new guard test passes.
- Submit a PR; reviewers validate ACs and policy test behavior.
- No migration or downtime; change is additive and test-only.

Backout Plan
- If the policy test causes unexpected failures, temporarily limit the keyword set or further scope scanning to attributes only. No runtime rollback is necessary.