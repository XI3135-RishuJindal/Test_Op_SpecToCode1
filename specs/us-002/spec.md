### User Story
Title: CI dependency scanning setup
As a Development Lead, I want to set up CI dependency scanning, so that we can ensure no payment SDKs or libraries are included.

### Acceptance Criteria
- CI dependency scans show no payment SDKs/libs in frontend/backend manifests.
- All acceptance criteria must pass before merging.
- CI pipeline successfully runs and validates scans.

### Definition of Done
- All acceptance criteria pass; CI pipeline completes successfully and documentation is updated.

### Out-of-Scope Items
- Manual approval processes for dependencies; scanner evaluations beyond initial setup.

### Constraints
- The scanning tool must integrate seamlessly into the current CI/CD pipeline.

### Cross-Repo Dependencies
- None identified at this time.