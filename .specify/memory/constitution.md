Quality principles
- Security by default: deny inclusion of prohibited SDKs/libraries (payment providers) and fail CI on detection.
- Supply-chain hygiene: continuously scan dependencies for known vulnerabilities and keep them updated.
- Reproducibility: deterministic builds, pinned action versions, and version-controlled scan policies.
- Fail fast with clear diagnostics: CI should provide actionable summaries and logs.
- Minimal privileges: CI secrets and permissions restricted to read-only where possible.
- Observability of the SDLC: scans run on PRs, main, and on a schedule; results are visible in PR checks and documentation.

Technology guardrails
- CI platform: GitHub Actions only; use official actions pinned by major version or commit SHA where possible.
- Scanners: .NET built-in dependency vulnerability reporting (dotnet list package) plus a custom prohibited-dependency detector.
- Policy-as-code: central JSON policy file for banned packages/patterns committed in repo.
- No external paid scanners or services; Dependabot is enabled for nuget and docker ecosystems.
- No calls to untrusted third-party endpoints from CI steps.
- Jobs must be cross-platform capable; scripts use PowerShell Core for portability on GitHub-hosted runners.

Coding standards for CI scripts
- PowerShell Core, strict mode, exit non-zero on policy violations.
- Clear console output and GitHub step summary for developer feedback.
- Input validation and defensive parsing of tool output.
- Keep business policy (banned list) outside the script in a JSON file.
- Avoid duplicating logic; shared logic in scripts/ci.

Non-functional requirements
- Performance: dependency scanning job completes within 5 minutes on standard runners for this repo size.
- Reliability: scans run on every PR and on a weekly schedule; deterministic outcomes on identical inputs.
- Maintainability: policy can be extended without code changes; script has comments and help.
- Compliance: keep artifacts minimal; do not print secrets; do not upload source externally.
- Documentation: developer-facing docs describing how