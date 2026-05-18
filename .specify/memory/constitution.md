Security and quality constitution for US-005: Ensure no payment secrets in configurations

Principles
- Secrets never in source control: No payment gateway credentials or sensitive tokens are allowed in any committed file or Git history across all environments (Dev, QA, Prod).
- Least privilege and need-to-know: Access tokens and API keys are scoped to environment and service, and stored in a dedicated secret manager managed by DevOps.
- Configuration hygiene: appsettings*.json and launchSettings.json must only contain non-sensitive defaults; secrets are injected at runtime via environment variables or secret manager bindings.
- Fail fast: CI must block merges if any payment secret pattern is detected.
- Auditability: Document the policy and the detection rules; retain scanning reports.
- Redaction-first logging: Logs must never print secret values; structured logging should mask values when keys match sensitive patterns.

Guardrails
- Disallowed in repo: Any of the following identifiers or values (non-exhaustive):
  - Stripe: keys starting with sk_live_, sk_test_, rk_live_, rk_test_, pk_live_, pk_test_
  - PayPal: ClientSecret, Secret, access_token in OAuth context
  - Braintree: MerchantId, PublicKey, PrivateKey, TokenizationKey
  - Adyen: ApiKey, X-API-Key, HMACKey
  - Razorpay: KeyId, KeySecret
  - Square: AccessToken values starting with sq0atp, sq0csp, sq0bsk or Bearer sq0
  - Generic: fields named ApiKey, ClientSecret, Secret, SigningSecret, WebhookSecret when paired with a known payment vendor name
- Allowed in repo: Non-sensitive identifiers (e.g., Issuer/Audience), feature flags, mock keys explicitly marked as fake and validated by tests, and documented placeholders (e.g., "set-with-env-var").
- Required storage: Secrets must reside in a secrets manager (GitHub Actions Secrets, Azure Key Vault, AWS Secrets Manager, or similar). Environment variables are acceptable when provisioned securely by the platform.

Non-functional requirements
- CI scanning must complete within 2 minutes per push and PR.
- Zero false negatives on the curated set of payment patterns; false positives may be suppressed via reviewed allowlist entries committed to rules file with justification.
- The default developer experience must remain functional without embedding real secrets.

Review standards and stakeholder expectations
- Security approves the detection rules and policy document.
- DevOps owns CI integration and secret manager wiring for each environment.
- Product Owner signs off that the story scope excludes payment feature behavior changes; this is compliance and hygiene only.
- Code review requires: presence of CI secret-scanning workflow, repository-level rules file, unit test validating configuration files are free of payment secrets, and documentation in /docs/security.

Change management
- Any change to the allowlist or patterns requires security review and PR approval by CODEOWNERS for security.
- Historical scan must be executed once, results archived, and remediation issues created for any findings (none expected here).