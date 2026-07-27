## Prerequisites
- [ ] [XS] Confirm CI provider and repository workflow location in `.github/workflows/` (or equivalent CI config directory)  
- [ ] [XS] Verify repository permissions to add workflow files and upload build artifacts in GitHub Actions settings (Actions → General → Workflow permissions)  

## Phase 1 — Preparation
- [ ] [S] Identify existing build workflow entrypoint and artifact outputs in `.github/workflows/*.yml`  
- [ ] [XS] Capture current baseline CI run status (successful build + existing artifacts) in `.github/workflows/*.yml` by re-running latest pipeline  

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
- [ ] [S] Validate SBOM generation job runs on pull_request and main branch pushes in `.github/workflows/*.yml`  
- [ ] [S] Validate SBOM is generated for the produced build artifacts and uploaded as a workflow artifact in `.github/workflows/*.yml`  

## Phase 4 — CI/CD & Infrastructure
- [ ] [M] Add SBOM generation job using CycloneDX (or equivalent) and upload SBOM as artifact in `.github/workflows/*.yml`  
- [ ] [S] Configure job dependencies so SBOM runs after build artifacts are produced (use `needs:`) in `.github/workflows/*.yml`  
- [ ] [S] Add caching (if applicable) to keep SBOM job runtime acceptable in `.github/workflows/*.yml`  
- [ ] [XS] Restrict workflow permissions to least privilege required for artifact upload in `.github/workflows/*.yml` (`permissions:` block)  

## Phase 5 — Documentation & Rollout
- [ ] [XS] Document SBOM job purpose, outputs, and where to download artifacts in `README.md` (or existing CI documentation file)  
- [ ] [S] Add changelog entry for new SBOM CI artifact in `CHANGELOG.md` (if present)  
- [ ] [S] Roll out by enabling workflow on default branch and monitoring first 3 successful runs for artifact availability in `.github/workflows/*.yml`