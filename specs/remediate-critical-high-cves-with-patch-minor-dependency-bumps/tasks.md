## Prerequisites
N/A — not applicable to this task

## Phase 1 — Preparation
- [ ] [S] Generate a current dependency and vulnerability report for the repository using the existing build tool and capture results in SECURITY/vuln-baseline.md
- [ ] [XS] Create a remediation branch remediations/cve-patch-bumps from the default branch in git
- [ ] [S] Identify all currently critical/high CVEs from existing security tooling output and list affected direct dependencies in SECURITY/cve-remediation-plan.md with target patched/minor versions
- [ ] [S] Record a pre-change test baseline by running the existing test command(s) and saving the summary output in SECURITY/test-baseline.txt

## Phase 2 — Core Upgrade
- [ ] [M] Bump patched/minor versions for direct dependencies that map to critical/high CVEs in the repository’s primary dependency manifest file(s) (e.g., package.json / pom.xml / build.gradle / requirements.txt) without introducing major-version upgrades
- [ ] [M] Bump patched/minor versions for indirect/transitive dependencies using the build tool’s supported mechanism (lockfile update / dependencyManagement / resolution strategy) in the repository’s lockfile or build config files
- [ ] [S] Update any security-related version pins/overrides to the remediated versions in the repository’s dependency override configuration (if present) to ensure patched versions are selected consistently

## Phase 3 — Testing & Validation
- [ ] [S] Re-run the full test suite using the existing test command(s) and store the summary output in SECURITY/test-postremediation.txt
- [ ] [S] Re-run vulnerability scanning and verify critical/high findings are remediated, saving the post-change report in SECURITY/vuln-postremediation.md
- [ ] [XS] Compare pre/post reports and document remaining accepted risk or blocked upgrades (if any) in SECURITY/cve-remediation-plan.md

## Phase 4 — CI/CD & Infrastructure
N/A — not applicable to this task

## Phase 5 — Documentation & Rollout
- [ ] [XS] Add an entry describing the dependency patch/minor bumps for CVE remediation in CHANGELOG.md
- [ ] [S] Document verification steps (tests run + vuln scan evidence) for this remediation in SECURITY/cve-remediation-plan.md