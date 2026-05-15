Quality principles
- Security-first CI: All pull requests and pushes must run automated dependency scanning. The pipeline must fail fast for high-risk findings (payment SDKs/libraries) unless an explicit, audited override is set.
- Explicit allow/deny: Introduce a curated denylist of payment-related SDKs/libraries across ecosystems. Add a controlled override mechanism (PR label allow-payment-sdks) for exceptional cases with auditability.
- Deterministic scans: Use repeatable CLI commands (dotnet list package) and a repository-pinned denylist file to ensure consistent results across runners and time.
- Observability: Publish human-friendly summaries and store machine-readable artifacts for traceability.
- Minimal friction: Scans run in parallel with build/test and complete within 3 minutes on typical hardware.
- Extensibility: The scanning workflow supports additional ecosystems (e.g., Node.js) when corresponding manifests appear (package.json, yarn.lock, pnpm-lock.yaml).

Coding standards
- Workflows: Use GitHub Actions YAML, lowercase job and step ids, and explicit versions of actions.
- Scripts: Implement scanning logic in PowerShell Core (pwsh) for cross-platform compatibility. Prefer pure CLI and standard JSON parsing (ConvertFrom-Json).
- Config files: Keep patterns/denylist in repo under .github/dependency-rules to allow code review and governance.
- Logging: Emit concise findings to console and $GITHUB_STEP_SUMMARY; avoid secrets or sensitive values in logs.

Architecture guardrails
- No network access to third-party services during scanning beyond package restore from official registries.
- No dynamic code execution introduced by scanning scripts.
- The denylist is applied to both direct and transitive dependencies. Transitive matches are treated as blocking unless overridden.
- Overrides are explicit: A PR label allow-payment-sdks or a temporary allowlist entry stored in-repo (with reviewer approval) is required to pass.

Non-functional requirements
- Performance: End-to-end dependency scanning must complete in under 180 seconds for this repo on ubuntu-latest.
- Reliability: Pipeline must not be flaky; any nonzero exit in scanning script must fail the job.
- Usability: On failure, developers must see the offending package id, version, path/manifests, and suggested remediation.
- Compliance: All findings and overrides are persisted as workflow artifacts; denylist changes require code review (PR).

Outcomes enforced by this constitution
- Any introduction of payment-related SDKs/libraries in .NET (NuGet) or, when present, frontend (npm/yarn/pnpm) will break the build unless explicitly allowed.
- Weekly scheduled scans detect drift or new transitive inclusions even without code changes.