# Python Runtime 3.12 Migration Runbook

## Pre-Migration Checklist

_All items must be ✅ before proceeding:_

- [ ] ✅ Project stakeholders notified of planned Python 3.12 upgrade and maintenance window
- [ ] ✅ Existing CI/CD pipelines are passing on current Python version
- [ ] ✅ All code and infrastructure are committed and pushed to source control
- [ ] ✅ A successful, restorable backup of application and data exists
- [ ] ✅ Inventory of all Python dependencies and their version compatibility with Python 3.12 is complete
- [ ] ✅ All developers/engineers have Python 3.12 available locally or access to the upgrade environment

---

## Environment Setup

_Prepare local and CI environments for Python 3.12:_

### Local Environment

1. **Install Python 3.12**
    ```sh
    # On Ubuntu/Debian
    sudo apt update
    sudo apt install -y python3.12 python3.12-venv python3.12-dev

    # On macOS (with Homebrew)
    brew install python@3.12
    ```

2. **Update PATH and aliases if necessary**
    ```sh
    # Example
    alias python3=python3.12
    ```

### CI Environment

1. **Update CI pipeline configuration** (e.g., `.github/workflows/`, `.gitlab-ci.yml`, Jenkinsfile) to use Python 3.12:
    ```yaml
    # Example for GitHub Actions
    jobs:
      build:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - name: Set up Python 3.12
            uses: actions/setup-python@v5
            with:
              python-version: "3.12"
    ```

2. **Rebuild any Docker images or containers**
    - Update `Dockerfile`:
      ```Dockerfile
      FROM python:3.12
      ```
    - Rebuild:
      ```sh
      docker build -t myapp:py312 .
      ```

---

## Step-by-Step Migration Procedure

1. **Pin Python version**
    - _Action:_ Update runtime/version config files (`runtime.txt`, `pyenv`, Dockerfile, CI config) to use Python 3.12
    - _Expected Outcome:_ All project environments use Python 3.12
    - _Verification Command:_
      ```sh
      python3 --version
      # Expected output: Python 3.12.x
      ```
    - _Rollback:_ Restore previous version configuration; re-install prior Python version

2. **Create and activate a fresh virtual environment**
    - _Action:_
      ```sh
      python3.12 -m venv venv312
      source venv312/bin/activate
      ```
    - _Expected Outcome:_ Shell is using new Python 3.12 venv
    - _Verification Command:_
      ```sh
      python --version
      # Expected output: Python 3.12.x
      ```
    - _Rollback:_ Revert to prior virtualenv; activate previous venv

3. **Update pip and setuptools**
    - _Action:_
      ```sh
      python -m pip install --upgrade pip setuptools wheel
      ```
    - _Expected Outcome:_ Latest pip and build tools installed
    - _Verification Command:_
      ```sh
      pip --version
      # Expected output includes pip for Python 3.12
      ```
    - _Rollback:_ Reinstall previous pip/setuptools if issues arise

4. **Reinstall all project dependencies**
    - _Action:_
      ```sh
      pip install -r requirements.txt
      ```
    - _Expected Outcome:_ All dependencies are installed without errors
    - _Verification Command:_
      ```sh
      pip check
      # Expected output: No broken requirements
      ```
    - _Rollback:_ Restore previous requirements or constraints; downgrade problematic packages

5. **Run test suite on Python 3.12**
    - _Action:_
      - If using pytest/unittest/etc.:
        ```sh
        pytest
        # or
        python -m unittest
        ```
    - _Expected Outcome:_ All tests pass
    - _Verification Command:_
      ```sh
      echo $?
      # Expected output: 0
      ```
    - _Rollback:_ Fix failing tests; revert to prior Python version if blockers

6. **Update deployment scripts and environment configs**
    - _Action:_ Modify deployment config (e.g., Dockerfile, process manager configs) to use Python 3.12
    - _Expected Outcome:_ Deployments use Python 3.12
    - _Verification Command:_
      - After deploy, check on target host/container:
        ```sh
        python3 --version
        ```
    - _Rollback:_ Redeploy previous image or restore prior configuration

---

## Verification & Smoke Tests

- Verify application endpoints (API, web interface) function correctly.
- Run regression test suite/end-to-end tests.
- Confirm core business workflows.
- _Sample commands:_
    ```sh
    # Example: basic import test
    python -c "import sys; assert sys.version_info[:2] == (3, 12)"
    # Application-specific
    pytest tests/smoke/
    curl http://localhost:8000/healthz
    ```

---

## Rollback Procedure

1. **Restore Previous Python Version**
    - Switch runtime, venv, and/or Docker image back to previous Python version.

2. **Revert configuration files**
    - Restore old `runtime.txt`, Dockerfile, CI/CD configuration.

3. **Reinstall dependencies for previous Python version**
    - Recreate old virtual environment:
      ```sh
      python3.<OLD_VERSION> -m venv venv_old
      source venv_old/bin/activate
      pip install -r requirements.txt
      ```

4. **Redeploy application**
    - Roll out old deployment scripts or container images.

5. **Verify application health**
    - Check application logs, run health checks and tests.

6. **Notify stakeholders of rollback and status**

---

## Post-Migration Monitoring

_Monitor for 24-48 hours:_

- Application and server logs for Python runtime errors (`SyntaxError`, `ImportError`, deprecated usage)
- Any failures or anomalies in application's primary error monitoring/alerting tools (e.g., Sentry, Datadog)
- CI/CD build/release success
- Core metrics: latency, error rate, crash rate, memory/CPU usage
- Alert on any increase in 5XX errors or process crashes

---

## Known Issues & Workarounds

_N/A — not applicable to this task_