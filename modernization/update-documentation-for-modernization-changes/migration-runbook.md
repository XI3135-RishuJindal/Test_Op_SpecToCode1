# MIGRATION RUNBOOK  
_Update Documentation for Modernization Changes_

---

## Pre-Migration Checklist

- [ ] ✅ Identify all documentation sets affected by modernization.
- [ ] ✅ Gather change log or summary of modernization changes.
- [ ] ✅ Confirm access to documentation repository (e.g., GitHub, GitLab).
- [ ] ✅ Ensure write permissions to the documentation branches.
- [ ] ✅ Notify stakeholders/documentation owners of planned update.

---

## Environment Setup

- Clone the documentation repository:
  ```sh
  git clone <REPO_URL>
  cd <REPO_FOLDER>
  ```
- (If using static site generators or docs tools) Install required dependencies:
  ```sh
  # Example for mkdocs
  pip install mkdocs

  # Example for Sphinx
  pip install sphinx
  ```
- (Optional) Setup pre-commit hooks for documentation linting if configured:
  ```sh
  pre-commit install
  ```

---

## Step-by-Step Migration Procedure

1. **Review Modernization Changes**
    - **Action:** Open the change log or summary describing the modernization efforts.
    - **Expected outcome:** Clear understanding of the new/changed features that require documentation updates.
    - **Verification command:** N/A (manual review).
    - **Rollback action if it fails:** Escalate to project lead for clarification before proceeding.

2. **Identify Impacted Documentation**
    - **Action:** Search the documentation repo for mentions of modified/removed features.
    - **Expected outcome:** List of affected files to be updated.
    - **Verification command:** Manual search or grep, e.g.,
      ```sh
      grep -ri '<deprecated-feature>' docs/
      ```
    - **Rollback action if it fails:** Request feature owner input.

3. **Update Documentation Content**
    - **Action:** Edit identified files to accurately describe modernized features, update screenshots/code samples if necessary.
    - **Expected outcome:** Documentation reflects the current, modernized system behavior.
    - **Verification command:** 
      ```sh
      git diff
      ```
    - **Rollback action if it fails:** Revert changes with:
      ```sh
      git checkout -- <affected-files>
      ```
  
4. **Preview Documentation Locally**
    - **Action:** Build and preview documentation using the local build tool (e.g., mkdocs serve, sphinx-build).
    - **Expected outcome:** Clean build; updated content displayed correctly.
    - **Verification command:**
      ```
      mkdocs serve
      # or
      sphinx-build -b html source/ build/
      ```
    - **Rollback action if it fails:** Address build errors or revert last content change.

5. **Commit and Push Changes**
    - **Action:** Commit documentation updates with a clear message and push to the relevant branch.
    - **Expected outcome:** Changes are available in the central repository.
    - **Verification command:**
      ```sh
      git status
      git commit -am "Update docs for modernization changes"
      git push origin <branch>
      ```
    - **Rollback action if it fails:** Amend or reset commit as necessary.

6. **Open Pull Request / Merge Request**
    - **Action:** Follow standard repo process to merge changes after review.
    - **Expected outcome:** Documentation updates are merged into mainline.
    - **Verification command:** Confirm via repo UI (GitHub, GitLab, etc.).
    - **Rollback action if it fails:** Close or update PR/MR as needed.

---

## Verification & Smoke Tests

- Render documentation to ensure formatting is correct:
  ```sh
  mkdocs build
  # or
  sphinx-build -b html source/ build/
  ```
- Visually inspect updated documentation sections.
- If applicable, run any configured documentation linter/test scripts:
  ```sh
  # Example:
  markdownlint docs/
  ```

---

## Rollback Procedure

1. **Identify Documentation Change Commit(s)**
    - Use:
      ```sh
      git log
      ```

2. **Revert the Commit(s)**
    - Use:
      ```sh
      git revert <commit-hash>
      git push origin <branch>
      ```

3. **Rebuild and Deploy Documentation**
    - Confirm site is restored to the previous state.

4. **Notify Stakeholders**
    - Communicate that docs have been reverted and follow up for further action.

---

## Post-Migration Monitoring

- N/A — not applicable to this task

---

## Known Issues & Workarounds

- N/A — not applicable to this task

---