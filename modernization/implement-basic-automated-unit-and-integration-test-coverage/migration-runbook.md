# MIGRATION RUNBOOK: Implement Basic Automated Unit and Integration Test Coverage

---

## Pre-Migration Checklist

- [ ] ✅ Source code is committed and pushed to the remote repository.
- [ ] ✅ All current features are stable (no unresolved critical bugs).
- [ ] ✅ Codebase is buildable locally and on CI (if applicable).
- [ ] ✅ Test framework(s) selected and compatible with codebase (see "Environment Setup").
- [ ] ✅ All relevant stakeholders are notified of test coverage changes.
- [ ] ✅ Access to CI/CD system (if applicable) is available and verified.

---

## Environment Setup

1. **Identify Language & Frameworks**
   - Confirm primary application language (e.g., Python, JavaScript, Java, etc.).
   - Research and select a widely-adopted unit/integration test library for that language (e.g., `pytest`, `unittest`, `Jest`, `Mocha`, `JUnit`, etc.).
   - If in doubt, consult team leads or project documentation.

2. **Install Test Libraries**

   - **Python Example**
     ```bash
     pip install pytest
     ```
   - **Node.js Example**
     ```bash
     npm install --save-dev jest
     ```
   - **Java Example**
     ```xml
     <!-- Add to pom.xml -->
     <dependency>
       <groupId>org.junit.jupiter</groupId>
       <artifactId>junit-jupiter</artifactId>
       <version>5.9.2</version>
       <scope>test</scope>
     </dependency>
     ```
   - Confirm successful installation:
     ```bash
     # Python
     pytest --version

     # Node.js
     npx jest --version

     # Java
     mvn test -Dtest=NonExistentTest # (should show nothing ran, but framework available)
     ```
   - Update CI build YAML/pipeline with test steps (e.g., add `pytest`, `jest`, or `mvn test` calls to pipeline file).

3. **Create Test Directory Structure**
   - Follow best practices; e.g.,
     ```
     /tests           # Top-level test folder
     /src or /app     # Source code folder
     ```

---

## Step-by-Step Migration Procedure

1. **Integrate Chosen Test Framework**
   - **Action:** Add test framework to `requirements.txt`, `package.json`, or equivalent manifest.
   - **Expected outcome:** Test framework specified as a dependency; developers can install it.
   - **Verification command:**
     - `pip freeze | grep test`  
     - `npm ls --dev | grep jest`
   - **Rollback action:** Remove dependency from manifest and reinstall dependencies.

2. **Author Basic Unit Tests**
   - **Action:** Write simple unit tests for core functions/methods in `tests/unit` (or equivalent).
   - **Expected outcome:** Unit test files exist and follow framework conventions.
   - **Verification command:**  
     - `pytest tests/unit`  
     - `npx jest tests/unit`
   - **Rollback action:** Remove newly created test files.

3. **Author Basic Integration Tests**
   - **Action:** Write at least one integration test that exercises a flow across multiple components in `tests/integration`.
   - **Expected outcome:** Integration test files exist and simulate high-level use cases.
   - **Verification command:**  
     - `pytest tests/integration`  
     - `npx jest tests/integration`
   - **Rollback action:** Remove newly created test files.

4. **Configure and Run Tests in CI**
   - **Action:** Add test steps to CI configuration (e.g., `.github/workflows/ci.yml`, `.gitlab-ci.yml`, etc.).
   - **Expected outcome:** CI job runs when code is pushed, executing both unit and integration tests.
   - **Verification command:**
     - Trigger a new CI build and confirm test jobs run and pass.
   - **Rollback action:** Remove test steps from CI configuration.

5. **Verify Minimum Test Coverage**
   - **Action:** Run tests with coverage flag enabled (if supported), verify at least minimal coverage is reported.
   - **Expected outcome:** Coverage report is generated, indicating at least baseline coverage.
   - **Verification command:**  
     - `pytest --cov=src`  
     - `npx jest --coverage`
   - **Rollback action:** Remove coverage config or scripts.

---

## Verification & Smoke Tests

- **Local Test Run:**  
  - `pytest`  
  - `npx jest`
- **CI Build:**  
  - Confirm all new test jobs pass in CI pipeline.
- **Test Coverage Report:**  
  - `pytest --cov=src` (Python)  
  - `npx jest --coverage` (Node.js)
- **Manual Verification:**  
  - Confirm tests are failing when defects are introduced (modify code to ensure test fails, then revert).

---

## Rollback Procedure

1. **Remove Unit and Integration Test Files**
   - Delete all test files created under `tests/unit` and `tests/integration`.

2. **Remove Test Framework Dependencies**
   - Remove dependencies from `requirements.txt`, `package.json`, or equivalent.
   - Reinstall/update dependencies.
     - `pip install -r requirements.txt`  
     - `npm install`

3. **Revert CI Configuration**
   - Remove test steps from CI pipeline configuration files.

4. **Commit and Push Rollback**
   - Commit changes with message, e.g., "Rollback: Removing automated tests and related configuration".
   - Push to remote repository.

5. **Notify Stakeholders**
   - Inform team that migration has been rolled back and provide reasoning.

---

## Post-Migration Monitoring

- **Metrics to Monitor:**
  - CI build success/failure rate.
  - Time to execute new test jobs.
  - Frequency of test failures in PRs.

- **Logs to Observe:**
  - Test run output in build logs.
  - Errors related to test setup, import failures, or misconfigurations.

- **Alerts to Configure:**
  - CI/CD pipeline failed build notifications to team email or chat.
  - Optional: Alerts if test coverage drops below an agreed threshold.

- **Suggested Period:** Monitor for at least 24-48 hours after rollout.

---

## Known Issues & Workarounds

- N/A — not applicable to this task

---