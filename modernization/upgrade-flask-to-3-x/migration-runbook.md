# MIGRATION RUNBOOK: Flask Upgrade to 3.x

## Pre-Migration Checklist
- [ ] ✅ Review Flask 3.x release notes for breaking changes.
- [ ] ✅ Ensure all dependencies are compatible with Flask 3.x.
- [ ] ✅ Update development and CI environment tools (Python, pip, etc.) to required versions.
- [ ] ✅ Create a backup of current application state and database.
- [ ] ✅ Ensure the application is currently functioning (run all existing tests).
- [ ] ✅ Communicate planned downtime to stakeholders.

## Environment Setup
1. Upgrade Python to version 3.8 or higher if not already done:
   ```bash
   sudo apt-get update
   sudo apt-get install python3.8
   ```

2. Upgrade pip and setuptools:
   ```bash
   python3.8 -m pip install --upgrade pip setuptools
   ```

3. Install Flask 3.x and test dependencies:
   ```bash
   python3.8 -m pip install Flask==3.*
   ```

4. Update the CI configuration file (e.g., `.github/workflows/ci.yml`) to use Python 3.8:
   ```yaml
   - name: Set up Python
     uses: actions/setup-python@v2
     with:
       python-version: '3.8'
   ```

## Step-by-Step Migration Procedure
1. **Action**: Update Flask in the `requirements.txt` file or equivalent.
   - **Expected outcome**: Flask version is updated to 3.x in dependency file.
   - **Verification command**: `cat requirements.txt | grep Flask`
   - **Rollback action**: Restore the original `requirements.txt` from backup.

2. **Action**: Modify codebase for any deprecated or breaking features that were removed in Flask 3.x.
   - **Expected outcome**: Code compiles without errors and passes pre-migration tests.
   - **Verification command**: `pytest`
   - **Rollback action**: Check out previous commit with `git checkout <commit_hash>`.

3. **Action**: Run database migrations if necessary (if using Flask-Migrate).
   - **Expected outcome**: Database schema is updated and functional.
   - **Verification command**: `flask db migrate` followed by `flask db upgrade`
   - **Rollback action**: Use `flask db downgrade` to revert to the previous migration.

4. **Action**: Deploy the application to the staging environment.
   - **Expected outcome**: The application starts without errors in staging.
   - **Verification command**: `curl -I http://staging.example.com`
   - **Rollback action**: Redeploy the last stable version from the backup.

5. **Action**: Run application smoke tests in the staging environment.
   - **Expected outcome**: All smoke tests pass successfully.
   - **Verification command**: `pytest smoke_tests/`
   - **Rollback action**: Configure the staging environment to run the last known good version.

6. **Action**: Merge migration branch to the main branch.
   - **Expected outcome**: The main branch reflects the updated codebase.
   - **Verification command**: `git log` to verify commit.
   - **Rollback action**: Revert merge commit with `git revert <commit_hash>`.

7. **Action**: Deploy to production environment.
   - **Expected outcome**: Production reflects the updated codebase with Flask 3.x.
   - **Verification command**: `curl -I http://example.com`
   - **Rollback action**: Roll back the production deployment to previous stable version.

## Verification & Smoke Tests
- Run the following command to check if the application is serving requests correctly:
  ```bash
  curl -I http://example.com
  ```

- Execute the test suite to confirm all functionalities work:
  ```bash
  pytest
  ```

## Rollback Procedure
1. Restore `requirements.txt` from backup.
2. Checkout last good codebase if any migrations have failed.
   ```bash
   git checkout <commit_hash>
   ```
3. Run the application using the previous stable version.
4. Revert any database changes made during the migration:
   ```bash
   flask db downgrade
   ```

5. Inform stakeholders about the rollback.

## Post-Migration Monitoring
- **Metrics to watch**:
  - Response time of endpoints (ensure they are within expected ranges).
  - Error rates (monitor for any increase in 500-level errors).
  
- **Logs**:
  - Check application logs for any critical warnings or errors.
  - Monitor access logs for unusual patterns.

- **Alerts**:
  - Set up alerts for response time exceeding thresholds.
  - Set up alerts for increased error rates in production monitoring tools.

## Known Issues & Workarounds
- N/A — not applicable to this task