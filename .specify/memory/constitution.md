US-002 — CI dependency scanning setup

Quality principles
- Security-by-default: supply-chain risks are first-class; builds fail on unacceptable CVEs (Critical/High) unless explicitly allowed with justification.
- Reproducibility: scanning is deterministic, pinned action versions/SHAs, immutable base images, SBOM artifacts retained.
- Least privilege: CI jobs run with minimal GitHub token permissions; no external secret exfiltration; network egress minimized.
- Transparency and auditability: scan outputs, SBOMs, and policy decisions are stored as build artifacts and linked in PRs.
- Fail-fast: detection of critical findings fails the job early with clear remediations.
- Traceability: each exception to policy (allowlist) includes maintainer, ticket/issue link, expiry/revisit date.

Coding standards and pipeline conventions
- GitHub Actions workflows:
  - Pin actions by commit SHA.
  - Set GITHUB_TOKEN permissions to contents:read and security-events:write only when uploading SARIF; otherwise contents:read.
  - Use concurrency groups to avoid redundant runs on same ref.
  - Cache NuGet to reduce runtime; do not cache scan results.
  - Upload SBOM in SPDX or CycloneDX; prefer SPDX JSON via syft.
  - Artifact retention 7–14 days, non-public.
- Scripts:
  - Place helper scripts under scripts/.
  - Shell scripts are POSIX-compliant, executable, set -euo pipefail, and produce machine- and human-readable outputs.
  - No secrets in logs. Redact sensitive env vars automatically.

Architecture guardrails
- Tools: syft (SBOM), grype (vuln scan) and/or trivy as a fallback. No self-hosted scanners introduced.
- Scope: repository and Docker image derived from Dockerfile; no external registries required.
- Policy: build fails on CVE severity High and Critical unless listed in .github/security/dependency-scan-policy.yml with documented justification. Medium/Low generate warnings.
- Payment SDK detection: proactive search for payment-related dependencies by scanning project files and transitive dependency lists. Findings are reported in job summary; build fails if unauthorized payment SDKs exist (not on allowlist).
- Performance: typical end-to-end scan under 10 minutes on ubuntu-latest.

Non-functional requirements
- Reliability: scanning jobs are idempotent, resilient to tool network hiccups (single retry).
- Maintainability: dependabot keeps github-actions and nuget ecosystems updated; policy file centralizes thresholds/allowlist.
- Observability: step summaries include counts of findings by severity and any payment SDK hits; SARIF uploaded for developer triage.
- Compliance: outputs adequate for audit (SBOM, SARIF, policy, job logs). Exceptions reference a tracking ticket.

Review standards and stakeholder expectations
- AppSec: reviews policy thresholds, allowlist additions, and confirms scanner accuracy on this repo.
- DevOps: validates pipeline stability, runtime, pinned SHAs, and caching effectiveness.
- Service owners: acknowledge payment SDK detections and approve/deny allowlist entries.
- Definition of Done: all acceptance criteria in spec are met; a green run on main; README updated; artifacts present; a sample PR demonstrates failure on seeded vulnerability or test payment pattern; ownership documented.