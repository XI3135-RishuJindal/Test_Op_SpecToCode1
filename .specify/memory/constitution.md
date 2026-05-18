Quality and Security Principles
- Security-first defaults: CI must block merges that introduce known-vulnerable dependencies or unapproved payment SDKs/libraries.
- Supply chain hygiene: prefer official, well-maintained scanners; pin action versions; verify integrity via checksums when practical.
- Least surprise: produce clear, human-readable reports and concise CI summaries with explicit remediation next steps.
- Deterministic and reproducible: scanners run consistently on PRs and default branch; cache where safe to keep times predictable.
- Fail-fast with controlled overrides: a documented allow-list file is the only supported override for payment SDK detection; no blanket ignores in CI configuration.
- Minimize secrets: no third-party SaaS tokens required; rely on GitHub-provided GITHUB_TOKEN and open-source scanners.
- Performance budgets: total dependency scanning should complete in under 6 minutes on a medium GitHub-hosted runner for this repository size. Use conditional steps for frontend scanning only when a package manager manifest exists.
- Evidence and traceability: publish artifacts for all scans (HTML, SARIF, text reports) and retain for at least 7 days.
- Clear ownership: security findings are owned by the repository maintainers; the scanning configuration is code-reviewed like application changes.
- Extensibility: the scanning pipeline should be language-agnostic where practical and ready for future frontend additions.

Coding and Configuration Standards
- GitHub Actions workflows must:
  - be placed under .github/workflows/
  - pin action versions by major/minor tags when possible
  - include concurrency groups to cancel superseded PR runs
  - use bash set -euo pipefail for custom scripts
- Custom scripts live under scripts/ and are executable with Unix LF line endings.
- Policy files live under .security/ and are reviewed whenever detection logic changes.
- Docker builds are not required for dependency scans; container scanning can use filesystem mode to save time unless image scanning is explicitly needed.

Architecture Guardrails
- Tooling:
  - Dependency change awareness: actions/dependency-review-action on pull_request.
  - OSS vulnerability SCA: OWASP Dependency-Check via containerized CLI for .NET/NuGet.
  - Node/NPM audit is conditional on the presence of package.json.
  - Repo-wide FS scanning (Trivy) for additional coverage; high/critical findings fail the job.
  - Custom payment SDK detector enforces organizational policy across multiple ecosystems.
- Gates:
  - Disallow introduction of payment SDKs unless explicitly allow-listed in .security/allowed-payment-sdks.txt.
  - Block merge on high/critical vulnerabilities from SCA steps.
- Reporting:
  - Upload artifacts for each scan; annotate PRs where the action supports it (dependency-review).

Non-Functional Requirements
- CI runtime: < 6 minutes median on ubuntu-latest.
- Maintainability: single policy file for allow-list; simple patterns; minimal duplication.
- Observability: each job prints a short summary and locations of reports.
- Compatibility: works whether or not a frontend currently exists; no changes to application code are required.