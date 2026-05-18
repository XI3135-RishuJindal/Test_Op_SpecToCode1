# Payment Secrets Policy

## Overview
This document outlines the policy for managing payment-related secrets and API keys within the repository to ensure compliance with security best practices and reduce the risk of accidental exposure.

## Prohibited Patterns
The following patterns and key prefixes for payment processors must never be included in any committed or versioned code or configuration files:

- **Stripe:** Keys starting with `sk_live_`, `pk_live_`
- **PayPal:** `ClientSecret`, `access_token`
- **Braintree:** `MerchantId`, `PublicKey`, `PrivateKey`, `TokenizationKey`
- **Adyen:** `ApiKey`, `X-API-Key`, `HMACKey`
- **Razorpay:** `KeyId`, `KeySecret`
- **Square:** Access tokens starting with `sq0atp`, `sq0csp`, `sq0bsk` or `Bearer sq0`

## Secrets Management
- **Environment Variables:** Use environment variables for secret values in local development and production.
- **Secret Manager:** For production, secrets should be managed through secure secret storage solutions like GitHub Cloud Secrets, Azure Key Vault, or AWS Secrets Manager.

## CI/CD Enforcement
- The CI/CD pipeline includes secret-scanning as a mandatory step that blocks merges if any prohibited patterns are detected.
- All tests on configuration files are automated to fail build if secrets are committed accidently.

## Developer Instructions
- Do not hardcode secrets directly into source code.
- Use provided configuration templates and inject secret values via environment variables or configuration providers at runtime.

## Compliance
- Any detection or mitigation reports, including the initial repository scan report, must be logged and reviewed by security personnel.

## Contact
For further assistance regarding secret management, please contact the security and DevOps teams.
