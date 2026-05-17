WHAT
Implement automated dependency and container image scanning in CI for repository XI3135-RishuJindal/Test_Op_SpecToCode1. The workflow must:
- Generate a software bill of materials (SBOM) for the .NET solution and Docker image.
- Scan direct and transitive dependencies for known CVEs; fail on High/Critical severities per policy.
- Detect presence of payment-related SDKs/libraries (e.g., Stripe, PayPal, Braintree, Razorpay, Square, Adyen, Worldpay, Klarna, etc.). If detected and not allowlisted, fail the job; otherwise warn and summarize.
- Upload findings in SARIF and artifact formats; post a concise summary in the job output.
- Keep dependencies current via Dependabot for nuget and github-actions ecosystems.

WHY
- Reduce supply-chain risk and provide auditable evidence of dependency health (SBOM, SARIF).
- Ensure early awareness of payment-related libraries that may impose compliance implications (PCI DSS) even if unused at runtime.
- Automate feedback on PRs so vulnerabilities and prohibited packages are blocked before merge.

User story
As a DevOps/Security engineer, I want dependency scanning in CI so that PRs are blocked if they introduce vulnerable or non-approved payment SDKs, and the team gains visibility through artifacts and automated summaries.

Acceptance criteria
1) GitHub Actions workflow
- A workflow .github/workflows/dependency-scanning.yml triggers on:
  - pull_request to main
  - push on main
  - manual dispatch
- Jobs:
  a) sbom-and-deps-scan
     - Runs on ubuntu-latest
     - Sets permissions: contents: read; security-events: write (only for SARIF upload)
     - Restores NuGet, runs syft to generate SPDX JSON SBOM for the repo, uploads as artifact
     - Runs grype scan on the SBOM; build fails on High/Critical unless allowlisted
     - Uploads SARIF to GitHub code scanning and attaches a human-readable summary to the job
     - Runs scripts/detect-payment-sdks.sh; fails if any non-allowlisted payment SDK is found; prints allowlist and findings
  b) docker-image-scan
     - Builds the Docker image from Dockerfile with local tag
     - Generates SBOM for the image and scans it with grype or trivy
     - Fails on High/Critical; uploads artifacts and optional SARIF
     - If Docker build fails, gracefully falls back to filesystem scan so CI still produces results
- Concurrency: cancel in-progress on new push to same ref.

2) Policy/allowlist
- .github/security/dependency-scan-policy.yml committed with:
  - severity_threshold: high
  - allowlist: list of CVE IDs and package coordinates with justification and expiry date
  - payment_sdk_allowlist: list of approved payment packages (empty by default)

3) Payment SDK detection
- The detection step scans:
  - *.csproj, packages.lock.json (if present), output of dotnet list <proj> package --include-transitive
  - Any package or file path containing case-insensitive patterns: stripe, paypal, braintree, razorpay, square, adyen, checkout, payu, worldpay, klarna, afterpay, sezzle, applepay, googlepay
- The step writes a table of matches to the job summary and exits non-zero if any unapproved hit exists.

4) Dependabot
- .github/dependabot.yml configured for:
  - package-ecosystem: nuget in root directory, schedule weekly
  - package-ecosystem: github-actions in root directory, schedule weekly
- Dependabot PRs are labeled security and dependency with auto-assign to CODEOWNERS if present.

5) Developer documentation
- README updated with:
  - brief overview of scanning, run conditions, policy, and how