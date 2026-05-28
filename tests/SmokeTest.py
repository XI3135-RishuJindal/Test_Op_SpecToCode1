#!/usr/bin/env python3
"""
Upgrade validation tests for GitHub Actions CI/CD pipeline introduction.

These tests verify that the CI/CD pipeline upgrade succeeded by checking:
- Required workflow files exist at the correct paths
- Workflow files contain the required stages (lint, SAST, test)
- Workflow triggers are correctly configured
- Required actions versions meet the target specification
- SAST tooling is configured
- Branch protection-compatible status check names are present
"""

import os
import unittest
import glob

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS_DIR = os.path.join(REPO_ROOT, ".github", "workflows")

REQUIRED_CHECKOUT_ACTION = "actions/checkout"
REQUIRED_CHECKOUT_VERSION = "v4"
REQUIRED_CHECKOUT_FULL = f"{REQUIRED_CHECKOUT_ACTION}@{REQUIRED_CHECKOUT_VERSION}"

EXPECTED_WORKFLOW_FILES = {
    "lint": None,       # resolved dynamically
    "sast": None,
    "test": None,
}

EXPECTED_TRIGGERS = {"push", "pull_request"}

KNOWN_SAST_ACTIONS = [
    "github/codeql-action",
    "returntocorp/semgrep-action",
    "snyk/actions",
    "aquasecurity/trivy-action",
    "anchore/scan-action",
]


def _load_workflow_files():
    """Return a dict of {stem: (path, parsed_yaml_or_None)} for all workflow YAML files."""
    result = {}
    if not os.path.isdir(WORKFLOWS_DIR):
        return result
    for path in glob.glob(os.path.join(WORKFLOWS_DIR, "*.yml")) + glob.glob(
        os.path.join(WORKFLOWS_DIR, "*.yaml")
    ):
        stem = os.path.splitext(os.path.basename(path))[0].lower()
        parsed = None
        if YAML_AVAILABLE:
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    parsed = yaml.safe_load(fh)
            except Exception:
                parsed = None
        result[stem] = (path, parsed)
    return result


def _find_workflow_for_stage(workflows, stage_keyword):
    """
    Return (stem, path, parsed) for the first workflow whose filename or
    top-level 'name' field contains the stage_keyword (case-insensitive).
    Returns None if not found.
    """
    for stem, (path, parsed) in workflows.items():
        if stage_keyword in stem:
            return stem, path, parsed
        if parsed and isinstance(parsed, dict):
            wf_name = str(parsed.get("name", "")).lower()
            if stage_keyword in wf_name:
                return stem, path, parsed
    return None


def _collect_all_uses(parsed):
    """Recursively collect all 'uses:' values from a parsed workflow dict."""
    uses_list = []
    if isinstance(parsed, dict):
        for key, value in parsed.items():
            if key == "uses" and isinstance(value, str):
                uses_list.append(value)
            else:
                uses_list.extend(_collect_all_uses(value))
    elif isinstance(parsed, list):
        for item in parsed:
            uses_list.extend(_collect_all_uses(item))
    return uses_list


def _collect_all_run_commands(parsed):
    """Recursively collect all 'run:' values from a parsed workflow dict."""
    run_list = []
    if isinstance(parsed, dict):
        for key, value in parsed.items():
            if key == "run" and isinstance(value, str):
                run_list.append(value)
            else:
                run_list.extend(_collect_all_run_commands(value))
    elif isinstance(parsed, list):
        for item in parsed:
            run_list.extend(_collect_all_run_commands(item))
    return run_list


def _get_triggers(parsed):
    """Return the set of event trigger keys from a parsed workflow."""
    if not parsed or not isinstance(parsed, dict):
        return set()
    on_value = parsed.get("on", parsed.get(True, {}))
    if isinstance(on_value, dict):
        return set(on_value.keys())
    if isinstance(on_value, list):
        return set(on_value)
    if isinstance(on_value, str):
        return {on_value}
    return set()


class TestWorkflowsDirectoryExists(unittest.TestCase):
    """Verify the .github/workflows/ directory was created as part of the upgrade."""

    def test_github_directory_exists(self):
        github_dir = os.path.join(REPO_ROOT, ".github")
        self.assertTrue(
            os.path.isdir(github_dir),
            f"Expected .github/ directory to exist at {github_dir}. "
            "The CI/CD upgrade requires this directory to be created.",
        )

    def test_workflows_directory_exists(self):
        self.assertTrue(
            os.path.isdir(WORKFLOWS_DIR),
            f"Expected .github/workflows/ directory to exist at {WORKFLOWS_DIR}. "
            "The CI/CD upgrade requires at least one workflow file here.",
        )

    def test_at_least_one_workflow_file_present(self):
        yml_files = glob.glob(os.path.join(WORKFLOWS_DIR, "*.yml")) + glob.glob(
            os.path.join(WORKFLOWS_DIR, "*.yaml")
        )
        self.assertGreater(
            len(yml_files),
            0,
            f"No .yml/.yaml workflow files found in {WORKFLOWS_DIR}. "
            "The upgrade must introduce at least one workflow file.",
        )


class TestLintWorkflowExists(unittest.TestCase):
    """Verify the lint stage workflow was introduced by the upgrade."""

    def setUp(self):
        self.workflows = _load_workflow_files()
        self.lint_entry = _find_workflow_for_stage(self.workflows, "lint")

    def test_lint_workflow_file_exists(self):
        self.assertIsNotNone(
            self.lint_entry,
            "No workflow file containing 'lint' in its filename or 'name' field was found. "
            f"Expected a lint workflow in {WORKFLOWS_DIR} (e.g., lint.yml).",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_lint_workflow_is_valid_yaml(self):
        if self.lint_entry is None:
            self.skipTest("Lint workflow not found; skipping YAML validity check.")
        _, path, parsed = self.lint_entry
        self.assertIsNotNone(
            parsed,
            f"Lint workflow at {path} could not be parsed as valid YAML.",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_lint_workflow_has_push_trigger(self):
        if self.lint_entry is None:
            self.skipTest("Lint workflow not found.")
        _, path, parsed = self.lint_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        triggers = _get_triggers(parsed)
        self.assertIn(
            "push",
            triggers,
            f"Lint workflow at {path} must trigger on 'push' events. Found triggers: {triggers}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_lint_workflow_has_pull_request_trigger(self):
        if self.lint_entry is None:
            self.skipTest("Lint workflow not found.")
        _, path, parsed = self.lint_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        triggers = _get_triggers(parsed)
        self.assertIn(
            "pull_request",
            triggers,
            f"Lint workflow at {path} must trigger on 'pull_request' events. Found triggers: {triggers}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_lint_workflow_uses_checkout_v4(self):
        if self.lint_entry is None:
            self.skipTest("Lint workflow not found.")
        _, path, parsed = self.lint_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        uses_list = _collect_all_uses(parsed)
        checkout_uses = [u for u in uses_list if REQUIRED_CHECKOUT_ACTION in u]
        self.assertTrue(
            len(checkout_uses) > 0,
            f"Lint workflow at {path} must use '{REQUIRED_CHECKOUT_ACTION}'. "
            f"Found 'uses' entries: {uses_list}",
        )
        self.assertTrue(
            any(REQUIRED_CHECKOUT_FULL in u for u in checkout_uses),
            f"Lint workflow at {path} must use '{REQUIRED_CHECKOUT_FULL}' (v4 is the target version). "
            f"Found checkout uses: {checkout_uses}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_lint_workflow_has_jobs(self):
        if self.lint_entry is None:
            self.skipTest("Lint workflow not found.")
        _, path, parsed = self.lint_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        jobs = parsed.get("jobs", {})
        self.assertGreater(
            len(jobs),
            0,
            f"Lint workflow at {path} must define at least one job under 'jobs:'.",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_lint_workflow_has_lint_run_step_or_action(self):
        if self.lint_entry is None:
            self.skipTest("Lint workflow not found.")
        _, path, parsed = self.lint_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        run_commands = _collect_all_run_commands(parsed)
        uses_list = _collect_all_uses(parsed)
        lint_keywords = ["lint", "eslint", "flake8", "pylint", "rubocop", "golangci", "checkstyle", "prettier", "ruff", "black"]
        has_lint_run = any(
            any(kw in cmd.lower() for kw in lint_keywords)
            for cmd in run_commands
        )
        has_lint_action = any(
            any(kw in u.lower() for kw in lint_keywords)
            for u in uses_list
        )
        self.assertTrue(
            has_lint_run or has_lint_action,
            f"Lint workflow at {path} must contain a step that invokes a linter "
            f"(via 'run:' or 'uses:'). Found run commands: {run_commands}, uses: {uses_list}",
        )


class TestSASTWorkflowExists(unittest.TestCase):
    """Verify the SAST stage workflow was introduced by the upgrade."""

    def setUp(self):
        self.workflows = _load_workflow_files()
        self.sast_entry = _find_workflow_for_stage(self.workflows, "sast") or \
                          _find_workflow_for_stage(self.workflows, "codeql") or \
                          _find_workflow_for_stage(self.workflows, "security") or \
                          _find_workflow_for_stage(self.workflows, "semgrep")

    def test_sast_workflow_file_exists(self):
        self.assertIsNotNone(
            self.sast_entry,
            "No workflow file containing 'sast', 'codeql', 'security', or 'semgrep' "
            "in its filename or 'name' field was found. "
            f"Expected a SAST workflow in {WORKFLOWS_DIR} (e.g., sast.yml or codeql.yml).",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_sast_workflow_is_valid_yaml(self):
        if self.sast_entry is None:
            self.skipTest("SAST workflow not found.")
        _, path, parsed = self.sast_entry
        self.assertIsNotNone(
            parsed,
            f"SAST workflow at {path} could not be parsed as valid YAML.",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_sast_workflow_has_push_or_pr_trigger(self):
        if self.sast_entry is None:
            self.skipTest("SAST workflow not found.")
        _, path, parsed = self.sast_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        triggers = _get_triggers(parsed)
        self.assertTrue(
            triggers & EXPECTED_TRIGGERS,
            f"SAST workflow at {path} must trigger on 'push' or 'pull_request'. "
            f"Found triggers: {triggers}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_sast_workflow_uses_known_sast_action(self):
        if self.sast_entry is None:
            self.skipTest("SAST workflow not found.")
        _, path, parsed = self.sast_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        uses_list = _collect_all_uses(parsed)
        run_commands = _collect_all_run_commands(parsed)
        sast_keywords = ["codeql", "semgrep", "snyk", "trivy", "anchore", "bandit", "gosec", "brakeman", "sonar"]
        has_sast_action = any(
            any(kw in u.lower() for kw in sast_keywords)
            for u in uses_list
        )
        has_sast_run = any(
            any(kw in cmd.lower() for kw in sast_keywords)
            for cmd in run_commands
        )
        self.assertTrue(
            has_sast_action or has_sast_run,
            f"SAST workflow at {path} must invoke a recognized SAST tool "
            f"(CodeQL, Semgrep, Snyk, Trivy, Bandit, etc.). "
            f"Found uses: {uses_list}, run commands: {run_commands}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_sast_workflow_uses_checkout_v4(self):
        if self.sast_entry is None:
            self.skipTest("SAST workflow not found.")
        _, path, parsed = self.sast_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        uses_list = _collect_all_uses(parsed)
        checkout_uses = [u for u in uses_list if REQUIRED_CHECKOUT_ACTION in u]
        self.assertTrue(
            len(checkout_uses) > 0,
            f"SAST workflow at {path} must use '{REQUIRED_CHECKOUT_ACTION}'. "
            f"Found 'uses' entries: {uses_list}",
        )
        self.assertTrue(
            any(REQUIRED_CHECKOUT_FULL in u for u in checkout_uses),
            f"SAST workflow at {path} must use '{REQUIRED_CHECKOUT_FULL}' (v4 is the target version). "
            f"Found checkout uses: {checkout_uses}",
        )


class TestTestWorkflowExists(unittest.TestCase):
    """Verify the test stage workflow was introduced by the upgrade."""

    def setUp(self):
        self.workflows = _load_workflow_files()
        self.test_entry = _find_workflow_for_stage(self.workflows, "test") or \
                          _find_workflow_for_stage(self.workflows, "ci")

    def test_test_workflow_file_exists(self):
        self.assertIsNotNone(
            self.test_entry,
            "No workflow file containing 'test' or 'ci' in its filename or 'name' field was found. "
            f"Expected a test workflow in {WORKFLOWS_DIR} (e.g., test.yml or ci.yml).",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_test_workflow_is_valid_yaml(self):
        if self.test_entry is None:
            self.skipTest("Test workflow not found.")
        _, path, parsed = self.test_entry
        self.assertIsNotNone(
            parsed,
            f"Test workflow at {path} could not be parsed as valid YAML.",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_test_workflow_has_push_trigger(self):
        if self.test_entry is None:
            self.skipTest("Test workflow not found.")
        _, path, parsed = self.test_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        triggers = _get_triggers(parsed)
        self.assertIn(
            "push",
            triggers,
            f"Test workflow at {path} must trigger on 'push' events. Found triggers: {triggers}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_test_workflow_has_pull_request_trigger(self):
        if self.test_entry is None:
            self.skipTest("Test workflow not found.")
        _, path, parsed = self.test_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        triggers = _get_triggers(parsed)
        self.assertIn(
            "pull_request",
            triggers,
            f"Test workflow at {path} must trigger on 'pull_request' events. Found triggers: {triggers}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_test_workflow_uses_checkout_v4(self):
        if self.test_entry is None:
            self.skipTest("Test workflow not found.")
        _, path, parsed = self.test_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        uses_list = _collect_all_uses(parsed)
        checkout_uses = [u for u in uses_list if REQUIRED_CHECKOUT_ACTION in u]
        self.assertTrue(
            len(checkout_uses) > 0,
            f"Test workflow at {path} must use '{REQUIRED_CHECKOUT_ACTION}'. "
            f"Found 'uses' entries: {uses_list}",
        )
        self.assertTrue(
            any(REQUIRED_CHECKOUT_FULL in u for u in checkout_uses),
            f"Test workflow at {path} must use '{REQUIRED_CHECKOUT_FULL}' (v4 is the target version). "
            f"Found checkout uses: {checkout_uses}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_test_workflow_has_test_run_step_or_action(self):
        if self.test_entry is None:
            self.skipTest("Test workflow not found.")
        _, path, parsed = self.test_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        run_commands = _collect_all_run_commands(parsed)
        uses_list = _collect_all_uses(parsed)
        test_keywords = [
            "test", "pytest", "jest", "mocha", "rspec", "go test",
            "mvn test", "gradle test", "npm test", "yarn test",
            "dotnet test", "cargo test", "phpunit",
        ]
        has_test_run = any(
            any(kw in cmd.lower() for kw in test_keywords)
            for cmd in run_commands
        )
        has_test_action = any(
            any(kw in u.lower() for kw in test_keywords)
            for u in uses_list
        )
        self.assertTrue(
            has_test_run or has_test_action,
            f"Test workflow at {path} must contain a step that invokes a test runner "
            f"(via 'run:' or 'uses:'). Found run commands: {run_commands}, uses: {uses_list}",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_test_workflow_has_jobs(self):
        if self.test_entry is None:
            self.skipTest("Test workflow not found.")
        _, path, parsed = self.test_entry
        if parsed is None:
            self.skipTest(f"Could not parse {path}.")
        jobs = parsed.get("jobs", {})
        self.assertGreater(
            len(jobs),
            0,
            f"Test workflow at {path} must define at least one job under 'jobs:'.",
        )


class TestActionsVersions(unittest.TestCase):
    """
    Verify that all workflow files use the target version of actions/checkout (v4)
    and do not reference deprecated v1 or v2 checkout actions.
    """

    def setUp(self):
        self.workflows = _load_workflow_files()

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_no_workflow_uses_checkout_v1(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            uses_list = _collect_all_uses(parsed)
            deprecated = [u for u in uses_list if "actions/checkout@v1" in u]
            self.assertEqual(
                len(deprecated),
                0,
                f"Workflow '{stem}' at {path} uses deprecated 'actions/checkout@v1'. "
                "Upgrade to actions/checkout@v4 as required by this pipeline upgrade.",
            )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_no_workflow_uses_checkout_v2(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            uses_list = _collect_all_uses(parsed)
            deprecated = [u for u in uses_list if "actions/checkout@v2" in u]
            self.assertEqual(
                len(deprecated),
                0,
                f"Workflow '{stem}' at {path} uses deprecated 'actions/checkout@v2'. "
                "Upgrade to actions/checkout@v4 as required by this pipeline upgrade.",
            )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_no_workflow_uses_checkout_v3(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            uses_list = _collect_all_uses(parsed)
            old_version = [u for u in uses_list if "actions/checkout@v3" in u]
            self.assertEqual(
                len(old_version),
                0,
                f"Workflow '{stem}' at {path} uses 'actions/checkout@v3'. "
                "The target version for this upgrade is actions/checkout@v4.",
            )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_all_workflows_use_checkout_v4(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            uses_list = _collect_all_uses(parsed)
            checkout_uses = [u for u in uses_list if REQUIRED_CHECKOUT_ACTION in u]
            if not checkout_uses:
                continue  # workflow may not need checkout (e.g., notification-only)
            self.assertTrue(
                any(REQUIRED_CHECKOUT_FULL in u for u in checkout_uses),
                f"Workflow '{stem}' at {path} uses checkout action but not the required "
                f"'{REQUIRED_CHECKOUT_FULL}'. Found: {checkout_uses}",
            )


class TestThreeStagesCoveredAcrossWorkflows(unittest.TestCase):
    """
    Verify that across all workflow files, all three required stages
    (lint, SAST, test) are represented — either as separate files or
    as jobs within a combined workflow.
    """

    def setUp(self):
        self.workflows = _load_workflow_files()

    def test_workflows_directory_not_empty(self):
        self.assertGreater(
            len(self.workflows),
            0,
            f"No workflow files found in {WORKFLOWS_DIR}. "
            "The upgrade must introduce workflow files for lint, SAST, and test stages.",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_lint_stage_present_across_all_workflows(self):
        lint_keywords = [
            "lint", "eslint", "flake8", "pylint", "rubocop",
            "golangci", "checkstyle", "prettier", "ruff", "black",
        ]
        found_lint = False
        for stem, (path, parsed) in self.workflows.items():
            if "lint" in stem:
                found_lint = True
                break
            if parsed is None:
                continue
            wf_name = str(parsed.get("name", "")).lower()
            if "lint" in wf_name:
                found_lint = True
                break
            jobs = parsed.get("jobs", {})
            for job_name in jobs:
                if any(kw in job_name.lower() for kw in lint_keywords):
                    found_lint = True
                    break
            if found_lint:
                break
            run_commands = _collect_all_run_commands(parsed)
            uses_list = _collect_all_uses(parsed)
            if any(any(kw in cmd.lower() for kw in lint_keywords) for cmd in run_commands):
                found_lint = True
                break
            if any(any(kw in u.lower() for kw in lint_keywords) for u in uses_list):
                found_lint = True
                break
        self.assertTrue(
            found_lint,
            "No lint stage was found across any workflow file. "
            "The upgrade requires a lint stage in the CI/CD pipeline.",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_sast_stage_present_across_all_workflows(self):
        sast_keywords = [
            "sast", "codeql", "semgrep", "snyk", "trivy",
            "anchore", "bandit", "gosec", "brakeman", "sonar", "security",
        ]
        found_sast = False
        for stem, (path, parsed) in self.workflows.items():
            if any(kw in stem for kw in sast_keywords):
                found_sast = True
                break
            if parsed is None:
                continue
            wf_name = str(parsed.get("name", "")).lower()
            if any(kw in wf_name for kw in sast_keywords):
                found_sast = True
                break
            jobs = parsed.get("jobs", {})
            for job_name in jobs:
                if any(kw in job_name.lower() for kw in sast_keywords):
                    found_sast = True
                    break
            if found_sast:
                break
            run_commands = _collect_all_run_commands(parsed)
            uses_list = _collect_all_uses(parsed)
            if any(any(kw in cmd.lower() for kw in sast_keywords) for cmd in run_commands):
                found_sast = True
                break
            if any(any(kw in u.lower() for kw in sast_keywords) for u in uses_list):
                found_sast = True
                break
        self.assertTrue(
            found_sast,
            "No SAST stage was found across any workflow file. "
            "The upgrade requires a SAST stage (e.g., CodeQL, Semgrep) in the CI/CD pipeline.",
        )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_test_stage_present_across_all_workflows(self):
        test_keywords = [
            "test", "pytest", "jest", "mocha", "rspec",
            "go test", "mvn test", "gradle test", "phpunit", "cargo test",
        ]
        found_test = False
        for stem, (path, parsed) in self.workflows.items():
            if "test" in stem or "ci" in stem:
                found_test = True
                break
            if parsed is None:
                continue
            wf_name = str(parsed.get("name", "")).lower()
            if any(kw in wf_name for kw in ["test", "ci"]):
                found_test = True
                break
            jobs = parsed.get("jobs", {})
            for job_name in jobs:
                if any(kw in job_name.lower() for kw in test_keywords):
                    found_test = True
                    break
            if found_test:
                break
            run_commands = _collect_all_run_commands(parsed)
            uses_list = _collect_all_uses(parsed)
            if any(any(kw in cmd.lower() for kw in test_keywords) for cmd in run_commands):
                found_test = True
                break
            if any(any(kw in u.lower() for kw in test_keywords) for u in uses_list):
                found_test = True
                break
        self.assertTrue(
            found_test,
            "No test stage was found across any workflow file. "
            "The upgrade requires a test stage in the CI/CD pipeline.",
        )


class TestWorkflowStructuralIntegrity(unittest.TestCase):
    """
    Verify that each workflow file has the minimum required top-level keys
    and that no workflow file is empty or malformed.
    """

    def setUp(self):
        self.workflows = _load_workflow_files()

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_all_workflows_have_on_trigger(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                self.fail(f"Workflow '{stem}' at {path} could not be parsed as valid YAML.")
            has_on = "on" in parsed or True in parsed  # PyYAML parses 'on' as True
            self.assertTrue(
                has_on,
                f"Workflow '{stem}' at {path} is missing the required 'on:' trigger block.",
            )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_all_workflows_have_jobs(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                self.fail(f"Workflow '{stem}' at {path} could not be parsed as valid YAML.")
            jobs = parsed.get("jobs", {})
            self.assertGreater(
                len(jobs),
                0,
                f"Workflow '{stem}' at {path} must define at least one job under 'jobs:'.",
            )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_all_workflow_jobs_have_runs_on(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            jobs = parsed.get("jobs", {})
            for job_id, job_def in jobs.items():
                if not isinstance(job_def, dict):
                    continue
                self.assertIn(
                    "runs-on",
                    job_def,
                    f"Job '{job_id}' in workflow '{stem}' at {path} is missing 'runs-on:'. "
                    "Every job must specify a runner.",
                )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_all_workflow_jobs_have_steps(self):
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            jobs = parsed.get("jobs", {})
            for job_id, job_def in jobs.items():
                if not isinstance(job_def, dict):
                    continue
                # Jobs using 'uses' (reusable workflows) don't need steps
                if "uses" in job_def:
                    continue
                steps = job_def.get("steps", [])
                self.assertGreater(
                    len(steps),
                    0,
                    f"Job '{job_id}' in workflow '{stem}' at {path} must define at least one step.",
                )

    def test_no_workflow_file_is_empty(self):
        for stem, (path, parsed) in self.workflows.items():
            file_size = os.path.getsize(path)
            self.assertGreater(
                file_size,
                0,
                f"Workflow file '{stem}' at {path} is empty. "
                "All workflow files introduced by the upgrade must contain valid content.",
            )


class TestNoLegacyWorkflowPatterns(unittest.TestCase):
    """
    Verify that deprecated or legacy patterns are not present in the
    newly introduced workflow files.
    """

    def setUp(self):
        self.workflows = _load_workflow_files()

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_no_set_env_deprecated_command(self):
        """set-env was deprecated and disabled by GitHub in 2020."""
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            run_commands = _collect_all_run_commands(parsed)
            for cmd in run_commands:
                self.assertNotIn(
                    "::set-env",
                    cmd,
                    f"Workflow '{stem}' at {path} uses deprecated '::set-env' workflow command. "
                    "Use $GITHUB_ENV file instead.",
                )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_no_add_path_deprecated_command(self):
        """add-path was deprecated and disabled by GitHub in 2020."""
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            run_commands = _collect_all_run_commands(parsed)
            for cmd in run_commands:
                self.assertNotIn(
                    "::add-path",
                    cmd,
                    f"Workflow '{stem}' at {path} uses deprecated '::add-path' workflow command. "
                    "Use $GITHUB_PATH file instead.",
                )

    @unittest.skipUnless(YAML_AVAILABLE, "PyYAML not installed; skipping YAML content checks")
    def test_no_save_state_deprecated_command(self):
        """save-state was deprecated in favor of environment files."""
        for stem, (path, parsed) in self.workflows.items():
            if parsed is None:
                continue
            run_commands = _collect_all_run_commands(parsed)
            for cmd in run_commands:
                self.assertNotIn(
                    "::save-state",
                    cmd,
                    f"Workflow '{stem}' at {path} uses deprecated '::save-state' workflow command.",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)