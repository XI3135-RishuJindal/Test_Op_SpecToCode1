#!/usr/bin/env python3
"""
Upgrade validation tests for GitHub Actions CI pipeline introduction.

These tests verify that the CI pipeline upgrade succeeded by inspecting
the actual workflow configuration files and directory structure that
should have been created as part of the upgrade.

Run with: python -m pytest tests/test_ci_pipeline_upgrade.py -v
(or: python tests/test_ci_pipeline_upgrade.py if pytest is unavailable)
"""

import os
import sys
import unittest
import glob

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS_DIR = os.path.join(REPO_ROOT, ".github", "workflows")
CI_WORKFLOW_CANDIDATES = [
    os.path.join(WORKFLOWS_DIR, "ci.yml"),
    os.path.join(WORKFLOWS_DIR, "ci.yaml"),
]


def _find_ci_workflow():
    """Return the path to the primary CI workflow file, or None."""
    for path in CI_WORKFLOW_CANDIDATES:
        if os.path.isfile(path):
            return path
    # Fall back: any yml/yaml in workflows dir
    matches = glob.glob(os.path.join(WORKFLOWS_DIR, "*.yml")) + \
              glob.glob(os.path.join(WORKFLOWS_DIR, "*.yaml"))
    return matches[0] if matches else None


def _load_workflow(path):
    """Load and parse a YAML workflow file. Returns dict or None."""
    if not YAML_AVAILABLE:
        return None
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _collect_all_job_steps(workflow_dict):
    """Return a flat list of all step dicts across all jobs."""
    steps = []
    jobs = workflow_dict.get("jobs", {}) or {}
    for job_name, job_def in jobs.items():
        if isinstance(job_def, dict):
            for step in (job_def.get("steps") or []):
                steps.append((job_name, step))
    return steps


def _uses_action(step, action_prefix):
    """Return True if a step's 'uses' field starts with action_prefix."""
    uses = (step or {}).get("uses", "") or ""
    return uses.startswith(action_prefix)


def _step_run_contains(step, keyword):
    """Return True if a step's 'run' field contains keyword (case-insensitive)."""
    run = (step or {}).get("run", "") or ""
    return keyword.lower() in run.lower()


def _step_name_contains(step, keyword):
    """Return True if a step's 'name' field contains keyword (case-insensitive)."""
    name = (step or {}).get("name", "") or ""
    return keyword.lower() in name.lower()


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

class TestWorkflowDirectoryStructure(unittest.TestCase):
    """Verify the .github/workflows/ directory and CI file exist."""

    def test_github_directory_exists(self):
        """The .github directory must exist at the repository root."""
        github_dir = os.path.join(REPO_ROOT, ".github")
        self.assertTrue(
            os.path.isdir(github_dir),
            f".github directory not found at {github_dir}. "
            "The CI pipeline upgrade requires this directory to be created."
        )

    def test_workflows_directory_exists(self):
        """The .github/workflows/ directory must exist."""
        self.assertTrue(
            os.path.isdir(WORKFLOWS_DIR),
            f".github/workflows/ directory not found at {WORKFLOWS_DIR}. "
            "The CI pipeline upgrade requires this directory to be created."
        )

    def test_ci_workflow_file_exists(self):
        """A CI workflow file (ci.yml or ci.yaml) must exist."""
        ci_path = _find_ci_workflow()
        self.assertIsNotNone(
            ci_path,
            f"No CI workflow file found in {WORKFLOWS_DIR}. "
            "Expected ci.yml or ci.yaml to be created by the upgrade."
        )
        self.assertTrue(
            os.path.isfile(ci_path),
            f"CI workflow path {ci_path} is not a regular file."
        )

    def test_ci_workflow_file_is_not_empty(self):
        """The CI workflow file must not be empty."""
        ci_path = _find_ci_workflow()
        self.assertIsNotNone(ci_path, "CI workflow file not found.")
        size = os.path.getsize(ci_path)
        self.assertGreater(
            size, 0,
            f"CI workflow file {ci_path} is empty."
        )

    def test_no_legacy_ci_configs_without_migration(self):
        """
        Legacy CI config files should not coexist with the new pipeline
        unless they have been explicitly migrated/removed.
        This is a warning-level check — it flags the presence of old configs.
        """
        legacy_files = [
            ".travis.yml",
            "Jenkinsfile",
            "circle.yml",
            ".circleci/config.yml",
            ".gitlab-ci.yml",
        ]
        found_legacy = [
            f for f in legacy_files
            if os.path.isfile(os.path.join(REPO_ROOT, f))
        ]
        # Not a hard failure — emit as informational via subTest
        for legacy in found_legacy:
            with self.subTest(legacy_file=legacy):
                # Warn but do not fail; migration may be intentional
                print(
                    f"\n  WARNING: Legacy CI config '{legacy}' still present. "
                    "Verify it has been migrated or intentionally retained."
                )


class TestWorkflowYAMLValidity(unittest.TestCase):
    """Verify the CI workflow YAML is syntactically valid."""

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest(
                "PyYAML not installed. Install with: pip install pyyaml"
            )
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found; skipping YAML tests.")
        self.workflow = _load_workflow(self.ci_path)

    def test_workflow_parses_as_valid_yaml(self):
        """The workflow file must parse as valid YAML without errors."""
        self.assertIsNotNone(
            self.workflow,
            f"Workflow file {self.ci_path} parsed to None — check for empty or invalid YAML."
        )
        self.assertIsInstance(
            self.workflow, dict,
            f"Workflow file {self.ci_path} did not parse to a YAML mapping."
        )

    def test_workflow_has_on_triggers(self):
        """The workflow must define 'on:' triggers."""
        on_key = self.workflow.get("on") or self.workflow.get(True)
        self.assertIsNotNone(
            on_key,
            "Workflow is missing the 'on:' trigger block. "
            "The upgrade requires triggers for push and pull_request events."
        )

    def test_workflow_has_jobs(self):
        """The workflow must define at least one job."""
        jobs = self.workflow.get("jobs")
        self.assertIsNotNone(jobs, "Workflow is missing the 'jobs:' block.")
        self.assertIsInstance(jobs, dict, "'jobs:' must be a mapping.")
        self.assertGreater(
            len(jobs), 0,
            "Workflow 'jobs:' block is empty — no jobs defined."
        )


class TestWorkflowTriggers(unittest.TestCase):
    """Verify the workflow triggers match the upgrade specification."""

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        # 'on' key may be parsed as boolean True by some YAML parsers
        self.on_block = self.workflow.get("on") or self.workflow.get(True) or {}

    def test_push_trigger_is_configured(self):
        """The workflow must trigger on 'push' events."""
        self.assertIn(
            "push", self.on_block,
            "Workflow is missing a 'push' trigger. "
            "The upgrade spec requires triggering on push to the default branch."
        )

    def test_pull_request_trigger_is_configured(self):
        """The workflow must trigger on 'pull_request' events."""
        self.assertIn(
            "pull_request", self.on_block,
            "Workflow is missing a 'pull_request' trigger. "
            "The upgrade spec requires triggering on pull requests targeting the default branch."
        )

    def test_push_trigger_targets_default_branch(self):
        """The push trigger should specify a branch (main or master)."""
        push_config = self.on_block.get("push")
        if not isinstance(push_config, dict):
            self.skipTest("Push trigger has no branch configuration to inspect.")
        branches = push_config.get("branches") or []
        self.assertTrue(
            len(branches) > 0,
            "Push trigger does not specify any branches. "
            "Expected 'main' or 'master' to be listed."
        )
        default_branch_found = any(
            b in ("main", "master") for b in branches
        )
        self.assertTrue(
            default_branch_found,
            f"Push trigger branches {branches} do not include 'main' or 'master'. "
            "The upgrade spec requires triggering on the default branch."
        )

    def test_pull_request_trigger_targets_default_branch(self):
        """The pull_request trigger should specify a branch (main or master)."""
        pr_config = self.on_block.get("pull_request")
        if not isinstance(pr_config, dict):
            self.skipTest("pull_request trigger has no branch configuration to inspect.")
        branches = pr_config.get("branches") or []
        if not branches:
            self.skipTest("pull_request trigger has no explicit branch filter (targets all branches).")
        default_branch_found = any(
            b in ("main", "master") for b in branches
        )
        self.assertTrue(
            default_branch_found,
            f"pull_request trigger branches {branches} do not include 'main' or 'master'."
        )


class TestRequiredJobsExist(unittest.TestCase):
    """Verify all four required pipeline stages are defined as jobs."""

    REQUIRED_JOBS = ["lint", "sast", "dependency-scan", "test"]
    # Also accept common alternative names
    JOB_ALIASES = {
        "dependency-scan": ["dependency-scan", "dependency_scan", "dep-scan",
                            "deps-scan", "dependabot", "snyk", "trivy"],
        "sast": ["sast", "codeql", "static-analysis", "static_analysis",
                 "security", "semgrep"],
        "lint": ["lint", "linting", "style", "format", "check"],
        "test": ["test", "tests", "unit-test", "unit_test", "pytest",
                 "jest", "go-test"],
    }

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.jobs = self.workflow.get("jobs") or {}
        self.job_names_lower = [j.lower() for j in self.jobs.keys()]

    def _job_present(self, canonical_name):
        """Return True if any defined job matches the canonical name or its aliases."""
        aliases = self.JOB_ALIASES.get(canonical_name, [canonical_name])
        return any(
            any(alias in job_name for alias in aliases)
            for job_name in self.job_names_lower
        )

    def test_lint_job_exists(self):
        """A lint job must be defined in the workflow."""
        self.assertTrue(
            self._job_present("lint"),
            f"No lint job found in workflow jobs: {list(self.jobs.keys())}. "
            "The upgrade spec requires a 'lint' stage."
        )

    def test_sast_job_exists(self):
        """A SAST job must be defined in the workflow."""
        self.assertTrue(
            self._job_present("sast"),
            f"No SAST job found in workflow jobs: {list(self.jobs.keys())}. "
            "The upgrade spec requires a 'sast' stage (e.g., CodeQL or Semgrep)."
        )

    def test_dependency_scan_job_exists(self):
        """A dependency scan job must be defined in the workflow."""
        self.assertTrue(
            self._job_present("dependency-scan"),
            f"No dependency scan job found in workflow jobs: {list(self.jobs.keys())}. "
            "The upgrade spec requires a 'dependency-scan' stage."
        )

    def test_test_job_exists(self):
        """A test job must be defined in the workflow."""
        self.assertTrue(
            self._job_present("test"),
            f"No test job found in workflow jobs: {list(self.jobs.keys())}. "
            "The upgrade spec requires a 'test' stage."
        )

    def test_all_four_required_stages_present(self):
        """All four required stages must be present in a single assertion."""
        missing = [
            stage for stage in self.REQUIRED_JOBS
            if not self._job_present(stage)
        ]
        self.assertEqual(
            missing, [],
            f"The following required pipeline stages are missing: {missing}. "
            f"Defined jobs: {list(self.jobs.keys())}"
        )


class TestJobRunnerConfiguration(unittest.TestCase):
    """Verify each job specifies a runs-on runner."""

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.jobs = self.workflow.get("jobs") or {}

    def test_all_jobs_have_runs_on(self):
        """Every job must specify a 'runs-on' runner."""
        jobs_missing_runner = [
            job_name for job_name, job_def in self.jobs.items()
            if not (isinstance(job_def, dict) and job_def.get("runs-on"))
        ]
        self.assertEqual(
            jobs_missing_runner, [],
            f"The following jobs are missing 'runs-on': {jobs_missing_runner}. "
            "Every job must specify a GitHub-hosted or self-hosted runner."
        )

    def test_all_jobs_use_ubuntu_or_valid_runner(self):
        """Jobs should use a recognized runner (ubuntu, windows, macos, or self-hosted)."""
        valid_prefixes = ("ubuntu-", "windows-", "macos-", "self-hosted")
        invalid_jobs = []
        for job_name, job_def in self.jobs.items():
            if not isinstance(job_def, dict):
                continue
            runs_on = job_def.get("runs-on", "")
            if isinstance(runs_on, list):
                # Matrix or self-hosted array — skip detailed check
                continue
            if not any(str(runs_on).startswith(p) for p in valid_prefixes):
                invalid_jobs.append((job_name, runs_on))
        self.assertEqual(
            invalid_jobs, [],
            f"Jobs with unrecognized runner values: {invalid_jobs}. "
            "Expected runners like 'ubuntu-latest', 'windows-latest', etc."
        )


class TestCheckoutStepPresent(unittest.TestCase):
    """Verify each job checks out the repository code."""

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.jobs = self.workflow.get("jobs") or {}

    def test_all_jobs_have_checkout_step(self):
        """Every job must include an actions/checkout step."""
        jobs_without_checkout = []
        for job_name, job_def in self.jobs.items():
            if not isinstance(job_def, dict):
                continue
            steps = job_def.get("steps") or []
            has_checkout = any(
                _uses_action(step, "actions/checkout")
                for step in steps
            )
            if not has_checkout:
                jobs_without_checkout.append(job_name)
        self.assertEqual(
            jobs_without_checkout, [],
            f"The following jobs are missing 'actions/checkout': {jobs_without_checkout}. "
            "Every job must check out the repository before running commands."
        )


class TestSASTJobConfiguration(unittest.TestCase):
    """Verify the SAST job uses CodeQL or an equivalent SAST tool."""

    SAST_ACTIONS = [
        "github/codeql-action/analyze",
        "github/codeql-action/init",
        "returntocorp/semgrep-action",
        "semgrep/semgrep-action",
        "AppThreat/sast-scan",
    ]

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.all_steps = _collect_all_job_steps(self.workflow)

    def test_sast_action_is_used(self):
        """A recognized SAST action must appear in at least one job step."""
        found_sast = any(
            any(_uses_action(step, action) for action in self.SAST_ACTIONS)
            for _, step in self.all_steps
        )
        # Also accept run-based SAST tools (semgrep CLI, bandit, etc.)
        sast_run_keywords = ["codeql", "semgrep", "bandit", "gosec",
                             "spotbugs", "sonar", "snyk code", "trivy fs"]
        found_sast_run = any(
            any(_step_run_contains(step, kw) for kw in sast_run_keywords)
            for _, step in self.all_steps
        )
        self.assertTrue(
            found_sast or found_sast_run,
            "No recognized SAST action or tool invocation found in any job step. "
            "The upgrade spec requires a SAST stage using CodeQL or equivalent. "
            f"Checked actions: {self.SAST_ACTIONS} and run keywords: {sast_run_keywords}"
        )

    def test_codeql_or_sast_not_skipped_by_default(self):
        """SAST steps must not be unconditionally skipped."""
        for job_name, step in self.all_steps:
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "") or ""
            is_sast_step = any(uses.startswith(a) for a in self.SAST_ACTIONS)
            if is_sast_step:
                condition = step.get("if", "")
                self.assertNotIn(
                    "false", str(condition).lower(),
                    f"SAST step in job '{job_name}' appears to be unconditionally "
                    f"skipped via 'if: false'. Step: {step.get('name', uses)}"
                )


class TestDependencyScanJobConfiguration(unittest.TestCase):
    """Verify the dependency scan job uses a recognized scanning tool."""

    DEP_SCAN_ACTIONS = [
        "actions/dependency-review-action",
        "snyk/actions",
        "aquasecurity/trivy-action",
        "ossf/scorecard-action",
        "github/advisory-database",
    ]
    DEP_SCAN_RUN_KEYWORDS = [
        "trivy", "snyk", "npm audit", "pip-audit", "safety",
        "bundler-audit", "govulncheck", "dependency-check",
        "owasp", "audit",
    ]

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.all_steps = _collect_all_job_steps(self.workflow)

    def test_dependency_scan_tool_is_used(self):
        """A recognized dependency scanning action or CLI tool must be present."""
        found_action = any(
            any(_uses_action(step, action) for action in self.DEP_SCAN_ACTIONS)
            for _, step in self.all_steps
        )
        found_run = any(
            any(_step_run_contains(step, kw) for kw in self.DEP_SCAN_RUN_KEYWORDS)
            for _, step in self.all_steps
        )
        self.assertTrue(
            found_action or found_run,
            "No recognized dependency scanning action or CLI tool found. "
            "The upgrade spec requires a dependency scan stage. "
            f"Checked actions: {self.DEP_SCAN_ACTIONS} and "
            f"run keywords: {self.DEP_SCAN_RUN_KEYWORDS}"
        )


class TestLintJobConfiguration(unittest.TestCase):
    """Verify the lint job invokes a linter."""

    LINT_ACTIONS = [
        "github/super-linter",
        "oxsecurity/megalinter",
        "wearerequired/lint-action",
        "reviewdog/action-",
    ]
    LINT_RUN_KEYWORDS = [
        "eslint", "flake8", "pylint", "ruff", "golangci-lint",
        "checkstyle", "rubocop", "ktlint", "swiftlint", "shellcheck",
        "hadolint", "markdownlint", "prettier", "black --check",
        "tflint", "yamllint", "lint",
    ]

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.all_steps = _collect_all_job_steps(self.workflow)

    def test_linter_is_invoked(self):
        """A recognized linter action or CLI invocation must be present."""
        found_action = any(
            any(_uses_action(step, action) for action in self.LINT_ACTIONS)
            for _, step in self.all_steps
        )
        found_run = any(
            any(_step_run_contains(step, kw) for kw in self.LINT_RUN_KEYWORDS)
            for _, step in self.all_steps
        )
        found_name = any(
            any(_step_name_contains(step, kw) for kw in ["lint", "style", "format"])
            for _, step in self.all_steps
        )
        self.assertTrue(
            found_action or found_run or found_name,
            "No recognized linter action or CLI invocation found. "
            "The upgrade spec requires a lint stage. "
            f"Checked actions: {self.LINT_ACTIONS} and "
            f"run keywords: {self.LINT_RUN_KEYWORDS}"
        )


class TestTestJobConfiguration(unittest.TestCase):
    """Verify the test job runs the automated test suite."""

    TEST_RUN_KEYWORDS = [
        "pytest", "jest", "npm test", "yarn test", "go test",
        "mvn test", "gradle test", "rspec", "cargo test",
        "dotnet test", "phpunit", "mocha", "vitest",
        "python -m pytest", "python -m unittest",
    ]

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.all_steps = _collect_all_job_steps(self.workflow)

    def test_test_runner_is_invoked(self):
        """A recognized test runner must be invoked in the test job."""
        found_run = any(
            any(_step_run_contains(step, kw) for kw in self.TEST_RUN_KEYWORDS)
            for _, step in self.all_steps
        )
        found_name = any(
            any(_step_name_contains(step, kw) for kw in ["test", "spec", "coverage"])
            for _, step in self.all_steps
        )
        self.assertTrue(
            found_run or found_name,
            "No recognized test runner invocation found. "
            "The upgrade spec requires a test stage that runs the automated test suite. "
            f"Checked run keywords: {self.TEST_RUN_KEYWORDS}"
        )


class TestActionVersionPinning(unittest.TestCase):
    """
    Verify that actions are pinned to a specific version (not floating 'latest').
    This is a security best practice required by the upgrade spec.
    """

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")
        self.all_steps = _collect_all_job_steps(self.workflow)

    def test_no_actions_use_latest_tag(self):
        """Actions must not use the floating '@latest' tag."""
        unpinned = []
        for job_name, step in self.all_steps:
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "") or ""
            if uses.endswith("@latest"):
                unpinned.append((job_name, uses))
        self.assertEqual(
            unpinned, [],
            f"The following actions use the floating '@latest' tag: {unpinned}. "
            "Pin actions to a specific version tag or SHA for reproducibility and security."
        )

    def test_actions_have_version_specifier(self):
        """All 'uses' references must include a version specifier (@vX.Y.Z or @SHA)."""
        unversioned = []
        for job_name, step in self.all_steps:
            if not isinstance(step, dict):
                continue
            uses = step.get("uses", "") or ""
            if uses and "@" not in uses:
                unversioned.append((job_name, uses))
        self.assertEqual(
            unversioned, [],
            f"The following actions lack a version specifier (@): {unversioned}. "
            "All actions must be pinned to a version tag or commit SHA."
        )


class TestWorkflowPermissions(unittest.TestCase):
    """
    Verify that the workflow follows least-privilege permissions.
    The upgrade spec requires minimal permissions for security.
    """

    def setUp(self):
        if not YAML_AVAILABLE:
            self.skipTest("PyYAML not installed.")
        self.ci_path = _find_ci_workflow()
        if self.ci_path is None:
            self.skipTest("CI workflow file not found.")
        self.workflow = _load_workflow(self.ci_path)
        if not self.workflow:
            self.skipTest("Workflow file could not be parsed.")

    def test_workflow_does_not_grant_write_all(self):
        """
        The workflow must not grant 'write-all' permissions at the top level,
        which would give every job excessive access.
        """
        permissions = self.workflow.get("permissions")
        if permissions is None:
            return  # No top-level permissions block — acceptable
        self.assertNotEqual(
            str(permissions).lower(), "write-all",
            "Workflow grants 'write-all' permissions at the top level. "
            "Use least-privilege permissions per job instead."
        )


class TestCIPipelineUpgradeVersion(unittest.TestCase):
    """
    Meta-test: verify the CI pipeline upgrade itself is at the target state.
    This acts as the 'version assertion' for the infrastructure upgrade.
    """

    TARGET_PIPELINE_FEATURES = {
        "workflow_directory": ".github/workflows/",
        "ci_workflow_file": "ci.yml or ci.yaml",
        "required_stages": ["lint", "sast", "dependency-scan", "test"],
        "required_triggers": ["push", "pull_request"],
    }

    def test_pipeline_upgrade_target_state_achieved(self):
        """
        Comprehensive assertion that the CI pipeline upgrade has reached
        its target state: all four stages present, correct triggers, valid YAML.
        """
        failures = []

        # 1. Workflows directory exists
        if not os.path.isdir(WORKFLOWS_DIR):
            failures.append(
                f"MISSING: .github/workflows/ directory at {WORKFLOWS_DIR}"
            )

        # 2. CI workflow file exists
        ci_path = _find_ci_workflow()
        if ci_path is None:
            failures.append(
                "MISSING: ci.yml or ci.yaml in .github/workflows/"
            )

        # 3. YAML validity and content checks (only if file exists and yaml available)
        if ci_path and YAML_AVAILABLE:
            workflow = _load_workflow(ci_path)
            if workflow is None:
                failures.append(f"INVALID: {ci_path} could not be parsed as YAML")
            else:
                # Check triggers
                on_block = workflow.get("on") or workflow.get(True) or {}
                for trigger in ["push", "pull_request"]:
                    if trigger not in on_block:
                        failures.append(
                            f"MISSING TRIGGER: '{trigger}' not in workflow 'on:' block"
                        )

                # Check jobs
                jobs = workflow.get("jobs") or {}
                job_names_lower = [j.lower() for j in jobs.keys()]
                required_stage_aliases = {
                    "lint": ["lint", "linting", "style"],
                    "sast": ["sast", "codeql", "semgrep", "security", "static"],
                    "dependency-scan": ["dependency", "dep-scan", "deps", "trivy",
                                        "snyk", "audit"],
                    "test": ["test", "tests", "pytest", "jest", "spec"],
                }
                for stage, aliases in required_stage_aliases.items():
                    found = any(
                        any(alias in job_name for alias in aliases)
                        for job_name in job_names_lower
                    )
                    if not found:
                        failures.append(
                            f"MISSING STAGE: No job matching '{stage}' "
                            f"(aliases: {aliases}) found in jobs: {list(jobs.keys())}"
                        )

        self.assertEqual(
            failures, [],
            "CI pipeline upgrade validation FAILED. Issues found:\n  - " +
            "\n  - ".join(failures) +
            "\n\nTarget state requires: " +
            str(self.TARGET_PIPELINE_FEATURES)
        )

    def test_pipeline_upgrade_replaces_no_ci_state(self):
        """
        Verify the upgrade moved from 'no CI' to 'CI present' state.
        The pre-upgrade state was: no .github/workflows/ directory.
        The post-upgrade state must be: .github/workflows/ exists with content.
        """
        self.assertTrue(
            os.path.isdir(WORKFLOWS_DIR),
            "Post-upgrade state validation FAILED: "
            ".github/workflows/ directory does not exist. "
            "The upgrade should have created this directory and added workflow files."
        )
        workflow_files = (
            glob.glob(os.path.join(WORKFLOWS_DIR, "*.yml")) +
            glob.glob(os.path.join(WORKFLOWS_DIR, "*.yaml"))
        )
        self.assertGreater(
            len(workflow_files), 0,
            "Post-upgrade state validation FAILED: "
            ".github/workflows/ directory exists but contains no workflow files. "
            "The upgrade should have created at least one workflow file."
        )


# ---------------------------------------------------------------------------
# Entry point for running without pytest
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Provide a helpful message if PyYAML is missing
    if not YAML_AVAILABLE:
        print(
            "WARNING: PyYAML is not installed. YAML-parsing tests will be skipped.\n"
            "Install it with: pip install pyyaml\n",
            file=sys.stderr
        )

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    test_classes = [
        TestWorkflowDirectoryStructure,
        TestWorkflowYAMLValidity,
        TestWorkflowTriggers,
        TestRequiredJobsExist,
        TestJobRunnerConfiguration,
        TestCheckoutStepPresent,
        TestSASTJobConfiguration,
        TestDependencyScanJobConfiguration,
        TestLintJobConfiguration,
        TestTestJobConfiguration,
        TestActionVersionPinning,
        TestWorkflowPermissions,
        TestCIPipelineUpgradeVersion,
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)