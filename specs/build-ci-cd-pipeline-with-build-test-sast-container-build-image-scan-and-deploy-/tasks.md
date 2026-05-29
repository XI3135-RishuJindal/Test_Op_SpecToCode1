# TASKS — Build CI/CD Pipeline with Build, Test, SAST, Container Build, Image Scan, and Deploy Stages

> **Scope:** Greenfield CI/CD pipeline construction covering the six required stages: build, test, SAST, container build, image scan, and deploy.
> **Note:** Language, runtime, and build tool are unspecified in the tech analysis. Tasks below are written to be platform-agnostic where forced, and flag decision points that must be resolved before execution begins.

---

## Prerequisites

- [ ] [XS] Confirm and document the target CI/CD platform (GitHub Actions, GitLab CI, Jenkins, etc.) in a `docs/cicd-decisions.md` decision log
- [ ] [XS] Confirm and document the container registry (ECR, GCR, Docker Hub, GHCR, etc.) and record the registry URL and auth method in `docs/cicd-decisions.md`
- [ ] [XS] Confirm and document the deployment target (Kubernetes, ECS, VM, serverless, etc.) and record in `docs/cicd-decisions.md`
- [ ] [XS] Verify that repository secrets/environment variables for registry credentials, SAST tokens, and deploy credentials are provisioned in the CI platform's secret store
- [ ] [XS] Confirm a `Dockerfile` (or equivalent container build file) exists at the repository root, or identify the path to be used in pipeline config
- [ ] [XS] Confirm the SAST tool selection (e.g., Semgrep, Snyk, Trivy for code, Bandit, CodeQL) and record license/token requirements in `docs/cicd-decisions.md`
- [ ] [XS] Confirm the image scanning tool (e.g., Trivy, Grype, Snyk Container, Anchore) and record in `docs/cicd-decisions.md`

---

## Phase 1 — Preparation

- [ ] [S] Create the base pipeline configuration file skeleton (e.g., `.github/workflows/ci-cd.yml`, `.gitlab-ci.yml`, or `Jenkinsfile`) with named, empty stage stubs: `build`, `test`, `sast`, `container-build`, `image-scan`, `deploy`
- [ ] [S] Define pipeline trigger rules in the pipeline config file — specify branch filters (e.g., `main`, `develop`), PR/MR triggers, and tag-based deploy triggers
- [ ] [S] Configure pipeline-level environment variables and secret references (registry URL, image name, deploy environment) in the pipeline config file, referencing the CI platform's secret store — no plaintext secrets
- [ ] [XS] Create a `.dockerignore` file at the repository root to exclude build artifacts, test output, and secrets from the container build context
- [ ] [XS] Add a `docs/cicd-decisions.md` file to the repository capturing all decisions from Prerequisites for team reference

---

## Phase 2 — Core Upgrade

> **Note:** "Core upgrade" in this context means building each pipeline stage. Tasks are ordered by the pipeline's dependency chain.

### Stage 1 — Build

- [ ] [M] Implement the `build` stage in the pipeline config file: define the correct runtime/build-tool container image, install dependencies, compile or assemble the application, and cache dependency directories to speed subsequent runs
- [ ] [S] Configure build artifact upload in the `build` stage so downstream stages (test, SAST) can consume compiled output without re-running the build step

### Stage 2 — Test

- [ ] [M] Implement the `test` stage in the pipeline config file: restore cached dependencies and build artifacts, execute the full test suite, and configure the stage to fail the pipeline on any test failure
- [ ] [S] Configure test result and code-coverage report export (JUnit XML or equivalent) as pipeline artifacts in the `test` stage for later review and baseline comparison

### Stage 3 — SAST

- [ ] [M] Implement the `sast` stage in the pipeline config file: install the chosen SAST tool, run a full source-code scan against the repository, output results in SARIF or tool-native format, and upload the report as a pipeline artifact
- [ ] [S] Configure SAST severity thresholds in the `sast` stage — define which severity levels (e.g., HIGH, CRITICAL) cause a pipeline failure vs. produce a warning, and document the threshold values in `docs/cicd-decisions.md`
- [ ] [XS] Add SAST tool configuration file (e.g., `.semgrep.yml`, `snyk.config.json`, or `.bandit`) to the repository root with project-appropriate rule sets

### Stage 4 — Container Build

- [ ] [M] Implement the `container-build` stage in the pipeline config file: build the Docker image using the repository `Dockerfile`, tag the image with both the commit SHA and a `latest`-equivalent tag, and ensure the stage only runs after `build` and `test` pass
- [ ] [S] Configure container registry authentication and image push in the `container-build` stage using credentials from the CI secret store — push the tagged image to the confirmed registry

### Stage 5 — Image Scan

- [ ] [M] Implement the `image-scan` stage in the pipeline config file: pull the just-pushed image from the registry, run the chosen image scanning tool (e.g., `trivy image`, `grype`), output results in a structured format, and upload the scan report as a pipeline artifact
- [ ] [S] Configure image scan severity thresholds in the `image-scan` stage — define which CVE severity levels (e.g., CRITICAL) fail the pipeline, and document threshold values in `docs/cicd-decisions.md`

### Stage 6 — Deploy

- [ ] [L] Implement the `deploy` stage in the pipeline config file: authenticate to the deployment target using credentials from the CI secret store, deploy the scanned and approved image, and restrict this stage to run only on the designated deploy branch or tag pattern
- [ ] [S] Add a manual approval gate (environment protection rule, `when: manual`, or equivalent) to the `deploy` stage in the pipeline config file to prevent unintended production deployments
- [ ] [S] Configure deploy stage rollback or failure notification in the pipeline config file — define the failure action (e.g., alert webhook, automatic rollback command) and document in `docs/cicd-decisions.md`

---

## Phase 3 — Testing & Validation

- [ ] [M] Execute the full pipeline end-to-end on a feature branch and verify all six stages complete successfully — capture stage durations and artifact outputs as the baseline in `docs/cicd-decisions.md`
- [ ] [S] Introduce a deliberate test failure in a scratch branch and confirm the `test` stage correctly blocks downstream stages (`sast`, `container-build`, `image-scan`, `deploy`)
- [ ] [S] Introduce a deliberate high-severity SAST finding in a scratch branch and confirm the `sast` stage blocks the pipeline at the configured threshold
- [ ] [S] Introduce a known-vulnerable base image in a scratch branch `Dockerfile` and confirm the `image-scan` stage blocks the pipeline at the configured CVE threshold
- [ ] [XS] Verify that pipeline artifacts (test report, SAST report, image scan report) are accessible and correctly formatted after a successful pipeline run
- [ ] [XS] Verify that the `deploy` stage does NOT trigger on pull request / non-deploy branches, confirming trigger rules are correctly scoped

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Configure branch protection rules on `main` (and any other deploy branches) in the repository settings to require a passing pipeline before merge
- [ ] [S] Configure pipeline caching keys in the pipeline config file for dependency and build caches — verify cache hit/miss behavior across consecutive runs to confirm cache is effective
- [ ] [S] Configure pipeline concurrency controls in the pipeline config file to cancel in-progress runs on the same branch when a new commit is pushed, preventing redundant resource usage
- [ ] [XS] Add the SAST tool config file (e.g., `.semgrep.yml`) and image scan config (e.g., `trivy.yaml`) to `.gitignore` exclusion review — confirm they ARE tracked in version control and not accidentally ignored
- [ ] [XS] Document all required CI/CD platform secrets (names, descriptions, rotation schedule) in `docs/cicd-decisions.md` for operational handoff

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Write `docs/cicd-pipeline.md` describing each stage's purpose, inputs, outputs, failure behavior, and the tools used — include a pipeline diagram (ASCII or linked image)
- [ ] [S] Write a runbook section in `docs/cicd-pipeline.md` covering: how to re-run a failed stage, how to update SAST/scan thresholds, how to rotate registry and deploy credentials, and how to trigger a manual deploy
- [ ] [XS] Add a pipeline status badge to `README.md` linking to the CI/CD platform's pipeline view
- [ ] [XS] Update `CHANGELOG.md` (or create it) with an entry recording the introduction of the CI/CD pipeline, the tools selected, and the date
- [ ] [S] Conduct a team walkthrough of the live pipeline — run it together, review each stage's artifact output, and confirm all team members can interpret a failure and action a fix
- [ ] [XS] Schedule a 30-day post-rollout review to assess pipeline duration, false-positive rates in SAST/image scan, and threshold calibration — record the review date in `docs/cicd-decisions.md`

---

> **Open Decision Points** (must be resolved before Phase 2 begins):
> 1. CI/CD platform selection
> 2. Container registry selection and authentication method
> 3. Deployment target and deploy mechanism
> 4. SAST tool selection and license/token provisioning
> 5. Image scanning tool selection
> 6. Severity thresholds for SAST and image scan failure gates