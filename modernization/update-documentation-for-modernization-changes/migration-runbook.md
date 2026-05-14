# Documentation Modernization Migration Runbook

## Pre-Migration Checklist

All must be ✅ before proceeding.

- [ ] ✅ Stakeholder sign-off received for documentation updates.
- [ ] ✅ Access confirmed to all documentation repositories and content management systems.
- [ ] ✅ Backup created of all existing documentation (local and remote).
- [ ] ✅ Chosen style guides/standards for modernization agreed on and documented.
- [ ] ✅ List of documentation targets finalized.


## Environment Setup

- Ensure access to the documentation repository (e.g., Git, Confluence, etc.).
- Set up local text editor or documentation tool (e.g., VS Code, Markdown editor).
- (If applicable) Clone the documentation repository:

  ```sh
  git clone <documentation-repo-url>
  cd <documentation-repo>
  ```

- Verify you have permission to push or create merge requests/pull requests.


## Step-by-Step Migration Procedure

1. **Pull Latest Documentation Content**
   - **Action:** Fetch the latest changes from the default branch.
   - **Expected outcome:** Local copy is up-to-date.
   - **Verification command:**  
     ```sh
     git pull origin main
     ```
   - **Rollback:** Revert local changes if fetch or merge fails.

2. **Standardize Documentation Files**
   - **Action:** Update documentation files to adhere to the new style guide (formatting, headers, structure).
   - **Expected outcome:** All files reflect the agreed modernization standards.
   - **Verification command:**  
     Review changes with:
     ```sh
     git status
     git diff
     ```
   - **Rollback:** Discard changes not meeting standards:
     ```sh
     git checkout -- <file>
     ```

3. **Update All Relevant Content**
   - **Action:** Revise and update outdated content, terminology, images, and references as required.
   - **Expected outcome:** Content is current, clear, and aligned with modernization goals.
   - **Verification command:**  
     Manual review via editor or preview tool.
   - **Rollback:** Revert specific changes as needed.

4. **Run Spellcheck/Linting Tools**
   - **Action:** Execute documentation linters and spelling checkers as per guidelines.
   - **Expected outcome:** No critical spelling or formatting errors reported.
   - **Verification command:**
     ```sh
     # Example for Markdown linting
     markdownlint *.md
     # Example for spell checking
     codespell .
     ```
   - **Rollback:** Fix flagged issues, or revert problematic files.

5. **Commit and Push Changes**
   - **Action:** Commit and push changes to the documentation repository.
   - **Expected outcome:** Updates are available in the remote repository.
   - **Verification command:**
     ```sh
     git add .
     git commit -m "Modernize documentation: applied standards and updates"
     git push origin <branch-name>
     ```
   - **Rollback:** Revert commit or open a pull request for review and possible rejection.

6. **Create Pull/Merge Request for Review**
   - **Action:** Open a pull/merge request and assign reviewers.
   - **Expected outcome:** Await, then collect feedback for further changes before merge.
   - **Verification:** PR/MR visible in repository UI.
   - **Rollback:** Close PR/MR if update not approved.

## Verification & Smoke Tests

- Preview the updated documentation in your local environment or documentation portal.
- Check for broken links with:
  ```sh
  # For Markdown docs (using markdown-link-check)
  npx markdown-link-check *.md
  ```
- Ask a team member to review rendered documentation for readability/completeness.
- Confirm all images and diagrams render correctly.

## Rollback Procedure

1. Revert to original files from backup:
   - Restore documentation from backup made in the Pre-Migration Checklist.

2. If changes have been pushed:
   - Use git to revert the commit:
     ```sh
     git log                # Identify the commit hash
     git revert <commit-hash>
     git push origin <branch-name>
     ```

3. If changes merged to main/default branch:
   - Open a rollback MR/PR to restore content from backup or previous commit.
   - Notify stakeholders of rollback.

## Post-Migration Monitoring

- N/A — not applicable to this task

## Known Issues & Workarounds

- Formatting may appear differently in various documentation portals; preview in all supported environments.
- If linting/spellcheck tools produce false positives, review results manually before correcting.
- Ensure images/links reference correct updated paths after restructuring, correcting as needed.