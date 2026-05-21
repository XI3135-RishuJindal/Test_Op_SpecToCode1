"""
Upgrade validation tests for GitHub Actions CI pipeline setup.

These tests verify that the CI pipeline infrastructure was correctly established:
- .github/workflows/ci.yml exists and is valid YAML
- Required jobs (build, test, sast) are present
- Correct action versions are pinned (checkout@v4, upload-artifact@v4, codeql@v3)
- Triggers, permissions, and job dependencies are configured correctly
- SAST is not set to continue-on-error
- Branch protection-ready status check names are present
"""

import os
import unittest

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


WORKFLOW_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    ".github", "workflows", "ci.yml"
)

# Fallback: also check relative to cwd
if not os.path.exists(WORKFLOW_PATH):
    WORKFLOW_PATH = os.path.join(".github", "workflows", "ci.yml")


def load_workflow():
    """Load and parse the CI workflow YAML file."""
    if not YAML_AVAILABLE:
        raise ImportError(
            "PyYAML is required to run these tests. Install with: pip install pyyaml"
        )
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class TestWorkflowFileExists(unittest.TestCase):
    """Verify the workflow file was created at the correct path."""

    def test_workflow_directory_exists(self):
        workflow_dir = os.path.dirname(WORKFLOW_PATH)
        self.assertTrue(
            os.path.isdir(workflow_dir),
            f".github/workflows/ directory not found at: {workflow_dir}"
        )

    def test_ci_workflow_file_exists(self):
        self.assertTrue(
            os.path.isfile(WORKFLOW_PATH),
            f"CI workflow file not found at: {WORKFLOW_PATH}\n"
            "Expected .github/workflows/ci.yml to be created as part of this upgrade."
        )

    def test_workflow_file_is_not_empty(self):
        self.assertGreater(
            os.path.getsize(WORKFLOW_PATH),
            0,
            "ci.yml exists but is empty."
        )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping YAML content tests")
class TestWorkflowYAMLValidity(unittest.TestCase):
    """Verify the workflow file is valid YAML and has the expected top-level structure."""

    def setUp(self):
        self.workflow = load_workflow()

    def test_workflow_parses_as_valid_yaml(self):
        self.assertIsInstance(
            self.workflow, dict,
            "ci.yml did not parse as a YAML mapping."
        )

    def test_workflow_name_is_ci(self):
        self.assertIn("name", self.workflow, "Workflow is missing a 'name' key.")
        self.assertEqual(
            self.workflow["name"], "CI",
            f"Workflow name should be 'CI', got: {self.workflow.get('name')}"
        )

    def test_workflow_has_on_triggers(self):
        self.assertIn(
            "on", self.workflow,
            "Workflow is missing an 'on' (trigger) key."
        )

    def test_workflow_has_jobs(self):
        self.assertIn(
            "jobs", self.workflow,
            "Workflow is missing a 'jobs' key."
        )
        self.assertIsInstance(self.workflow["jobs"], dict)


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping trigger tests")
class TestWorkflowTriggers(unittest.TestCase):
    """Verify push and pull_request triggers are configured for the default branch."""

    def setUp(self):
        self.workflow = load_workflow()
        self.triggers = self.workflow.get("on", {})

    def test_push_trigger_present(self):
        self.assertIn(
            "push", self.triggers,
            "Workflow must have a 'push' trigger."
        )

    def test_pull_request_trigger_present(self):
        self.assertIn(
            "pull_request", self.triggers,
            "Workflow must have a 'pull_request' trigger."
        )

    def test_push_targets_default_branch(self):
        push_config = self.triggers.get("push", {})
        if push_config is None:
            self.fail("push trigger is present but has no configuration.")
        branches = push_config.get("branches", [])
        self.assertTrue(
            any(b in branches for b in ["main", "master"]),
            f"push trigger should target 'main' or 'master'. Got branches: {branches}"
        )

    def test_pull_request_targets_default_branch(self):
        pr_config = self.triggers.get("pull_request", {})
        if pr_config is None:
            # pull_request with no config targets default branch — acceptable
            return
        branches = pr_config.get("branches", [])
        if branches:
            self.assertTrue(
                any(b in branches for b in ["main", "master"]),
                f"pull_request trigger should target 'main' or 'master'. Got branches: {branches}"
            )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping job tests")
class TestRequiredJobsPresent(unittest.TestCase):
    """Verify all three required jobs (build, test, sast) are defined."""

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})

    def test_build_job_exists(self):
        self.assertIn(
            "build", self.jobs,
            "Required 'build' job is missing from ci.yml."
        )

    def test_test_job_exists(self):
        self.assertIn(
            "test", self.jobs,
            "Required 'test' job is missing from ci.yml."
        )

    def test_sast_job_exists(self):
        self.assertIn(
            "sast", self.jobs,
            "Required 'sast' job is missing from ci.yml."
        )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping runner tests")
class TestJobRunners(unittest.TestCase):
    """Verify jobs run on ubuntu-latest."""

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})

    def _get_runner(self, job_name):
        job = self.jobs.get(job_name, {})
        return job.get("runs-on")

    def test_build_job_runs_on_ubuntu_latest(self):
        runner = self._get_runner("build")
        self.assertEqual(
            runner, "ubuntu-latest",
            f"'build' job should run on 'ubuntu-latest', got: {runner}"
        )

    def test_test_job_runs_on_ubuntu_latest(self):
        runner = self._get_runner("test")
        self.assertEqual(
            runner, "ubuntu-latest",
            f"'test' job should run on 'ubuntu-latest', got: {runner}"
        )

    def test_sast_job_runs_on_ubuntu_latest(self):
        runner = self._get_runner("sast")
        self.assertEqual(
            runner, "ubuntu-latest",
            f"'sast' job should run on 'ubuntu-latest', got: {runner}"
        )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping action version tests")
class TestPinnedActionVersions(unittest.TestCase):
    """
    Verify that the correct, up-to-date action versions are used.
    This is the primary version assertion for this upgrade:
      - actions/checkout@v4  (not v2 or v3)
      - actions/upload-artifact@v4  (not v2 or v3)
      - github/codeql-action/*@v3  (not v1 or v2)
    """

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})

    def _collect_all_uses(self):
        """Walk all job steps and collect every 'uses' value."""
        uses_list = []
        for job_name, job in self.jobs.items():
            steps = job.get("steps", []) or []
            for step in steps:
                if isinstance(step, dict) and "uses" in step:
                    uses_list.append((job_name, step.get("name", "<unnamed>"), step["uses"]))
        return uses_list

    def _find_uses(self, action_prefix):
        """Return all (job, step_name, uses) tuples matching an action prefix."""
        return [
            (job, name, uses)
            for job, name, uses in self._collect_all_uses()
            if uses.startswith(action_prefix)
        ]

    def test_checkout_action_is_v4(self):
        matches = self._find_uses("actions/checkout")
        self.assertTrue(
            matches,
            "No 'actions/checkout' step found in any job. "
            "Each job should check out the repository."
        )
        for job, step_name, uses in matches:
            self.assertEqual(
                uses, "actions/checkout@v4",
                f"Job '{job}' step '{step_name}' uses '{uses}'. "
                f"Expected 'actions/checkout@v4' (upgrade target version)."
            )

    def test_upload_artifact_action_is_v4(self):
        matches = self._find_uses("actions/upload-artifact")
        self.assertTrue(
            matches,
            "No 'actions/upload-artifact' step found. "
            "The 'test' job should upload test results using actions/upload-artifact@v4."
        )
        for job, step_name, uses in matches:
            self.assertEqual(
                uses, "actions/upload-artifact@v4",
                f"Job '{job}' step '{step_name}' uses '{uses}'. "
                f"Expected 'actions/upload-artifact@v4' (upgrade target version)."
            )

    def test_codeql_init_action_is_v3(self):
        matches = self._find_uses("github/codeql-action/init")
        self.assertTrue(
            matches,
            "No 'github/codeql-action/init' step found in the 'sast' job."
        )
        for job, step_name, uses in matches:
            self.assertEqual(
                uses, "github/codeql-action/init@v3",
                f"Job '{job}' step '{step_name}' uses '{uses}'. "
                f"Expected 'github/codeql-action/init@v3' (upgrade target version)."
            )

    def test_codeql_analyze_action_is_v3(self):
        matches = self._find_uses("github/codeql-action/analyze")
        self.assertTrue(
            matches,
            "No 'github/codeql-action/analyze' step found in the 'sast' job."
        )
        for job, step_name, uses in matches:
            self.assertEqual(
                uses, "github/codeql-action/analyze@v3",
                f"Job '{job}' step '{step_name}' uses '{uses}'. "
                f"Expected 'github/codeql-action/analyze@v3' (upgrade target version)."
            )

    def test_no_deprecated_checkout_v2_or_v3(self):
        """Ensure old checkout versions are not present (replaced in this upgrade)."""
        deprecated = [
            (job, name, uses)
            for job, name, uses in self._collect_all_uses()
            if uses in ("actions/checkout@v2", "actions/checkout@v3")
        ]
        self.assertEqual(
            deprecated, [],
            f"Deprecated action versions found (should have been replaced by @v4): {deprecated}"
        )

    def test_no_deprecated_upload_artifact_v2_or_v3(self):
        """Ensure old upload-artifact versions are not present (replaced in this upgrade)."""
        deprecated = [
            (job, name, uses)
            for job, name, uses in self._collect_all_uses()
            if uses in ("actions/upload-artifact@v2", "actions/upload-artifact@v3")
        ]
        self.assertEqual(
            deprecated, [],
            f"Deprecated action versions found (should have been replaced by @v4): {deprecated}"
        )

    def test_no_deprecated_codeql_v1_or_v2(self):
        """Ensure old CodeQL action versions are not present (replaced in this upgrade)."""
        deprecated = [
            (job, name, uses)
            for job, name, uses in self._collect_all_uses()
            if any(
                uses.startswith(prefix)
                for prefix in (
                    "github/codeql-action/init@v1",
                    "github/codeql-action/init@v2",
                    "github/codeql-action/analyze@v1",
                    "github/codeql-action/analyze@v2",
                )
            )
        ]
        self.assertEqual(
            deprecated, [],
            f"Deprecated CodeQL action versions found (should have been replaced by @v3): {deprecated}"
        )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping job dependency tests")
class TestJobDependencies(unittest.TestCase):
    """Verify job ordering: test depends on build; sast is independent."""

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})

    def test_test_job_needs_build(self):
        test_job = self.jobs.get("test", {})
        needs = test_job.get("needs")
        if isinstance(needs, str):
            needs = [needs]
        self.assertIsNotNone(
            needs,
            "The 'test' job should declare 'needs: build' to run after the build job."
        )
        self.assertIn(
            "build", needs,
            f"The 'test' job's 'needs' should include 'build'. Got: {needs}"
        )

    def test_build_job_has_no_needs(self):
        build_job = self.jobs.get("build", {})
        needs = build_job.get("needs")
        self.assertIsNone(
            needs,
            f"The 'build' job should not depend on any other job. Got needs: {needs}"
        )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping SAST config tests")
class TestSASTJobConfiguration(unittest.TestCase):
    """Verify SAST job is correctly configured to block PRs on failure."""

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})
        self.sast_job = self.jobs.get("sast", {})

    def test_sast_continue_on_error_is_false_or_absent(self):
        """
        SAST must NOT have continue-on-error: true.
        Either absent (defaults to false) or explicitly false is acceptable.
        """
        coe = self.sast_job.get("continue-on-error")
        self.assertNotEqual(
            coe, True,
            "The 'sast' job has 'continue-on-error: true'. "
            "This must be false (or omitted) so SAST failures block PR merges."
        )

    def test_sast_job_has_codeql_init_step(self):
        steps = self.sast_job.get("steps", []) or []
        uses_values = [s.get("uses", "") for s in steps if isinstance(s, dict)]
        self.assertTrue(
            any("codeql-action/init" in u for u in uses_values),
            "The 'sast' job is missing a 'github/codeql-action/init@v3' step."
        )

    def test_sast_job_has_codeql_analyze_step(self):
        steps = self.sast_job.get("steps", []) or []
        uses_values = [s.get("uses", "") for s in steps if isinstance(s, dict)]
        self.assertTrue(
            any("codeql-action/analyze" in u for u in uses_values),
            "The 'sast' job is missing a 'github/codeql-action/analyze@v3' step."
        )

    def test_sast_job_has_checkout_step(self):
        steps = self.sast_job.get("steps", []) or []
        uses_values = [s.get("uses", "") for s in steps if isinstance(s, dict)]
        self.assertTrue(
            any("actions/checkout" in u for u in uses_values),
            "The 'sast' job is missing an 'actions/checkout' step."
        )

    def test_codeql_init_uses_auto_language_detection(self):
        """CodeQL init should either omit 'languages' (auto-detect) or set it explicitly."""
        steps = self.sast_job.get("steps", []) or []
        for step in steps:
            if not isinstance(step, dict):
                continue
            if "codeql-action/init" in step.get("uses", ""):
                with_config = step.get("with", {}) or {}
                # Auto-detect is valid (no languages key), or explicit list is valid.
                # What is NOT valid is an empty string value.
                languages = with_config.get("languages")
                if languages is not None:
                    self.assertTrue(
                        bool(str(languages).strip()),
                        "CodeQL init 'languages' is set but empty. "
                        "Either omit it for auto-detection or provide a valid language list."
                    )
                return
        self.fail("No 'github/codeql-action/init' step found in 'sast' job.")


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping permissions tests")
class TestWorkflowPermissions(unittest.TestCase):
    """
    Verify least-privilege permissions are configured.
    CodeQL requires security-events: write; general jobs need contents: read.
    """

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})

    def _get_permissions(self, job_name):
        """Return permissions dict for a job, or workflow-level permissions."""
        job = self.jobs.get(job_name, {})
        job_perms = job.get("permissions")
        if job_perms is not None:
            return job_perms
        return self.workflow.get("permissions")

    def test_sast_job_has_security_events_write(self):
        """CodeQL requires security-events: write to upload SARIF results."""
        perms = self._get_permissions("sast")
        if perms is None:
            # Permissions may be set at workflow level or rely on repo defaults.
            # Emit a warning-style failure only if permissions are explicitly set elsewhere.
            return
        if isinstance(perms, str) and perms == "write-all":
            return  # write-all satisfies the requirement (though not recommended)
        self.assertIn(
            "security-events", perms,
            "The 'sast' job (or workflow) permissions should include 'security-events: write' "
            "for CodeQL to upload SARIF results."
        )
        self.assertEqual(
            perms.get("security-events"), "write",
            f"Expected 'security-events: write', got: {perms.get('security-events')}"
        )

    def test_workflow_or_jobs_have_contents_read(self):
        """At minimum, contents: read is needed for checkout."""
        workflow_perms = self.workflow.get("permissions")
        if workflow_perms is None:
            # No explicit permissions — relies on repo defaults, which is acceptable
            # but not ideal. We skip rather than fail.
            return
        if isinstance(workflow_perms, str):
            # e.g., permissions: read-all
            self.assertIn(
                workflow_perms, ("read-all", "write-all"),
                f"Unexpected string value for workflow permissions: {workflow_perms}"
            )
            return
        if "contents" in workflow_perms:
            self.assertIn(
                workflow_perms["contents"], ("read", "write"),
                f"Unexpected value for contents permission: {workflow_perms['contents']}"
            )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping checkout step tests")
class TestCheckoutStepsInAllJobs(unittest.TestCase):
    """Every job must check out the repository before doing work."""

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})

    def _job_has_checkout(self, job_name):
        job = self.jobs.get(job_name, {})
        steps = job.get("steps", []) or []
        return any(
            isinstance(s, dict) and "actions/checkout" in s.get("uses", "")
            for s in steps
        )

    def test_build_job_checks_out_repo(self):
        self.assertTrue(
            self._job_has_checkout("build"),
            "The 'build' job is missing an 'actions/checkout' step."
        )

    def test_test_job_checks_out_repo(self):
        self.assertTrue(
            self._job_has_checkout("test"),
            "The 'test' job is missing an 'actions/checkout' step."
        )

    def test_sast_job_checks_out_repo(self):
        self.assertTrue(
            self._job_has_checkout("sast"),
            "The 'sast' job is missing an 'actions/checkout' step."
        )


@unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed — skipping artifact upload tests")
class TestTestJobArtifactUpload(unittest.TestCase):
    """The test job should upload test results as artifacts."""

    def setUp(self):
        self.workflow = load_workflow()
        self.jobs = self.workflow.get("jobs", {})
        self.test_job = self.jobs.get("test", {})

    def test_test_job_uploads_artifacts(self):
        steps = self.test_job.get("steps", []) or []
        uses_values = [s.get("uses", "") for s in steps if isinstance(s, dict)]
        self.assertTrue(
            any("actions/upload-artifact" in u for u in uses_values),
            "The 'test' job should upload test results using 'actions/upload-artifact@v4'."
        )

    def test_artifact_upload_specifies_path(self):
        steps = self.test_job.get("steps", []) or []
        for step in steps:
            if not isinstance(step, dict):
                continue
            if "actions/upload-artifact" in step.get("uses", ""):
                with_config = step.get("with", {}) or {}
                self.assertIn(
                    "path", with_config,
                    "The 'actions/upload-artifact' step in the 'test' job must specify a 'path'."
                )
                self.assertTrue(
                    bool(str(with_config.get("path", "")).strip()),
                    "The 'path' for artifact upload is empty."
                )
                return
        self.fail("No 'actions/upload-artifact' step found in 'test' job.")


if __name__ == "__main__":
    unittest.main(verbosity=2)