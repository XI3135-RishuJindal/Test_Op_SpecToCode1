## Prerequisites
- [ ] [XS] Confirm requester has authorization to access source code and share repository artifact in onboarding ticket (or equivalent access request record)
- [ ] [XS] Install Git CLI (version N/A — not provided in tech analysis) on the workstation used for validation

## Phase 1 — Preparation
- [ ] [XS] Collect primary source access method (Git URL vs ZIP vs local path) in access-request record (same ticket/thread as above)
- [ ] [XS] Validate Git URL accessibility by running `git ls-remote <git-url>` and recording outcome in access-request record
- [ ] [S] Validate clone access by running `git clone <git-url> <target-dir>` and confirming a working checkout in `<target-dir>/.git/config`
- [ ] [XS] Validate ZIP access by downloading provided archive and confirming it contains a repository root with expected top-level files in extracted folder (e.g., presence/absence notes recorded)
- [ ] [XS] Validate local path access by confirming the path exists and is readable, and recording absolute path and permissions summary in access-request record
- [ ] [XS] Capture source “identity” metadata (commit SHA if Git, archive checksum if ZIP, last-modified timestamp if path) in access-request record

## Phase 2 — Core Upgrade
N/A — not applicable to this task

## Phase 3 — Testing & Validation
- [ ] [XS] Confirm repository integrity by running `git status` (for Git-based access) in the checked-out root and recording clean/dirty state in access-request record
- [ ] [XS] Confirm history availability by running `git rev-parse HEAD` and `git log -1` (for Git-based access) in the checked-out root and recording results in access-request record

## Phase 4 — CI/CD & Infrastructure
N/A — not applicable to this task

## Phase 5 — Documentation & Rollout
- [ ] [XS] Document verified access method(s), canonical source location (Git URL / artifact link / path), and identity metadata in access-request record
- [ ] [XS] Provide handoff note summarizing how to obtain source (exact command or steps) in access-request record