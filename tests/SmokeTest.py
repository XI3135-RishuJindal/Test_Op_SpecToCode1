import unittest
import os
import yaml

class TestCIWorkflowUpgrade(unittest.TestCase):
    CI_WORKFLOW_PATH = os.path.join('.github', 'workflows', 'ci.yml')
    TARGET_VERSION = 'latest stable'

    def setUp(self):
        if not os.path.exists(self.CI_WORKFLOW_PATH):
            self.fail(f"CI workflow file not found at expected path: {self.CI_WORKFLOW_PATH}")
        with open(self.CI_WORKFLOW_PATH, 'r') as f:
            self.workflow = yaml.safe_load(f)

    def test_ci_workflow_version_annotation(self):
        # There may be no explicit version field, so we check for an identifying mark.
        # For this upgrade context, look for 'uses: actions/checkout@v3' or similar latest-stable markers.
        jobs = self.workflow.get('jobs', {})
        found_latest = False
        for job in jobs.values():
            steps = job.get('steps', [])
            for step in steps:
                uses = step.get('uses', '')
                if 'actions/checkout' in uses:
                    # Accept any commonly used latest-stable tag, e.g., '@v3' or '@latest'.
                    if '@v3' in uses or '@latest' in uses or 'stable' in uses:
                        found_latest = True
        self.assertTrue(found_latest, f"CI workflow must use 'actions/checkout' at {self.TARGET_VERSION} or latest stable.")

    def test_linting_job_present_and_runs(self):
        jobs = self.workflow.get('jobs', {})
        lint_job = None
        for name, job in jobs.items():
            if 'lint' in name.lower():
                lint_job = job
                break
        self.assertIsNotNone(lint_job, "CI workflow must include a linting job.")

        has_run_lint = False
        for step in lint_job['steps']:
            if 'lint' in step.get('name', '').lower() or 'lint' in step.get('run', ''):
                has_run_lint = True
        self.assertTrue(has_run_lint, "Linting job must run a linting command.")

    def test_testing_job_present_and_runs(self):
        jobs = self.workflow.get('jobs', {})
        test_job = None
        for name, job in jobs.items():
            if 'test' in name.lower():
                test_job = job
                break
        self.assertIsNotNone(test_job, "CI workflow must include a testing job.")

        has_run_tests = False
        for step in test_job['steps']:
            if 'test' in step.get('name', '').lower() or 'test' in step.get('run', ''):
                has_run_tests = True
        self.assertTrue(has_run_tests, "Testing job must run a test command.")

    def test_no_deprecated_workflow_keys(self):
        # Check for deprecated keys like 'runs-on: ubuntu-latest' misspelling, or 'actions/setup-python@v1'
        jobs = self.workflow.get('jobs', {})
        for job in jobs.values():
            for step in job.get('steps', []):
                uses = step.get('uses', '')
                # For demonstration, assume actions/setup-python@v1 is deprecated; verify v2 or higher used if present.
                if 'actions/setup-python' in uses:
                    self.assertTrue(
                        '@v2' in uses or '@v3' in uses or '@latest' in uses or 'stable' in uses,
                        "CI workflow should not use deprecated 'actions/setup-python@v1', must use v2 or higher."
                    )

    def test_new_workflow_configuration_keys_load(self):
        # For this upgrade, validate that 'on' (trigger), 'jobs', and at least two jobs (lint & test) exist.
        self.assertIn('on', self.workflow, "CI workflow must define triggers in the 'on' key.")
        self.assertIn('jobs', self.workflow, "CI workflow must define 'jobs'.")
        jobs = self.workflow['jobs']
        self.assertGreaterEqual(len(jobs), 2, "CI workflow should define at least two jobs (lint and test).")

if __name__ == "__main__":
    unittest.main()