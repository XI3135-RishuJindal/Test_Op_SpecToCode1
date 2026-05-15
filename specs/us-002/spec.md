WHAT
- Implement CI dependency scanning that automatically detects payment-related SDKs/libraries in this repository.
- Scope prioritizes backend (.NET 8, NuGet) and is extensible to frontend (npm/yarn/pnpm) when a package.json is present.
- On detection of denylisted packages (direct or transitive), the CI job fails and surfaces a clear report.
- Provide an auditable override via PR label allow-payment-sdks to temporarily unblock while maintaining visibility.

User story narrative
- As a security/compliance owner, I need automated detection of payment SDKs/libraries so that payment processing logic cannot be introduced without review and approval.
- As a developer, I want fast feedback on PRs and clear instructions on how to remediate or request an approved exception.

WHY
- Prevent unapproved payment integrations, reduce compliance risk, and ensure architectural boundaries (payments handled only in designated services).
- Early detection minimizes rework and audit exposure.

Acceptance criteria
1) Triggering
- Runs on pull_request (all branches), push to main, and a weekly schedule (cron).
- Skips failure when the PR has label allow-payment-sdks, but still produces a report.

2) Detection (backend)
- Restore dependencies and enumerate both direct and transitive NuGet packages from ApiGateway.csproj using dotnet list package with JSON output.
- Match package ids against a denylist (case-insensitive, regex-supported) including: stripe, paypal, braintree, adyen, razorpay, square, authorize(.?net)?, cybersource, checkout(.?com)?, mollie, worldpay, bluesnap, klarna, afterpay, affirm, amazonpay, payu.
- If any match is found, job fails with exit code 1 and summarizes the list of matches in $GITHUB_STEP_SUMMARY.

3) Detection (frontend; future-proof)
- If a package.json is present at repo root or subfolders, parse dependencies and devDependencies and match against the same denylist.
- Absence of a frontend manifest does not fail or warn.

4) Reporting
- Produce a concise console output and append a markdown summary (found packages, versions, manifest path, direct vs transitive).
- Upload machine-readable artifacts (packages.json from dotnet list; scan-results.json) for audit.

5) Override and governance
- Presence of the PR label allow-payment-sdks causes the job to report findings but not fail.
- Denylist patterns are stored in .github/dependency-rules/payment-denylist.txt and changes require PR review.

6) Developer experience
- README updated with “Dependency scanning” section explaining behavior, override, and how to run locally.

Out-of-scope
- Vulnerability/License scanning (separate pipelines).
- Secret scanning (covered by platform).
- Auto-remediation PRs.
- CodeQL or SAST configuration changes.

Cross-service dependencies
- None at runtime. Build-time only:
  - GitHub Actions runners (ubuntu-latest).
  - actions/setup-dotnet to install .NET 8 SDK.
  - PowerShell Core (pwsh) shell available on ubuntu-latest.