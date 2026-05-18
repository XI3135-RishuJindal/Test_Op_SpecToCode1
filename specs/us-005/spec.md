US-005: Ensure no payment secrets in configurations

What
- Review and enforce that no payment gateway secrets or configurations containing sensitive credentials exist in environment configuration for Dev, QA, and Production within the repository XI3135-RishuJindal/Test_Op_SpecToCode1.
- Introduce automated and manual controls to prevent future regressions:
  - CI secret scanning for payment-specific patterns.
  - Unit test that asserts appsettings*.json and launchSettings.json do not include disallowed keys or recognizable token prefixes.
  - Documentation of the policy and the accepted mechanism for providing secrets at runtime (environment variables or secret manager).
- Execute a one-time historical scan and archive the report.

Why
- Payment providers strictly prohibit storing live/test secrets in source control. Leaks create high-risk exposure, PCI-DSS issues, and potential financial loss.
- Proactive CI and unit test gates reduce operational risk and support audit readiness.

In-scope
- Files to inspect and gate in this repository:
  - appsettings.json
  - appsettings.Development.json
  - Properties/launchSettings.json
  - Dockerfile (for embedded secrets or ARG defaults)
  - Program.cs and Controllers for hard-coded payment credentials (none expected; confirm)
  - Any future appsettings.*.json files
- CI workflow under .github/workflows with policy rules in .gitleaks.toml (or equivalent) tailored to payment vendors.
- Repository documentation under docs/security.

Out-of-scope
- Refactoring authentication/JWT configuration or removing non-payment development keys. Note: JWT keys shown are not payment-related; they may be addressed in a separate hardening story.
- Adding or changing actual payment gateway integrations.
- Rotating secrets in external systems.

Acceptance criteria
- No payment secrets are present in appsettings*.json, launchSettings.json, Dockerfile, or code files. Manual review checklist completed and attached to PR.
- CI includes a secret-scanning job that blocks merges on findings and includes custom payment-signature patterns.
- Unit test in Tests/ validates disallowed payment keys/prefixes are absent in config JSON files; test passes in CI.
- A policy document exists at docs/security/payment-secrets-policy.md describing how to supply secrets at runtime and listing prohibited patterns/keys.
- One-time historical scan report is added under docs/reports/gitleaks-initial-scan.md with date, tool version, and results summary.
- Branch protection updated to require the secret-scanning job to pass on PRs to main.
- Security and DevOps sign-off recorded in the PR.

Dependencies and interfaces
- CI platform: GitHub Actions for running secret scanning workflow.
- Secret storage reference: GitHub Actions Secrets or organization-level secret manager (documentation link and ownership noted).
- Stakeholders: Security (policy/patterns), DevOps (CI + secret storage), API team (code/tests), Product Owner (scope sign-off).

Operational considerations
- False positives are suppressed via allowlist entries in .gitleaks.toml with comments and reviewer approval.
- The unit test must be deterministic and fast (<1s), scanning only the small set of configuration files.
- Logs must not include any values of keys matching sensitive patterns.