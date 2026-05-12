Architecture and approach
- No runtime changes. Introduce a test-only guardrail to assert the absence of payment-related UI/route indicators.
- Implement two tests:
  1) Reflection-based scan of ASP.NET Core controllers and their routes/HTTP attributes to ensure no forbidden tokens are present in names or templates.
  2) Repository source scan to ensure no forbidden tokens in source/content files that could represent UI artifacts or documentation leaks.

Key decisions
- Prefer tests over analyzers for speed of adoption and low maintenance.
- Avoid overly-generic tokens to reduce false positives; do not include “pay” alone to avoid hits like “payload”.
- Keep Swagger enabled; only ensure no payment-related routes exist.

Forbidden tokens (case-insensitive)
- payment, payments, payout, billing, invoice, invoices, checkout, creditcard, debitcard, cardnumber, cvv, stripe, paypal, applepay, googlepay, wallet

Test design
1) Controller/route reflection test
- Load ApiGateway assembly.
- Find all types assignable to ControllerBase.
- For each controller:
  - Build a set of candidate strings: type.Name, [Route] template(s), [HttpGet/Post/Put/Delete/...](template) values, method names.
  - Assert none contain forbidden tokens (case-insensitive substring match).
- Fails with details listing offending type/method and token.

2) Source/content file scan test
- Starting from AppContext.BaseDirectory, ascend directories until locating ApiGateway.csproj to find repository root.
- Enumerate files with extensions: .cs, .cshtml, .html, .js, .ts, .css, .md.
- For each file, read text (with UTF-8) and scan for forbidden tokens.
- Ignore:
  - This specification directory (.specify and specs) to avoid self-references.
  - bin/ and obj/ directories.
- Fails with list of offending files and tokens.

API contracts
- No changes. Existing endpoints (Auth, Health, Test) remain unchanged.

Data model
- No changes.

Integration points
- None added. Tests are self-contained.

Risks and mitigations
- Risk: False positives in documentation or specs.
  - Mitigation: Exclude specs/.specify from the content scan.
- Risk: Path discovery in CI differs.
  - Mitigation: Root discovery ascends multiple levels to locate ApiGateway.csproj reliably.
- Risk: Future introduction of payment endpoints bypass guardrail.
  - Mitigation: Tests run in CI and will fail PRs.

Performance and reliability
- Tests are fast (string/IO scans) and deterministic.
- No external dependencies.

Rollout
- Single PR: add tests + docs.
- CI will start enforcing immediately after merge.

Sign-off
- PO confirms absence of payment UI discoverability for ApiGateway after PR merges and CI passes.