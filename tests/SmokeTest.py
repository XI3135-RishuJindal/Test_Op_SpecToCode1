#!/usr/bin/env python3
"""
Upgrade validation tests for GitHub Actions CI pipeline introduction.

These tests verify that the CI pipeline configuration files exist, are valid YAML,
contain the required jobs and triggers, and that all critical pipeline components
(linting, SAST, dependency scanning, tests) are properly configured.

Run with: python -m pytest validate_ci_upgrade.py -v
"""

import os
import glob
import yaml
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKFLOWS_DIR = os.path.join(REPO_ROOT, ".github", "workflows")


def _load_workflow(filename: str) -> dict:
    """Load and parse a workflow YAML file, returning its contents as a dict."""
    path = os.path.join(WORKFLOWS_DIR, filename)
    assert os.path.isfile(path), (
        f"Expected workflow file '{filename}' not found at {path}. "
        "The CI upgrade requires this file to exist."
    )
    with open(path, "r", encoding="utf-8") as fh:
        content = yaml.safe_load(fh)
    assert content is not None, f"Workflow file '{filename}' is empty or invalid YAML."
    return content


def _all_workflow_files() -> list:
    """Return a list of all *.yml / *.yaml files under .github/workflows/."""
    patterns = [
        os.path.join(WORKFLOWS_DIR, "*.yml"),
        os.path.join(WORKFLOWS_DIR, "*.yaml"),
    ]
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern))
    return files


def _collect_job_steps(workflow: dict) -> list:
    """Flatten all steps from all jobs in a workflow into a single list."""
    steps = []
    jobs = workflow.get("jobs", {}) or {}
    for job_def in jobs.values():
        steps.extend(job_def.get("steps", []) or [])
    return steps


def _step_uses_or_run(step: dict) -> str:
    """Return the 'uses' or 'run' value of a step, or empty string."""
    return step.get("uses", "") or step.get("run", "") or ""


# ---------------------------------------------------------------------------
# 1. Infrastructure existence tests
# ---------------------------------------------------------------------------


class TestWorkflowsDirectoryExists:
    """Verify the .github/workflows directory was created by the upgrade."""

    def test_github_directory_exists(self):
        github_dir = os.path.join(REPO_ROOT, ".github")
        assert os.path.isdir(github_dir), (
            f".github directory not found at {github_dir}. "
            "The CI upgrade must create this directory."
        )

    def test_workflows_directory_exists(self):
        assert os.path.isdir(WORKFLOWS_DIR), (
            f".github/workflows directory not found at {WORKFLOWS_DIR}. "
            "The CI upgrade must create this directory."
        )

    def test_at_least_one_workflow_file_exists(self):
        files = _all_workflow_files()
        assert len(files) >= 1, (
            f"No workflow YAML files found in {WORKFLOWS_DIR}. "
            "The CI upgrade must add at least one workflow file."
        )

    def test_expected_workflow_files_present(self):
        """
        The spec requires separate workflow files for lint, test, SAST, and
        dependency scanning. Accept either individual files or a single
        combined pipeline file that contains all four job types.
        """
        individual_files = {
            "lint.yml", "lint.yaml",
            "test.yml", "test.yaml",
            "sast.yml", "sast.yaml",
            "dependency-scan.yml", "dependency-scan.yaml",
            "dependency_scan.yml", "dependency_scan.yaml",
            "security.yml", "security.yaml",
        }
        combined_files = {
            "ci.yml", "ci.yaml",
            "pipeline.yml", "pipeline.yaml",
            "main.yml", "main.yaml",
        }
        existing = {os.path.basename(f) for f in _all_workflow_files()}

        has_individual = bool(existing & individual_files)
        has_combined = bool(existing & combined_files)

        assert has_individual or has_combined, (
            f"No recognised CI workflow files found. Existing files: {existing}. "
            "Expected one of the individual files "
            f"({individual_files}) or a combined file ({combined_files})."
        )


# ---------------------------------------------------------------------------
# 2. YAML validity tests
# ---------------------------------------------------------------------------


class TestWorkflowYamlValidity:
    """Every workflow file must be parseable, valid YAML."""

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_workflow_file_is_valid_yaml(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            try:
                content = yaml.safe_load(fh)
            except yaml.YAMLError as exc:
                pytest.fail(
                    f"Workflow file '{filepath}' contains invalid YAML: {exc}"
                )
        assert content is not None, (
            f"Workflow file '{filepath}' parsed to None — it may be empty."
        )

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_workflow_has_on_trigger(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        assert "on" in content or True in content, (
            f"Workflow '{filepath}' is missing an 'on:' trigger block. "
            "GitHub Actions requires an 'on:' key."
        )

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_workflow_has_jobs(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        assert "jobs" in content, (
            f"Workflow '{filepath}' is missing a 'jobs:' block."
        )
        assert len(content["jobs"]) >= 1, (
            f"Workflow '{filepath}' has an empty 'jobs:' block."
        )


# ---------------------------------------------------------------------------
# 3. Trigger configuration tests
# ---------------------------------------------------------------------------


class TestWorkflowTriggers:
    """
    Every workflow must trigger on both push and pull_request events
    targeting the default branch, as required by the spec.
    """

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_workflow_triggers_on_push(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        # PyYAML parses the bare `on` key as Python True
        trigger = content.get("on") or content.get(True)
        assert trigger is not None, (
            f"Workflow '{filepath}' has no 'on:' trigger."
        )
        if isinstance(trigger, dict):
            assert "push" in trigger, (
                f"Workflow '{filepath}' does not trigger on 'push'. "
                "The spec requires push triggers."
            )

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_workflow_triggers_on_pull_request(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        trigger = content.get("on") or content.get(True)
        assert trigger is not None, (
            f"Workflow '{filepath}' has no 'on:' trigger."
        )
        if isinstance(trigger, dict):
            assert "pull_request" in trigger, (
                f"Workflow '{filepath}' does not trigger on 'pull_request'. "
                "The spec requires pull_request triggers."
            )

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_push_trigger_targets_default_branch(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        trigger = content.get("on") or content.get(True)
        if not isinstance(trigger, dict):
            pytest.skip("Trigger is not a mapping — skipping branch check.")
        push_cfg = trigger.get("push")
        if not isinstance(push_cfg, dict):
            pytest.skip("Push trigger has no branch filter — acceptable.")
        branches = push_cfg.get("branches", [])
        default_branch_names = {"main", "master", "develop", "trunk"}
        assert any(b in default_branch_names for b in branches), (
            f"Workflow '{filepath}' push trigger does not target a recognised "
            f"default branch. Found: {branches}. "
            "Expected one of: {default_branch_names}."
        )


# ---------------------------------------------------------------------------
# 4. Lint job tests
# ---------------------------------------------------------------------------


class TestLintJob:
    """Verify a linting job is present and uses a checkout step."""

    def _find_lint_workflow(self):
        candidates = ["lint.yml", "lint.yaml", "ci.yml", "ci.yaml",
                      "pipeline.yml", "pipeline.yaml", "main.yml", "main.yaml"]
        for name in candidates:
            path = os.path.join(WORKFLOWS_DIR, name)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as fh:
                    return yaml.safe_load(fh), name
        return None, None

    def test_lint_job_exists(self):
        workflow, name = self._find_lint_workflow()
        if workflow is None:
            pytest.skip("No lint or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        lint_job_keys = [k for k in jobs if "lint" in k.lower()]
        assert len(lint_job_keys) >= 1, (
            f"No lint job found in '{name}'. "
            "The spec requires a linting job. "
            f"Existing jobs: {list(jobs.keys())}"
        )

    def test_lint_job_has_checkout_step(self):
        workflow, name = self._find_lint_workflow()
        if workflow is None:
            pytest.skip("No lint or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        lint_job_keys = [k for k in jobs if "lint" in k.lower()]
        if not lint_job_keys:
            pytest.skip("No lint job found — covered by test_lint_job_exists.")
        lint_job = jobs[lint_job_keys[0]]
        steps = lint_job.get("steps", [])
        uses_values = [s.get("uses", "") for s in steps if s.get("uses")]
        checkout_steps = [u for u in uses_values if "actions/checkout" in u]
        assert len(checkout_steps) >= 1, (
            f"Lint job in '{name}' is missing an 'actions/checkout' step. "
            "All jobs must check out the repository."
        )

    def test_lint_job_has_linter_step(self):
        workflow, name = self._find_lint_workflow()
        if workflow is None:
            pytest.skip("No lint or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        lint_job_keys = [k for k in jobs if "lint" in k.lower()]
        if not lint_job_keys:
            pytest.skip("No lint job found.")
        lint_job = jobs[lint_job_keys[0]]
        steps = lint_job.get("steps", [])
        # A linter step either uses a known linter action or runs a linter command
        linter_keywords = [
            "eslint", "flake8", "ruff", "pylint", "golangci-lint",
            "checkstyle", "rubocop", "ktlint", "swiftlint", "hadolint",
            "super-linter", "reviewdog", "lint", "stylelint", "prettier",
        ]
        found = False
        for step in steps:
            combined = _step_uses_or_run(step).lower()
            if any(kw in combined for kw in linter_keywords):
                found = True
                break
        assert found, (
            f"Lint job in '{name}' does not appear to invoke a linter. "
            f"Steps found: {[_step_uses_or_run(s) for s in steps]}. "
            "Add a step that runs a linter appropriate for the repository's language."
        )


# ---------------------------------------------------------------------------
# 5. Test job tests
# ---------------------------------------------------------------------------


class TestTestJob:
    """Verify a test-execution job is present."""

    def _find_test_workflow(self):
        candidates = ["test.yml", "test.yaml", "ci.yml", "ci.yaml",
                      "pipeline.yml", "pipeline.yaml", "main.yml", "main.yaml"]
        for name in candidates:
            path = os.path.join(WORKFLOWS_DIR, name)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as fh:
                    return yaml.safe_load(fh), name
        return None, None

    def test_test_job_exists(self):
        workflow, name = self._find_test_workflow()
        if workflow is None:
            pytest.skip("No test or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        test_job_keys = [k for k in jobs if "test" in k.lower()]
        assert len(test_job_keys) >= 1, (
            f"No test job found in '{name}'. "
            "The spec requires a test-execution job. "
            f"Existing jobs: {list(jobs.keys())}"
        )

    def test_test_job_has_checkout_step(self):
        workflow, name = self._find_test_workflow()
        if workflow is None:
            pytest.skip("No test or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        test_job_keys = [k for k in jobs if "test" in k.lower()]
        if not test_job_keys:
            pytest.skip("No test job found.")
        test_job = jobs[test_job_keys[0]]
        steps = test_job.get("steps", [])
        uses_values = [s.get("uses", "") for s in steps if s.get("uses")]
        checkout_steps = [u for u in uses_values if "actions/checkout" in u]
        assert len(checkout_steps) >= 1, (
            f"Test job in '{name}' is missing an 'actions/checkout' step."
        )

    def test_test_job_has_test_runner_step(self):
        workflow, name = self._find_test_workflow()
        if workflow is None:
            pytest.skip("No test or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        test_job_keys = [k for k in jobs if "test" in k.lower()]
        if not test_job_keys:
            pytest.skip("No test job found.")
        test_job = jobs[test_job_keys[0]]
        steps = test_job.get("steps", [])
        runner_keywords = [
            "pytest", "jest", "mocha", "npm test", "yarn test",
            "go test", "mvn test", "gradle test", "rspec", "cargo test",
            "dotnet test", "phpunit", "test", "spec",
        ]
        found = False
        for step in steps:
            combined = _step_uses_or_run(step).lower()
            if any(kw in combined for kw in runner_keywords):
                found = True
                break
        assert found, (
            f"Test job in '{name}' does not appear to invoke a test runner. "
            f"Steps found: {[_step_uses_or_run(s) for s in steps]}. "
            "Add a step that runs the project's test suite."
        )


# ---------------------------------------------------------------------------
# 6. SAST job tests
# ---------------------------------------------------------------------------


class TestSASTJob:
    """Verify a SAST (static application security testing) job is present."""

    def _find_sast_workflow(self):
        candidates = [
            "sast.yml", "sast.yaml",
            "security.yml", "security.yaml",
            "codeql.yml", "codeql.yaml",
            "ci.yml", "ci.yaml",
            "pipeline.yml", "pipeline.yaml",
            "main.yml", "main.yaml",
        ]
        for name in candidates:
            path = os.path.join(WORKFLOWS_DIR, name)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as fh:
                    return yaml.safe_load(fh), name
        return None, None

    def test_sast_job_exists(self):
        workflow, name = self._find_sast_workflow()
        if workflow is None:
            pytest.skip("No SAST or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        sast_keywords = ["sast", "security", "codeql", "semgrep", "sonar",
                         "snyk", "bandit", "gosec", "brakeman", "scan"]
        sast_job_keys = [
            k for k in jobs
            if any(kw in k.lower() for kw in sast_keywords)
        ]
        # Also check step-level for SAST tools in all jobs
        all_steps = []
        for job_def in jobs.values():
            all_steps.extend(job_def.get("steps", []) or [])
        sast_in_steps = any(
            any(kw in _step_uses_or_run(s).lower() for kw in sast_keywords)
            for s in all_steps
        )
        assert len(sast_job_keys) >= 1 or sast_in_steps, (
            f"No SAST job or SAST step found in '{name}'. "
            "The spec requires SAST scanning. "
            f"Existing jobs: {list(jobs.keys())}. "
            "Add a job using CodeQL, Semgrep, Bandit, or another SAST tool."
        )

    def test_sast_uses_recognised_tool(self):
        workflow, name = self._find_sast_workflow()
        if workflow is None:
            pytest.skip("No SAST or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        all_steps = _collect_job_steps(workflow)
        sast_tools = [
            "codeql", "semgrep", "sonarcloud", "sonarqube", "snyk",
            "bandit", "gosec", "brakeman", "trivy", "grype",
            "github/codeql-action", "returntocorp/semgrep",
        ]
        found = any(
            any(tool in _step_uses_or_run(s).lower() for tool in sast_tools)
            for s in all_steps
        )
        assert found, (
            f"No recognised SAST tool found in workflow '{name}'. "
            f"Recognised tools: {sast_tools}. "
            "Ensure a SAST action or command is present."
        )


# ---------------------------------------------------------------------------
# 7. Dependency scanning job tests
# ---------------------------------------------------------------------------


class TestDependencyScanJob:
    """Verify a dependency vulnerability scanning job is present."""

    def _find_dep_scan_workflow(self):
        candidates = [
            "dependency-scan.yml", "dependency-scan.yaml",
            "dependency_scan.yml", "dependency_scan.yaml",
            "deps.yml", "deps.yaml",
            "security.yml", "security.yaml",
            "ci.yml", "ci.yaml",
            "pipeline.yml", "pipeline.yaml",
            "main.yml", "main.yaml",
        ]
        for name in candidates:
            path = os.path.join(WORKFLOWS_DIR, name)
            if os.path.isfile(path):
                with open(path, "r", encoding="utf-8") as fh:
                    return yaml.safe_load(fh), name
        return None, None

    def test_dependency_scan_job_exists(self):
        workflow, name = self._find_dep_scan_workflow()
        if workflow is None:
            pytest.skip("No dependency-scan or combined workflow file found.")
        jobs = workflow.get("jobs", {})
        dep_keywords = [
            "depend", "dep-scan", "dependency", "vuln", "audit",
            "trivy", "snyk", "grype", "safety", "pip-audit",
            "npm audit", "yarn audit", "owasp",
        ]
        dep_job_keys = [
            k for k in jobs
            if any(kw in k.lower() for kw in dep_keywords)
        ]
        all_steps = _collect_job_steps(workflow)
        dep_in_steps = any(
            any(kw in _step_uses_or_run(s).lower() for kw in dep_keywords)
            for s in all_steps
        )
        assert len(dep_job_keys) >= 1 or dep_in_steps, (
            f"No dependency scanning job or step found in '{name}'. "
            "The spec requires dependency vulnerability scanning. "
            f"Existing jobs: {list(jobs.keys())}. "
            "Add a job using Trivy, Snyk, pip-audit, npm audit, or similar."
        )

    def test_dependency_scan_uses_recognised_tool(self):
        workflow, name = self._find_dep_scan_workflow()
        if workflow is None:
            pytest.skip("No dependency-scan or combined workflow file found.")
        all_steps = _collect_job_steps(workflow)
        dep_tools = [
            "trivy", "snyk", "grype", "pip-audit", "safety",
            "npm audit", "yarn audit", "owasp", "dependabot",
            "aquasecurity/trivy-action", "snyk/actions",
            "anchore/scan-action", "dependency-check",
        ]
        found = any(
            any(tool in _step_uses_or_run(s).lower() for tool in dep_tools)
            for s in all_steps
        )
        assert found, (
            f"No recognised dependency scanning tool found in workflow '{name}'. "
            f"Recognised tools: {dep_tools}."
        )


# ---------------------------------------------------------------------------
# 8. Job runner / environment tests
# ---------------------------------------------------------------------------


class TestJobRunnerConfiguration:
    """Every job must specify a runs-on value."""

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_all_jobs_have_runs_on(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        jobs = content.get("jobs", {})
        missing = [
            job_name for job_name, job_def in jobs.items()
            if not job_def.get("runs-on")
        ]
        assert len(missing) == 0, (
            f"Jobs in '{filepath}' are missing 'runs-on': {missing}. "
            "Every GitHub Actions job must specify a runner."
        )

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_all_jobs_use_supported_runner(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        jobs = content.get("jobs", {})
        supported_prefixes = [
            "ubuntu-", "windows-", "macos-", "self-hosted",
        ]
        for job_name, job_def in jobs.items():
            runs_on = job_def.get("runs-on", "")
            if isinstance(runs_on, list):
                # self-hosted runner with labels
                continue
            assert any(runs_on.startswith(p) for p in supported_prefixes), (
                f"Job '{job_name}' in '{filepath}' uses unrecognised runner: "
                f"'{runs_on}'. Expected one of: {supported_prefixes}."
            )


# ---------------------------------------------------------------------------
# 9. Security permissions tests
# ---------------------------------------------------------------------------


class TestWorkflowPermissions:
    """
    Workflows should follow least-privilege: either declare minimal permissions
    or rely on the repository default (read-only). This test warns when
    write-all permissions are granted without justification.
    """

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_workflow_does_not_grant_write_all_globally(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        top_level_perms = content.get("permissions")
        if top_level_perms == "write-all":
            pytest.fail(
                f"Workflow '{filepath}' grants 'write-all' permissions globally. "
                "Use least-privilege permissions scoped to individual jobs."
            )

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_sast_job_has_security_events_write_if_using_codeql(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            content = yaml.safe_load(fh)
        jobs = content.get("jobs", {})
        for job_name, job_def in jobs.items():
            steps = job_def.get("steps", []) or []
            uses_codeql = any(
                "codeql" in (s.get("uses", "") or "").lower()
                for s in steps
            )
            if uses_codeql:
                perms = job_def.get("permissions", {})
                if isinstance(perms, dict):
                    security_events = perms.get("security-events", "")
                    assert security_events == "write", (
                        f"Job '{job_name}' in '{filepath}' uses CodeQL but does not "
                        "set 'permissions.security-events: write'. "
                        "CodeQL requires this permission to upload SARIF results."
                    )


# ---------------------------------------------------------------------------
# 10. Pipeline completeness — all four required components present
# ---------------------------------------------------------------------------


class TestPipelineCompleteness:
    """
    High-level assertion: across all workflow files, all four required
    CI components (lint, test, SAST, dependency-scan) must be present.
    """

    def _all_step_strings(self) -> list:
        strings = []
        for filepath in _all_workflow_files():
            with open(filepath, "r", encoding="utf-8") as fh:
                content = yaml.safe_load(fh)
            if not content:
                continue
            jobs = content.get("jobs", {}) or {}
            for job_name, job_def in jobs.items():
                strings.append(job_name.lower())
                for step in (job_def.get("steps", []) or []):
                    strings.append(_step_uses_or_run(step).lower())
                    strings.append((step.get("name", "") or "").lower())
        return strings

    def test_linting_component_present(self):
        all_strings = self._all_step_strings()
        lint_keywords = [
            "lint", "eslint", "flake8", "ruff", "pylint",
            "golangci", "checkstyle", "rubocop", "stylelint",
        ]
        found = any(
            any(kw in s for kw in lint_keywords)
            for s in all_strings
        )
        assert found, (
            "No linting component found across all workflow files. "
            "The spec requires automated linting. "
            f"Keywords searched: {lint_keywords}"
        )

    def test_test_execution_component_present(self):
        all_strings = self._all_step_strings()
        test_keywords = [
            "test", "pytest", "jest", "mocha", "rspec",
            "go test", "mvn test", "cargo test",
        ]
        found = any(
            any(kw in s for kw in test_keywords)
            for s in all_strings
        )
        assert found, (
            "No test-execution component found across all workflow files. "
            "The spec requires automated test execution. "
            f"Keywords searched: {test_keywords}"
        )

    def test_sast_component_present(self):
        all_strings = self._all_step_strings()
        sast_keywords = [
            "sast", "codeql", "semgrep", "sonar", "bandit",
            "gosec", "brakeman", "security-scan", "snyk",
        ]
        found = any(
            any(kw in s for kw in sast_keywords)
            for s in all_strings
        )
        assert found, (
            "No SAST component found across all workflow files. "
            "The spec requires static application security testing. "
            f"Keywords searched: {sast_keywords}"
        )

    def test_dependency_scanning_component_present(self):
        all_strings = self._all_step_strings()
        dep_keywords = [
            "trivy", "snyk", "grype", "pip-audit", "safety",
            "npm audit", "yarn audit", "dependency-check",
            "dependency-scan", "dep-scan", "audit",
        ]
        found = any(
            any(kw in s for kw in dep_keywords)
            for s in all_strings
        )
        assert found, (
            "No dependency scanning component found across all workflow files. "
            "The spec requires dependency vulnerability scanning. "
            f"Keywords searched: {dep_keywords}"
        )

    def test_all_four_components_present(self):
        """
        Composite assertion: all four required pipeline components must be
        present. This is the primary upgrade-success gate.
        """
        all_strings = self._all_step_strings()

        components = {
            "linting": [
                "lint", "eslint", "flake8", "ruff", "pylint",
                "golangci", "checkstyle", "rubocop",
            ],
            "test_execution": [
                "test", "pytest", "jest", "mocha", "rspec",
                "go test", "mvn test", "cargo test",
            ],
            "sast": [
                "sast", "codeql", "semgrep", "sonar", "bandit",
                "gosec", "brakeman", "snyk",
            ],
            "dependency_scanning": [
                "trivy", "snyk", "grype", "pip-audit", "safety",
                "npm audit", "yarn audit", "dependency-check", "audit",
            ],
        }

        missing = []
        for component, keywords in components.items():
            found = any(
                any(kw in s for kw in keywords)
                for s in all_strings
            )
            if not found:
                missing.append(component)

        assert len(missing) == 0, (
            f"CI pipeline upgrade is INCOMPLETE. "
            f"Missing components: {missing}. "
            "All four components (linting, test_execution, sast, "
            "dependency_scanning) must be present in the workflow files."
        )


# ---------------------------------------------------------------------------
# 11. No legacy / placeholder artefacts
# ---------------------------------------------------------------------------


class TestNoPlaceholderArtefacts:
    """Verify that placeholder tokens from the spec/tasks were not committed."""

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_no_todo_placeholders_in_workflow(self, filepath):
        with open(filepath, "r", encoding="utf-8") as fh:
            raw = fh.read()
        forbidden = ["<language>", "<package-manager>", "<linter>",
                     "<test-command>", "TODO", "FIXME", "<runtime>"]
        found = [token for token in forbidden if token in raw]
        assert len(found) == 0, (
            f"Workflow file '{filepath}' contains unresolved placeholder tokens: "
            f"{found}. Replace all placeholders with actual values before merging."
        )

    @pytest.mark.parametrize("filepath", _all_workflow_files())
    def test_no_gitkeep_only_workflows_directory(self, filepath):
        """
        .gitkeep is a temporary placeholder; real workflow files must exist
        alongside or instead of it.
        """
        basename = os.path.basename(filepath)
        assert basename != ".gitkeep", (
            f"Only a .gitkeep placeholder found in {WORKFLOWS_DIR}. "
            "Real workflow files must be added."
        )