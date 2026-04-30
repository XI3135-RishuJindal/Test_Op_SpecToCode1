# Migration Runbook: Implementing Unit Tests Across Services and Controllers

## Pre-Migration Checklist
- [ ] ✅ Review and understand the existing codebase structure for services and controllers.
- [ ] ✅ Identify which services and controllers require unit tests.
- [ ] ✅ Confirm that the required testing frameworks are available in the environment.
- [ ] ✅ Ensure there is a code coverage baseline.
- [ ] ✅ Validate that a branching strategy (e.g., feature branch) is in place to avoid conflicts.

## Environment Setup
1. Install the testing framework if not present (examples include Jest for JavaScript, JUnit for Java, etc.):
   ```bash
   # For JavaScript with Jest
   npm install --save-dev jest
   ```
   
2. Configure the test environment:
   - For Jest, add the following to the `package.json`:
   ```json
   "scripts": {
     "test": "jest"
   }
   ```

3. Update CI configuration to include test execution:
   (Example for a CI tool like GitHub Actions)
   ```yaml
   steps:
     - name: Run tests
       run: npm test
   ```

## Step-by-Step Migration Procedure
1. **Action**: Identify a service to start implementing unit tests.
   - **Expected outcome**: A specific service is chosen for initial unit tests.
   - **Verification command**: Review codebase to ensure service selection.
   - **Rollback action if it fails**: No rollback required; simply choose another service.

2. **Action**: Write unit tests for the chosen service.
   - **Expected outcome**: Unit tests are created and structured properly.
   - **Verification command**: Run `npm test` or appropriate command for the chosen framework to ensure tests compile.
   - **Rollback action if it fails**: Remove or comment out any failing tests and review implementation.

3. **Action**: Run unit tests and achieve desired test coverage.
   - **Expected outcome**: All tests pass successfully, achieving at least the baseline coverage.
   - **Verification command**: Review test output and code coverage report.
   - **Rollback action if it fails**: Investigate failing tests; rectify issues or rollback code changes if necessary.

4. **Action**: Implement unit tests for additional identified services/controllers.
   - **Expected outcome**: Each identified service/controller is fully tested.
   - **Verification command**: Consistently run the testing command during implementation.
   - **Rollback action if it fails**: Revisit the implementation of tests for the specific failing service/controller.

## Verification & Smoke Tests
- Run all unit tests after migration:
  ```bash
  npm test
  ```
- Check test coverage report to ensure it meets the baseline:
  ```bash
  npm run test -- --coverage
  ```

## Rollback Procedure
1. Remove newly added unit tests if they consistently fail:
   ```bash
   git checkout HEAD~1 -- path/to/new-tests
   ```

2. Restore code to the last stable state prior to migration:
   ```bash
   git checkout main
   ```

## Post-Migration Monitoring
- Monitor test results in CI/CD pipeline for subsequent pushes for 24-48 hours.
- Check code coverage reports to confirm new tests are included.
- Set alerts for any failures in the CI workflow due to tests.

## Known Issues & Workarounds
- **Issue**: Tests may fail due to external dependencies (e.g., database connections).
  - **Workaround**: Use mocking frameworks to simulate external calls.
- **Issue**: Inconsistent test results due to environment differences.
  - **Workaround**: Ensure a consistent testing environment across local and CI. Use Docker or similar tools for uniformity.