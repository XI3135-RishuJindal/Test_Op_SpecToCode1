Delivery plan and architecture/process decisions

Approach
- Prevent: Add a GitHub Actions workflow to run a curated secrets scan on push and PR. Provide a repository-local rules file (.gitleaks.toml) focused on payment vendors (Stripe, PayPal, Braintree, Adyen, Razorpay, Square) including key names and token prefix signatures.
- Detect in tests: Add a lightweight xUnit test (Tests/Config/SensitiveConfigTests.cs) that loads appsettings.json, appsettings.Development.json, and Properties/launchSettings.json if present, then asserts no disallowed keys or values exist.
- Document: Add docs/security/payment-secrets-policy.md explaining prohibited fields, sample environment variable usage, and how CI enforces the rule. Record the initial scan report under docs/reports/.

Decisions
- Use gitleaks as the primary scanner due to speed, ecosystem support, and simple TOML rule customization. Rules will cover both high-entropy tokens and explicit vendor patterns.
- Keep runtime code unchanged (no startup blockers) to avoid impacting developer experience; the guards are in CI and tests.
- Treat payment secrets as P0 severity; CI job will fail builds on any finding with zero tolerance.

Process steps
1) Create .gitleaks.toml with payment patterns, include allowlist stubs with comments requiring security approval.
2) Add .github/workflows/secret-scan.yml to run gitleaks on PRs and pushes to main. Upload a SARIF artifact and fail the job on findings.
3) Implement Tests/Config/SensitiveConfigTests.cs to scan configuration JSONs for blacklisted keys/prefixes and fail if any are present.
4) Author docs/security/payment-secrets-policy.md covering storage guidelines (GitHub Secrets/Azure Key Vault), how to pass secrets as environment variables, and prohibited keys.
5) Run a one-time full-repo history scan locally or via Actions and commit the results to docs/reports/gitleaks-initial-scan.md (no secrets expected).
6) Update README.md with a short section linking to the policy and indicating that CI will block merges on secret findings.
7) Coordinate with Security and DevOps for policy review and branch protection rule updates requiring the Secret Scan workflow to pass.

Stakeholders and tools
- Security: approves rules and allowlist, reviews initial scan report.
- DevOps: configures branch protections, oversees GitHub Secrets.
- API team: implements tests and documentation.
- Tools: gitleaks, GitHub Actions, xUnit.

Risk and mitigation
- False positives: mitigate via allowlist with justification comments reviewed by Security.
- Developer friction: tests are fast; no runtime impact. Documentation provides clear guidance.
- Future files: CI and rules file cover any new appsettings.* automatically.