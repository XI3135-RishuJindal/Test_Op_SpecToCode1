# Migration Runbook for Upgrading SQLAlchemy to 2.x

## Pre-Migration Checklist
- [ ] Review SQLAlchemy 2.x [migration guide](https://docs.sqlalchemy.org/en/20/changelog/changelog_20.html).
- [ ] Update dependencies in the `requirements.txt` (or equivalent) file to specify `SQLAlchemy>=2.0`.
- [ ] Ensure all unit tests are passing with the current version of SQLAlchemy.
- [ ] Back up the existing database prior to migration.
- [ ] Ensure that the application is running on a local or staging environment that can be temporarily modified.
- [ ] Communicate the migration schedule to the team and stakeholders.

## Environment Setup
1. **Check Python Version**:
   Ensure you are running Python 3.7 or later, as SQLAlchemy 2.x is not compatible with earlier versions.
   ```bash
   python --version
   ```

2. **Install required migration tooling**:
   Upgrade your existing SQLAlchemy version to 2.x in your development environment:
   ```bash
   pip install --upgrade SQLAlchemy
   ```

3. **Update Continuous Integration (CI) Pipeline**:
   Make sure your CI configuration file (e.g., `.github/workflows/ci.yml`, `.travis.yml`) is updated to use a compatible Python version. Define the `SQLAlchemy` dependency.

## Step-by-Step Migration Procedure
1. **Action**: Update SQLAlchemy in `requirements.txt` or the equivalent dependency file.
   - **Expected outcome**: Dependency file is updated to include `SQLAlchemy>=2.0`.
   - **Verification command**: 
     ```bash
     pip freeze | grep SQLAlchemy
     ```
   - **Rollback action if it fails**: Restore the previous version of `SQLAlchemy` in the dependency file and run `pip install -r requirements.txt` to revert.

2. **Action**: Refactor codebase to address the breaking changes and required updates as per SQLAlchemy 2.x migration guide.
   - **Expected outcome**: Codebase passes static analysis checks and compiles without errors.
   - **Verification command**: 
     ```bash
     flake8 .
     ```
   - **Rollback action if it fails**: Revert the code changes by restoring from version control or applying a stash.

3. **Action**: Run the application locally to verify functionality.
   - **Expected outcome**: Application starts successfully without errors.
   - **Verification command**: 
     ```bash
     python app.py  # or the command used to run your application
     ```
   - **Rollback action if it fails**: Restore previous dependencies and code changes, then rerun the application.

4. **Action**: Execute unit tests to ensure all functionalities are working.
   - **Expected outcome**: All tests pass without failures.
   - **Verification command**: 
     ```bash
     pytest  # or whichever test framework you are using
     ```
   - **Rollback action if it fails**: Address test failures or revert the codebase to its previous state.

5. **Action**: Deploy the updated application to the staging environment.
   - **Expected outcome**: Application is successfully deployed to staging with SQLAlchemy 2.x.
   - **Verification command**: 
     ```bash
     curl http://staging-url/healthcheck
     ```
   - **Rollback action if it fails**: Redeploy the previous version of the application.

## Verification & Smoke Tests
1. **Login Smoke Test**:
   ```bash
   curl -X POST http://staging-url/login -d '{"username": "test", "password": "test"}'
   ```

2. **Database Connection Test**:
   ```bash
   python -c "from sqlalchemy import create_engine; engine = create_engine('DATABASE_URL'); print(engine.execute('SELECT 1')).scalar()"
   ```

3. **Basic Endpoint Test**:
   ```bash
   curl http://staging-url/api/data
   ```

## Rollback Procedure
1. **Action**: Revert the changes in `requirements.txt` to the previous version of SQLAlchemy.
   - **Expected outcome**: Dependency reverts successfully.
   - **Rollback command**: 
     ```bash
     pip install -r requirements.txt
     ```

2. **Action**: Revert the codebase to the previous commit or reset any local changes made.
   - **Expected outcome**: Codebase is reverted.
   - **Rollback command**:
     ```bash
     git checkout HEAD~1  # Adjust as necessary to revert changes
     ```

3. **Action**: Redeploy the previous version of the application.
   - **Expected outcome**: Application is back to the previous working state.
   - **Rollback command**: 
     ```bash
     git checkout <commit_hash_for_previous_version>
     ```

4. **Action**: Verify that the previous version of the application is functioning correctly.
   - **Expected outcome**: Application is operating normally without SQLAlchemy 2.x.
   - **Rollback command**: 
     ```bash
     curl http://previous-url/healthcheck
     ```

## Post-Migration Monitoring
- **Metrics**: Monitor database query performance metrics via your APM (Application Performance Monitoring) tool.
- **Logs**: Check application logs for any error patterns or deprecation warnings related to SQLAlchemy.
- **Alerts**: Set up alerts for any increase in response times or error rates over the 24-48 hour deployment window.

## Known Issues & Workarounds
- Some ORM queries may fail if they were using deprecated methods; refactoring using the new syntax is necessary.
- If there are custom connections or legacy code that rely on old SQLAlchemy behaviors, consider isolating those and adapting them in the next sprint.