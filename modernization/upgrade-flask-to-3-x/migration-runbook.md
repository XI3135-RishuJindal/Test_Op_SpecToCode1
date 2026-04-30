# Flask Upgrade Migration Runbook

## Pre-Migration Checklist
- [ ] Verify the current Flask version is 2.x
- [ ] Backup the current application and database
- [ ] Ensure all dependencies are compatible with Flask 3.x
- [ ] Update documentation to reflect the upgrade
- [ ] Gain approval from project stakeholders

## Environment Setup
1. Upgrade pip to the latest version:
   ```bash
   pip install --upgrade pip
   ```
2. Create or update a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install the required dependencies as specified in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

## Step-by-Step Migration Procedure
1. **Action**: Update the Flask version in `requirements.txt` file.
   - **Expected outcome**: The requirements file reflects the new version Flask==3.x.
   - **Verification command**: 
     ```bash
     grep "Flask==" requirements.txt
     ```
   - **Rollback action if it fails**: Restore the `requirements.txt` from backup.

2. **Action**: Upgrade Flask using pip.
   - **Expected outcome**: Flask 3.x is installed.
   - **Verification command**: 
     ```bash
     pip show Flask
     ```
   - **Rollback action if it fails**: Reinstall the previous version of Flask:
     ```bash
     pip install Flask==2.x
     ```

3. **Action**: Review and update the application code for any breaking changes introduced in Flask 3.x.
   - **Expected outcome**: Code is compliant with Flask 3.x requirements.
   - **Verification command**: Use `pytest` or an equivalent testing framework:
     ```bash
     pytest
     ```
   - **Rollback action if it fails**: Restore the codebase from the backup.

4. **Action**: Run migrations related to the application (if applicable).
   - **Expected outcome**: Migrations run successfully.
   - **Verification command**: 
     ```bash
     flask db upgrade
     ```
   - **Rollback action if it fails**: Revert the database to the previous state using backup.

## Verification & Smoke Tests
- Start the Flask application:
  ```bash
  flask run
  ```
- Access the application in a browser at `http://localhost:5000` to confirm it loads successfully.
- Run core endpoint tests to ensure expected responses.

## Rollback Procedure
1. **Action**: Deactivate the current virtual environment.
   ```bash
   deactivate
   ```
   
2. **Action**: Restore the previous version of Flask in `requirements.txt`.
   - Restore the previous copy from backup if necessary.
   
3. **Action**: Recreate and activate the virtual environment.
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Action**: Reinstall dependencies from the previous `requirements.txt`.
   ```bash
   pip install -r requirements.txt
   ```

5. **Action**: Restore the application code from the backup if changes were made.
   - Replace the files with the backup.

6. **Action**: Run the application again to ensure stability.
   ```bash
   flask run
   ```

## Post-Migration Monitoring
- Monitor application logs for errors and warnings within the first 24-48 hours:
  - Check for 500 and 404 errors.
  - Track response times and request counts.
- Set up alerts for any exceptions logged during this period.
- Review database performance metrics, focusing on query times and error logs.

## Known Issues & Workarounds
- N/A — not applicable to this task.