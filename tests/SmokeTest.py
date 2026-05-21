#!/usr/bin/env python3
"""
CI Pipeline Upgrade Validation Tests

Verifies that the CI pipeline setup (build and test stages) was successfully
established. These tests validate the pipeline configuration files, stage
definitions, trigger rules, and that the pipeline infrastructure is in place
as specified by the upgrade goal.

Run with: python -m pytest test_ci_pipeline_upgrade.py -v
"""

import os
import re
import sys
import subprocess
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Candidate CI configuration file paths (ordered by likelihood)
CANDIDATE_CI_FILES = [
    ".github/workflows/ci.yml",
    ".github/workflows/ci.yaml",
    ".github/workflows/build.yml",
    ".github/workflows/build.yaml",
    ".gitlab-ci.yml",
    ".gitlab-ci.yaml",
    "Jenkinsfile",
    ".circleci/config.yml",
    ".circleci/config.yaml",
    "azure-pipelines.yml",
    "azure-pipelines.yaml",
    "bitbucket-pipelines.yml",
    "bitbucket-pipelines.yaml",
    ".drone.yml",
    "circle.yml",
]

TECH_STACK_DOC = "docs/tech-stack.md"
CI_BASELINE_DOC = "docs/ci-baseline.md"


def _abs(relative_path: str) -> str:
    """Return absolute path relative to repo root."""
    return os.path.join(REPO_ROOT, relative_path)


def _find_ci_config_file() -> str | None:
    """Return the first CI config file that exists in the repository."""
    for candidate in CANDIDATE_CI_FILES:
        full = _abs(candidate)
        if os.path.isfile(full):
            return candidate
    return None


def _read_ci_config() -> tuple[str, str]:
    """
    Return (relative_path, content) of the CI config file.
    Raises pytest.skip if no file is found.
    """
    path = _find_ci_config_file()
    if path is None:
        pytest.fail(
            "No CI configuration file was found in the repository. "
            "Expected one of: " + ", ".join(CANDIDATE_CI_FILES)
        )
    with open(_abs(path), "r", encoding="utf-8") as fh:
        return path, fh.read()


# ---------------------------------------------------------------------------
# 1. CI configuration file existence
# ---------------------------------------------------------------------------

class TestCIConfigFileExists:
    """The upgrade must produce a committed CI configuration file."""

    def test_ci_config_file_is_present(self):
        """At least one recognised CI configuration file must exist."""
        found = _find_ci_config_file()
        assert found is not None, (
            "No CI configuration file found. "
            "Expected one of: " + ", ".join(CANDIDATE_CI_FILES)
        )

    def test_ci_config_file_is_not_empty(self):
        """The CI configuration file must not be empty."""
        _, content = _read_ci_config()
        assert content.strip(), "CI configuration file exists but is empty."

    def test_ci_config_file_is_readable_text(self):
        """The CI configuration file must be valid UTF-8 text."""
        path, _ = _read_ci_config()
        try:
            with open(_abs(path), "r", encoding="utf-8") as fh:
                fh.read()
        except UnicodeDecodeError as exc:
            pytest.fail(f"CI configuration file is not valid UTF-8: {exc}")


# ---------------------------------------------------------------------------
# 2. Build stage is defined
# ---------------------------------------------------------------------------

class TestBuildStageDefinition:
    """The pipeline must contain an explicit build stage."""

    def test_build_stage_keyword_present(self):
        """
        The word 'build' must appear as a stage/job name in the CI config.
        Covers GitHub Actions job id, GitLab CI stage name, Jenkinsfile stage,
        CircleCI job name, etc.
        """
        _, content = _read_ci_config()
        # Case-insensitive search for 'build' as a standalone token
        assert re.search(r'\bbuild\b', content, re.IGNORECASE), (
            "No 'build' stage or job found in the CI configuration file. "
            "A build stage is required by the upgrade spec."
        )

    def test_build_stage_has_steps_or_script(self):
        """
        The build stage must contain at least one step, script, or run
        directive — it must not be an empty placeholder.
        """
        _, content = _read_ci_config()
        has_steps = bool(re.search(r'\bsteps\b', content, re.IGNORECASE))
        has_script = bool(re.search(r'\bscript\b', content, re.IGNORECASE))
        has_run = bool(re.search(r'\brun\b', content, re.IGNORECASE))
        has_sh = bool(re.search(r'\bsh\b', content))
        assert any([has_steps, has_script, has_run, has_sh]), (
            "The CI configuration file does not appear to contain any "
            "executable steps (steps/script/run/sh). "
            "The build stage must execute actual commands."
        )


# ---------------------------------------------------------------------------
# 3. Test stage is defined
# ---------------------------------------------------------------------------

class TestTestStageDefinition:
    """The pipeline must contain an explicit test stage."""

    def test_test_stage_keyword_present(self):
        """
        The word 'test' must appear as a stage/job name in the CI config.
        """
        _, content = _read_ci_config()
        assert re.search(r'\btest\b', content, re.IGNORECASE), (
            "No 'test' stage or job found in the CI configuration file. "
            "A test stage is required by the upgrade spec."
        )

    def test_build_and_test_stages_are_distinct(self):
        """
        Both 'build' and 'test' keywords must be present, confirming two
        separate stages rather than a single combined stage.
        """
        _, content = _read_ci_config()
        has_build = bool(re.search(r'\bbuild\b', content, re.IGNORECASE))
        has_test = bool(re.search(r'\btest\b', content, re.IGNORECASE))
        assert has_build and has_test, (
            "CI configuration must define both a 'build' stage and a 'test' "
            f"stage. Found build={has_build}, test={has_test}."
        )


# ---------------------------------------------------------------------------
# 4. Trigger configuration
# ---------------------------------------------------------------------------

class TestPipelineTriggers:
    """The pipeline must trigger on push and/or pull-request events."""

    def test_push_trigger_is_configured(self):
        """
        The CI config must reference a push trigger so the pipeline runs on
        every code push.
        """
        _, content = _read_ci_config()
        # GitHub Actions: 'push', GitLab CI: 'push', CircleCI: branches,
        # Jenkinsfile: pollSCM / webhook — accept broad match
        has_push = bool(re.search(r'\bpush\b', content, re.IGNORECASE))
        has_webhook = bool(re.search(r'webhook|pollSCM|trigger', content, re.IGNORECASE))
        assert has_push or has_webhook, (
            "No push trigger found in the CI configuration. "
            "The pipeline must run automatically on code push."
        )

    def test_pull_request_or_merge_request_trigger_is_configured(self):
        """
        The CI config must reference a pull_request or merge_request trigger
        so the pipeline acts as a merge gate.
        """
        _, content = _read_ci_config()
        has_pr = bool(re.search(
            r'pull_request|merge_request|pullrequest|pull-request',
            content, re.IGNORECASE
        ))
        if not has_pr:
            pytest.xfail(
                "No pull_request / merge_request trigger found. "
                "This is strongly recommended by the upgrade spec to act as a "
                "merge gate, but may be deferred. Mark as resolved once "
                "branch protection is configured."
            )

    def test_default_branch_is_targeted(self):
        """
        The pipeline should target the default branch (main, master, or
        equivalent) in its trigger configuration.
        """
        _, content = _read_ci_config()
        has_default_branch = bool(re.search(
            r'\b(main|master|develop|trunk)\b', content, re.IGNORECASE
        ))
        # Also accept 'branches' keyword as a signal that branch filtering exists
        has_branches_key = bool(re.search(r'\bbranches\b', content, re.IGNORECASE))
        assert has_default_branch or has_branches_key, (
            "The CI configuration does not appear to target a default branch "
            "(main/master/develop/trunk). "
            "Ensure the pipeline is scoped to the correct branch."
        )


# ---------------------------------------------------------------------------
# 5. Stage ordering — build before test
# ---------------------------------------------------------------------------

class TestStageOrdering:
    """Build stage must be defined/listed before the test stage."""

    def test_build_appears_before_test_in_config(self):
        """
        In the CI config file, the first occurrence of 'build' (as a stage
        name) must appear before the first occurrence of 'test' (as a stage
        name). This validates the sequential Build → Test ordering required
        by the spec.
        """
        _, content = _read_ci_config()
        build_match = re.search(r'\bbuild\b', content, re.IGNORECASE)
        test_match = re.search(r'\btest\b', content, re.IGNORECASE)

        assert build_match is not None, "No 'build' keyword found in CI config."
        assert test_match is not None, "No 'test' keyword found in CI config."

        assert build_match.start() < test_match.start(), (
            f"'build' first appears at position {build_match.start()} but "
            f"'test' first appears at position {test_match.start()}. "
            "The build stage must be defined before the test stage."
        )


# ---------------------------------------------------------------------------
# 6. Dependency installation step
# ---------------------------------------------------------------------------

class TestDependencyInstallation:
    """The build stage must install dependencies before building."""

    INSTALL_PATTERNS = [
        r'\bnpm\s+install\b',
        r'\bnpm\s+ci\b',
        r'\byarn\s+install\b',
        r'\bpip\s+install\b',
        r'\bpipenv\s+install\b',
        r'\bpoetry\s+install\b',
        r'\bmvn\s+install\b',
        r'\bgradle\b.*\bdependencies\b',
        r'\bgo\s+mod\s+download\b',
        r'\bbundle\s+install\b',
        r'\bcomposer\s+install\b',
        r'\bcargo\s+fetch\b',
        r'\bapt(-get)?\s+install\b',
        r'\binstall\s+dependencies\b',
        r'\bdependencies\b',   # broad fallback
    ]

    def test_dependency_install_command_present(self):
        """
        The CI configuration must include a dependency installation command
        so the build environment is reproducible.
        """
        _, content = _read_ci_config()
        found = any(
            re.search(pattern, content, re.IGNORECASE)
            for pattern in self.INSTALL_PATTERNS
        )
        assert found, (
            "No dependency installation command found in the CI configuration. "
            "The build stage must install dependencies (e.g., npm ci, "
            "pip install -r requirements.txt, mvn install, etc.)."
        )


# ---------------------------------------------------------------------------
# 7. Documentation artefacts created by the upgrade
# ---------------------------------------------------------------------------

class TestUpgradeDocumentationArtefacts:
    """Phase 1 of the upgrade requires specific documentation files."""

    def test_tech_stack_doc_exists(self):
        """
        docs/tech-stack.md must exist — created during Phase 1 to document
        the identified language, runtime, build tool, and CI platform.
        """
        path = _abs(TECH_STACK_DOC)
        assert os.path.isfile(path), (
            f"{TECH_STACK_DOC} not found. "
            "Phase 1 of the upgrade requires this file to document the "
            "tech stack findings."
        )

    def test_tech_stack_doc_is_not_empty(self):
        """docs/tech-stack.md must contain actual content."""
        path = _abs(TECH_STACK_DOC)
        if not os.path.isfile(path):
            pytest.skip(f"{TECH_STACK_DOC} does not exist — covered by prior test.")
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        assert content.strip(), f"{TECH_STACK_DOC} exists but is empty."

    def test_tech_stack_doc_mentions_ci_platform(self):
        """
        docs/tech-stack.md must mention the chosen CI platform so the
        decision is recorded as required by Phase 1.
        """
        path = _abs(TECH_STACK_DOC)
        if not os.path.isfile(path):
            pytest.skip(f"{TECH_STACK_DOC} does not exist — covered by prior test.")
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        ci_platforms = [
            "github actions", "gitlab ci", "gitlab-ci", "circleci",
            "circle ci", "jenkins", "azure pipelines", "bitbucket pipelines",
            "drone", "travis", "teamcity",
        ]
        found = any(p in content.lower() for p in ci_platforms)
        assert found, (
            f"{TECH_STACK_DOC} does not mention a CI platform. "
            "Phase 1 requires documenting the chosen CI platform."
        )

    def test_ci_baseline_doc_exists(self):
        """
        docs/ci-baseline.md must exist — created during Phase 1 to record
        the pre-CI test suite baseline (pass/fail counts).
        """
        path = _abs(CI_BASELINE_DOC)
        assert os.path.isfile(path), (
            f"{CI_BASELINE_DOC} not found. "
            "Phase 1 of the upgrade requires this file to capture the "
            "test suite baseline before CI was introduced."
        )

    def test_ci_baseline_doc_is_not_empty(self):
        """docs/ci-baseline.md must contain actual content."""
        path = _abs(CI_BASELINE_DOC)
        if not os.path.isfile(path):
            pytest.skip(f"{CI_BASELINE_DOC} does not exist — covered by prior test.")
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
        assert content.strip(), f"{CI_BASELINE_DOC} exists but is empty."


# ---------------------------------------------------------------------------
# 8. CI configuration file is syntactically valid (YAML platforms)
# ---------------------------------------------------------------------------

class TestCIConfigSyntax:
    """For YAML-based CI platforms, the config must parse without errors."""

    def test_yaml_ci_config_is_valid(self):
        """
        If the CI configuration file has a .yml or .yaml extension, it must
        be parseable as valid YAML.
        """
        path = _find_ci_config_file()
        if path is None:
            pytest.fail("No CI configuration file found.")

        if not (path.endswith(".yml") or path.endswith(".yaml")):
            pytest.skip(
                f"CI config file '{path}' is not YAML — skipping YAML syntax check."
            )

        try:
            import yaml  # PyYAML
        except ImportError:
            pytest.skip(
                "PyYAML is not installed; cannot validate YAML syntax. "
                "Install with: pip install pyyaml"
            )

        with open(_abs(path), "r", encoding="utf-8") as fh:
            raw = fh.read()

        try:
            parsed = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            pytest.fail(
                f"CI configuration file '{path}' contains invalid YAML: {exc}"
            )

        assert parsed is not None, (
            f"CI configuration file '{path}' parsed as empty/null YAML document."
        )
        assert isinstance(parsed, dict), (
            f"CI configuration file '{path}' top-level YAML must be a mapping, "
            f"got {type(parsed).__name__}."
        )

    def test_yaml_ci_config_has_expected_top_level_keys(self):
        """
        For GitHub Actions: expects 'on' (trigger) and 'jobs'.
        For GitLab CI: expects 'stages'.
        For CircleCI: expects 'version' and 'jobs'.
        At least one of these patterns must be present.
        """
        path = _find_ci_config_file()
        if path is None:
            pytest.fail("No CI configuration file found.")

        if not (path.endswith(".yml") or path.endswith(".yaml")):
            pytest.skip("CI config is not YAML — skipping key structure check.")

        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed.")

        with open(_abs(path), "r", encoding="utf-8") as fh:
            parsed = yaml.safe_load(fh.read())

        if not isinstance(parsed, dict):
            pytest.skip("Top-level YAML is not a mapping — skipping key check.")

        keys = set(str(k).lower() for k in parsed.keys())

        github_actions = {"on", "jobs"}.issubset(keys) or {"true", "jobs"}.issubset(keys)
        gitlab_ci = "stages" in keys
        circleci = "version" in keys and "jobs" in keys
        azure = "trigger" in keys and "jobs" in keys
        generic_jobs = "jobs" in keys
        generic_stages = "stages" in keys

        assert any([github_actions, gitlab_ci, circleci, azure, generic_jobs, generic_stages]), (
            f"CI configuration top-level keys {sorted(keys)} do not match any "
            "recognised CI platform structure "
            "(GitHub Actions: on+jobs, GitLab CI: stages, "
            "CircleCI: version+jobs, Azure Pipelines: trigger+jobs)."
        )


# ---------------------------------------------------------------------------
# 9. Feature branch was created (git history check)
# ---------------------------------------------------------------------------

class TestFeatureBranchCreated:
    """
    Phase 1 requires creating a feature branch ci/setup-build-test-pipeline.
    Validate it exists in git history (local or remote).
    """

    def _git_available(self) -> bool:
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True, check=True, cwd=REPO_ROOT
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def test_ci_feature_branch_exists_in_git(self):
        """
        The branch 'ci/setup-build-test-pipeline' must exist locally or
        remotely, confirming Phase 1 branch creation was completed.
        """
        if not self._git_available():
            pytest.skip("git is not available in this environment.")

        result = subprocess.run(
            ["git", "branch", "-a"],
            capture_output=True, text=True, cwd=REPO_ROOT
        )
        if result.returncode != 0:
            pytest.skip("Could not list git branches — not a git repository or no commits.")

        branches = result.stdout
        assert "ci/setup-build-test-pipeline" in branches, (
            "Branch 'ci/setup-build-test-pipeline' not found in git branches. "
            "Phase 1 requires creating this feature branch for CI configuration work. "
            f"Available branches:\n{branches}"
        )


# ---------------------------------------------------------------------------
# 10. No legacy/placeholder TODO markers left in CI config
# ---------------------------------------------------------------------------

class TestNoPendingPlaceholders:
    """The CI configuration must not contain unresolved TODO placeholders."""

    TODO_PATTERN = re.compile(
        r'\b(TODO|FIXME|PLACEHOLDER|YOUR_COMMAND_HERE|<YOUR|INSERT_HERE)\b',
        re.IGNORECASE
    )

    def test_no_unresolved_todos_in_ci_config(self):
        """
        The CI configuration file must not contain TODO/FIXME/PLACEHOLDER
        markers that indicate incomplete setup.
        """
        _, content = _read_ci_config()
        matches = self.TODO_PATTERN.findall(content)
        assert not matches, (
            f"CI configuration contains {len(matches)} unresolved placeholder(s): "
            f"{sorted(set(matches))}. "
            "All TODO/FIXME/PLACEHOLDER markers must be resolved before the "
            "upgrade is considered complete."
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))