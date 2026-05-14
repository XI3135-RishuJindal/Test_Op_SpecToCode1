# Migration Runbook: Flask 3.x Compatibility

---

## Pre-Migration Checklist

All items below must be ✅ before migration starts:

- [ ] ✅ Current codebase is version-controlled and latest changes are committed/pushed.
- [ ] ✅ All tests (unit/integration) are passing on main branch in CI.
- [ ] ✅ Full requirements list (requirements.txt or equivalent) is available and up to date.
- [ ] ✅ Confirmation received that all third-party Flask extensions used are compatible with Flask 3.x, or replacements have been identified.
- [ ] ✅ Staging environment is available for validation.
- [ ] ✅ Backup/restore procedures for application data are documented and tested.

---

## Environment Setup

Prepare both local and CI environments for migration:

```bash
# 1. Create and activate a fresh virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Upgrade pip, setuptools, and wheel
pip install --upgrade pip setuptools wheel

# 3. Install latest Flask 3.x (replace 'x' with latest minor/patch)
pip install "Flask>=3.0,<4.0"
```

- Update `requirements.txt` or dependency manifest:
  - `Flask>=3.0,<4.0`
- For dependencies:
  - Check and update all Flask extensions (e.g. Flask-SQLAlchemy, Flask-Login) to latest compatible versions using their project documentation.
- In CI (example for GitHub Actions):
    - Update setup steps to install Python 3.x and Flask 3.x as above.

---

## Step-by-Step Migration Procedure

### 1. Bump Flask Dependency Version

- **Action:** Update project dependency manifest (e.g., `requirements.txt`, `pyproject.toml`) to require `Flask>=3.0,<4.0`.
- **Expected outcome:** Dependency file lists Flask 3.x.
- **Verification command:**  
  `pip freeze | grep Flask`
- **Rollback:** Revert dependency file to previous version and reinstall dependencies.

### 2. Update and Install Dependencies

- **Action:** Upgrade all dependencies to latest versions compatible with Flask 3.x.
  ```
  pip install -r requirements.txt --upgrade
  ```
- **Expected outcome:** All dependencies and project libraries install without version conflicts.
- **Verification command:**  
  `pip check`
- **Rollback:** Restore prior lock/requirements file and reinstall original dependencies.

### 3. Identify & Refactor Deprecated APIs

- **Action:** Review [Flask 3.x migration guide](https://flask.palletsprojects.com/en/3.0.x/changes/) for breaking changes (e.g., removal of deprecated APIs, Blueprints, import paths, etc.) and update application code accordingly.
- **Expected outcome:** Application code no longer uses any APIs removed/changed in Flask 3.x.
- **Verification command:**  
  `pytest` (or relevant test suite)
- **Rollback:** Revert code changes.

### 4. Update Extension Usage

- **Action:** Update Flask extension usages, ensuring code is using only APIs supported by Flask 3.x extensions, per each extension’s changelog.
- **Expected outcome:** Code is compatible with all updated extensions, no deprecation or removal warnings at runtime.
- **Verification command:**  
  `pytest` and check for runtime warnings/errors in logs.
- **Rollback:** Revert to previous extension versions and usages.

### 5. Local Application Run

- **Action:** Launch application locally with Flask 3.x.
  ```
  flask run
  ```
- **Expected outcome:** Application starts without errors; routes function normally.
- **Verification command:**  
  Access core endpoints in browser or via `curl`.
- **Rollback:** Revert all code and dependency changes.

### 6. Run Test Suite

- **Action:** Execute all automated tests (unit, integration).
- **Expected outcome:** All tests pass.
- **Verification command:**  
  `pytest` or CI pipeline run.
- **Rollback:** Revert changes and rerun tests to restore previous passing state.

### 7. Staging Deployment

- **Action:** Deploy upgraded application to staging environment.
- **Expected outcome:** Application boots and responds to test traffic as expected.
- **Verification command:**  
  Smoke test endpoints and review logs for errors.
- **Rollback:** Redeploy previous stable version.

---

## Verification & Smoke Tests

Run the following after migration:

```bash
# Verify application launches without error
flask run

# Smoke test key endpoints
curl -i http://localhost:5000/            # Replace with actual endpoints
curl -i http://localhost:5000/healthz

# Run full test suite
pytest

# Optionally, test login/flows via browser if app has authentication
```

Verify:

- All routes show expected responses (HTTP 200).
- No import/module errors or deprecation warnings appear in logs.
- Authentication and extension features function as expected.

---

## Rollback Procedure

If migration fails at any point:

1. **Deactivate virtual environment (if active):**
   ```bash
   deactivate
   ```
2. **Restore dependency files (requirements.txt, pyproject.toml) from latest backup or VCS:**
   ```bash
   git checkout main -- requirements.txt
   ```
3. **Remove and recreate virtual environment:**
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Revert code changes:**
   ```bash
   git reset --hard <last_known_good_commit>
   ```
5. **Redeploy previous application version to all affected environments.**
6. **Verify application is restored by running tests and smoke checks.**
7. **Inform team of rollback and investigate failure causes.**

---

## Post-Migration Monitoring

For 24–48 hours post-deployment, monitor:

- Application error logs for new `ImportError`, `TypeError`, or failed imports.
- HTTP 5xx and 4xx rates in metrics/monitoring dashboards.
- Extension/component warnings (deprecation, removed APIs).
- Authentication and extension-dependent endpoint failures.
- User bug reports related to broken routes/flows.

**Alerts:**  
Set up alerts for:

- Application startup failures or repeated restarts.
- Significant increases in error rates.
- Any critical health check failures.

---

## Known Issues & Workarounds

- N/A — not applicable to this task

---