Workstream: Repository XI3135-RishuJindal/Test_Op_SpecToCode1

CI and scanning
- [ ] add .gitleaks.toml: define payment-specific rules (Stripe sk_live_, PayPal ClientSecret, Braintree PrivateKey, Adyen ApiKey/HMACKey, Razorpay KeySecret, Square AccessToken prefixes sq0atp/sq0csp/sq0bsk) and minimal allowlist with comments
- [ ] add .github/workflows/secret-scan.yml: GitHub Actions workflow running gitleaks on push and pull_request, uploading SARIF/HTML report artifacts, failing on findings
- [ ] update README.md: add “Secrets policy and CI” section linking to docs/security/payment-secrets-policy.md and describing the secret-scan workflow status check

Unit tests (prevent regressions)
- [ ] add Tests/Config/SensitiveConfigTests.cs: scan appsettings.json, appsettings.Development.json, and Properties/launchSettings.json for disallowed keys/prefixes; assert none found
- [ ] run dotnet test locally and in CI to ensure the new test passes

Documentation and evidence
- [ ] add docs/security/payment-secrets-policy.md: policy, prohibited keys/prefixes, how to inject secrets via environment variables or secret manager, remediation steps
- [ ] add docs/reports/gitleaks-initial-scan.md: capture one-time historical scan summary (tool version, command, timestamp, result = no findings)
- [ ] create CODEOWNERS or update existing to require Security and DevOps approval for changes to .gitleaks.toml and .github/workflows/secret-scan.yml (if repository uses CODEOWNERS)

Manual review checklist
- [ ] verify appsettings.json contains no payment secrets or vendor configs (OK)
- [ ] verify appsettings.Development.json contains no payment secrets or vendor configs (OK)
- [ ] verify Properties/launchSettings.json contains no payment secrets (OK)
- [ ] verify Dockerfile contains no embedded secrets or ARG default values containing sensitive tokens (OK)
- [ ] verify Program.cs and Controllers contain no payment-related hard-coded credentials (OK)

Governance and rollout
- [ ] enable branch protection to require secret-scan workflow to pass before merge to main
- [ ] review acceptance criteria with Product