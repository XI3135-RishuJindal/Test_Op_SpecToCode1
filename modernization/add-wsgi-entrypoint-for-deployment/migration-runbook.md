# MIGRATION RUNBOOK: Add WSGI Entrypoint for Deployment

## Pre-Migration Checklist

- [ ] ✅ Confirm application is a Python web application and compatible with WSGI (e.g., Flask, Django, etc.)
- [ ] ✅ Identify main application module and callable object (e.g., `app`, `application`)
- [ ] ✅ Ensure local development environment matches production Python and dependency versions
- [ ] ✅ All current tests pass in CI/CD
- [ ] ✅ Code freeze (no other changes merged during this migration)
- [ ] ✅ Stakeholders notified about migration window
- [ ] ✅ Rollback plan reviewed and approved

---

## Environment Setup

1. **Install WSGI server (e.g., gunicorn, uWSGI) locally and in CI**
   
   **Commands:**
   ```sh
   # Example for Gunicorn
   pip install gunicorn
   ```

2. **Add WSGI server to project dependencies**
   
   - If using `requirements.txt`:
     ```sh
     echo "gunicorn" >> requirements.txt
     ```
   - OR with Poetry/Pipenv/etc.:
     ```sh
     poetry add gunicorn
     ```
     or
     ```sh
     pipenv install gunicorn
     ```

3. **Ensure virtual environment is activated:**
   ```sh
   python -m venv venv
   source venv/bin/activate
   ```

---

## Step-by-Step Migration Procedure

1. **Add WSGI entrypoint file**

    - **Action:**  
      Create `wsgi.py` at the project root with content suited to your framework. Example for Flask:

      ```python
      from myapp import app

      if __name__ == "__main__":
          app.run()
      ```

      For Django (adjust as necessary):

      ```python
      import os
      from django.core.wsgi import get_wsgi_application

      os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myproject.settings")
      application = get_wsgi_application()
      ```

    - **Expected outcome:**  
      WSGI entrypoint (`wsgi.py`) exists and imports the production-ready application callable.

    - **Verification command:**  
      ```sh
      python wsgi.py  # Should start local server with no error (for Flask)
      ```

    - **Rollback action if it fails:**  
      Delete `wsgi.py`.

2. **Update deployment scripts/processes to use WSGI server**

    - **Action:**  
      Modify deployment scripts (Dockerfile, Procfile, etc.) to launch the app with the WSGI server, e.g.:
      ```sh
      gunicorn --bind 0.0.0.0:8000 wsgi:app
      ```
      (Replace `app` with your callable as appropriate.)

    - **Expected outcome:**  
      Application starts via WSGI server in deployment environment.

    - **Verification command:**  
      ```sh
      gunicorn --bind 127.0.0.1:8000 wsgi:app
      curl -I http://127.0.0.1:8000/
      ```

    - **Rollback action if it fails:**  
      Revert deployment scripts to prior state; redeploy.

3. **Update documentation and inform team**

    - **Action:**  
      Document `wsgi.py` and new server start procedure.

    - **Expected outcome:**  
      Team is aware of how to start and debug the app with WSGI.

    - **Verification command:**  
      N/A (manual confirmation)

    - **Rollback action if it fails:**  
      Restore prior documentation and communicate as before.

---

## Verification & Smoke Tests

1. **Start application locally via WSGI server**
   ```sh
   gunicorn --bind 127.0.0.1:8000 wsgi:app
   ```

2. **Test main endpoints**
   ```sh
   curl -I http://127.0.0.1:8000/
   # Verify status 200 OK
   ```

3. **Run existing automated tests**
   ```sh
   pytest
   # Or your project’s test tool
   ```

---

## Rollback Procedure

1. **Restore previous deployment scripts/processes**

    - Revert any changes to Dockerfile, Procfile, or other process managers to previous non-WSGI commands.
    - Redeploy the previous release.

2. **Remove `wsgi.py` entrypoint**
   
    - Delete the `wsgi.py` file added during migration.

3. **Remove WSGI server from dependencies if it was newly added**
   ```sh
   pip uninstall gunicorn
   ```
   Or remove from `requirements.txt` and reinstall.

4. **Confirm application starts as before**
   ```sh
   # Use the original (pre-migration) startup command
   ```

5. **Communicate rollback to stakeholders**

---

## Post-Migration Monitoring

- **Application Logs**  
  - Monitor WSGI server logs for startup errors, import errors, or unhandled exceptions.
- **Response Metrics**  
  - Monitor HTTP 4xx/5xx error rates.
  - Check response latency and throughput.
- **Alerts**  
  - Set up alerts for WSGI server process failures or restarts.
  - Track application uptime and user error reports.

Monitor for at least 24-48 hours post deployment.

---

## Known Issues & Workarounds

- **Issue:** Module import errors in `wsgi.py`  
  - **Workaround:** Confirm correct import paths, ensure all dependencies are installed.

- **Issue:** Environment variable not set (e.g., Django's `DJANGO_SETTINGS_MODULE`)  
  - **Workaround:** Set environment variable in deployment environment or within `wsgi.py`.

- **Issue:** Gunicorn fails to find callable  
  - **Workaround:** Check that the callable name in the launch command matches what is defined in `wsgi.py` (e.g., `wsgi:app`).

---