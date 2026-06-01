"""
CI/CD Pipeline Upgrade Validation Tests

Validates that the CI/CD pipeline configuration (test, lint, and SAST stages)
has been successfully added to the repository.

These tests verify:
- Pipeline configuration files exist at expected paths
- All three required stages (test, lint, sast) are defined
- Pipeline triggers are correctly configured (push + pull_request)
- SAST, lint, and test jobs contain required configuration keys
- No legacy/absent pipeline state remains
- CI_SETUP_NOTES.md documents the setup as required by the spec
"""

import os
import sys
import unittest
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent  # adjust depth if needed


def _find_repo_root() -> Path:
    """Walk up from this file until we find a .git directory or hit the fs root."""
    candidate = Path(__file__).resolve().parent
    for _ in range(10):
        if (candidate / ".git").exists():
            return candidate
        parent = candidate.parent
        if parent == candidate:
            break
        candidate = parent
    # Fall back to two levels above this file
    return Path(__file__).resolve().parent.parent


REPO_ROOT = _find_repo_root()

# Supported pipeline file locations (ordered by preference)
_GITHUB_WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"
_GITLAB_CI_FILE = REPO_ROOT / ".gitlab-ci.yml"
_BITBUCKET_PIPELINES_FILE = REPO_ROOT / "bitbucket-pipelines.yml"
_CIRCLECI_DIR = REPO_ROOT / ".circleci"
_JENKINS_FILE = REPO_ROOT / "Jenkinsfile"
_AZURE_PIPELINES_FILE = REPO_ROOT / "azure-pipelines.yml"


def _load_yaml(path: Path) -> dict:
    """Load a YAML file, returning a dict. Skips if PyYAML is unavailable."""
    try:
        import yaml  # type: ignore
    except ImportError:
        raise unittest.SkipTest(
            "PyYAML is not installed; install it to run pipeline validation tests."
        )
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _find_github_workflow_files() -> list:
    """Return all YAML files inside .github/workflows/."""
    if not _GITHUB_WORKFLOW_DIR.is_dir():
        return []
    return list(_GITHUB_WORKFLOW_DIR.glob("*.yml")) + list(
        _GITHUB_WORKFLOW_DIR.glob("*.yaml")
    )


def _find_ci_workflow_file() -> Path | None:
    """
    Return the primary CI workflow file.
    Prefers a file named 'ci.yml' / 'ci.yaml'; falls back to any workflow file.
    """
    candidates = _find_github_workflow_files()
    for name in ("ci.yml", "ci.yaml", "pipeline.yml", "pipeline.yaml"):
        for f in candidates:
            if f.name.lower() == name:
                return f
    return candidates[0] if candidates else None


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------


class TestCIPipelineFilesExist(unittest.TestCase):
    """Verify that at least one CI/CD pipeline configuration file is present."""

    def test_at_least_one_pipeline_config_exists(self):
        """
        The upgrade must introduce a pipeline configuration file.
        Checks all common CI/CD platforms.
        """
        found_any = (
            _GITHUB_WORKFLOW_DIR.is_dir()
            and bool(_find_github_workflow_files())
            or _GITLAB_CI_FILE.exists()
            or _BITBUCKET_PIPELINES_FILE.exists()
            or _CIRCLECI_DIR.is_dir()
            or _JENKINS_FILE.exists()
            or _AZURE_PIPELINES_FILE.exists()
        )
        self.assertTrue(
            found_any,
            msg=(
                "No CI/CD pipeline configuration file was found in the repository. "
                "Expected at least one of: .github/workflows/*.yml, .gitlab-ci.yml, "
                "bitbucket-pipelines.yml, .circleci/config.yml, Jenkinsfile, "
                "azure-pipelines.yml"
            ),
        )

    def test_github_workflows_directory_exists_if_using_github_actions(self):
        """
        If GitHub Actions is the chosen platform, the .github/workflows/ directory
        must exist and contain at least one workflow file.
        """
        if not _GITHUB_WORKFLOW_DIR.exists():
            self.skipTest(
                ".github/workflows/ not present — project may use a different CI platform."
            )
        workflow_files = _find_github_workflow_files()
        self.assertGreater(
            len(workflow_files),
            0,
            msg=".github/workflows/ directory exists but contains no .yml/.yaml files.",
        )

    def test_primary_ci_workflow_file_exists(self):
        """A primary CI workflow file (ci.yml or equivalent) must be present."""
        if not _GITHUB_WORKFLOW_DIR.is_dir():
            self.skipTest("Not using GitHub Actions — skipping workflow file check.")
        ci_file = _find_ci_workflow_file()
        self.assertIsNotNone(
            ci_file,
            msg=(
                "No primary CI workflow file found in .github/workflows/. "
                "Expected a file named ci.yml, ci.yaml, pipeline.yml, or similar."
            ),
        )
        self.assertTrue(
            ci_file.exists(),
            msg=f"CI workflow file path resolved but does not exist: {ci_file}",
        )


class TestCIPipelineStagesDefined(unittest.TestCase):
    """Verify that test, lint, and sast stages/jobs are defined in the pipeline."""

    def setUp(self):
        ci_file = _find_ci_workflow_file()
        if ci_file is None:
            if _GITLAB_CI_FILE.exists():
                self.pipeline_path = _GITLAB_CI_FILE
            elif _AZURE_PIPELINES_FILE.exists():
                self.pipeline_path = _AZURE_PIPELINES_FILE
            else:
                self.skipTest(
                    "No parseable CI pipeline file found — cannot validate stages."
                )
                return
        else:
            self.pipeline_path = ci_file
        self.pipeline = _load_yaml(self.pipeline_path)

    def _get_job_names(self) -> list:
        """
        Extract job/stage names from the pipeline config.
        Handles GitHub Actions (jobs:) and GitLab CI (top-level keys minus reserved).
        """
        # GitHub Actions format
        if "jobs" in self.pipeline and isinstance(self.pipeline["jobs"], dict):
            return list(self.pipeline["jobs"].keys())
        # GitLab CI format — top-level keys that are not reserved keywords
        gitlab_reserved = {
            "stages",
            "variables",
            "include",
            "default",
            "workflow",
            "image",
            "services",
            "before_script",
            "after_script",
            "cache",
        }
        return [k for k in self.pipeline.keys() if k not in gitlab_reserved]

    def _job_names_lower(self) -> list:
        return [name.lower() for name in self._get_job_names()]

    def test_test_stage_is_defined(self):
        """A 'test' job/stage must be present in the pipeline configuration."""
        job_names = self._job_names_lower()
        has_test = any("test" in name for name in job_names)
        self.assertTrue(
            has_test,
            msg=(
                f"No 'test' job/stage found in {self.pipeline_path.name}. "
                f"Defined jobs: {job_names}"
            ),
        )

    def test_lint_stage_is_defined(self):
        """A 'lint' job/stage must be present in the pipeline configuration."""
        job_names = self._job_names_lower()
        has_lint = any("lint" in name for name in job_names)
        self.assertTrue(
            has_lint,
            msg=(
                f"No 'lint' job/stage found in {self.pipeline_path.name}. "
                f"Defined jobs: {job_names}"
            ),
        )

    def test_sast_stage_is_defined(self):
        """A 'sast' job/stage must be present in the pipeline configuration."""
        job_names = self._job_names_lower()
        has_sast = any(
            keyword in name for name in job_names for keyword in ("sast", "security", "scan")
        )
        self.assertTrue(
            has_sast,
            msg=(
                f"No 'sast'/'security'/'scan' job/stage found in {self.pipeline_path.name}. "
                f"Defined jobs: {job_names}. "
                "A SAST stage is required by the upgrade spec."
            ),
        )

    def test_all_three_required_stages_present(self):
        """All three stages — test, lint, sast — must be present simultaneously."""
        job_names = self._job_names_lower()
        has_test = any("test" in n for n in job_names)
        has_lint = any("lint" in n for n in job_names)
        has_sast = any(
            kw in n for n in job_names for kw in ("sast", "security", "scan")
        )
        missing = []
        if not has_test:
            missing.append("test")
        if not has_lint:
            missing.append("lint")
        if not has_sast:
            missing.append("sast/security/scan")
        self.assertEqual(
            missing,
            [],
            msg=(
                f"The following required stages are missing from the pipeline: {missing}. "
                f"All three stages (test, lint, sast) are required by the upgrade spec."
            ),
        )


class TestCIPipelineTriggers(unittest.TestCase):
    """Verify that the pipeline triggers on push and pull_request events."""

    def setUp(self):
        ci_file = _find_ci_workflow_file()
        if ci_file is None:
            self.skipTest("No GitHub Actions CI workflow file found.")
        self.pipeline_path = ci_file
        self.pipeline = _load_yaml(ci_file)

    def test_pipeline_has_on_triggers(self):
        """The workflow must define trigger events via the 'on' key."""
        # GitHub Actions uses 'on' (which PyYAML may parse as True in some versions)
        has_on = "on" in self.pipeline or True in self.pipeline
        self.assertTrue(
            has_on,
            msg=(
                f"No 'on:' trigger block found in {self.pipeline_path.name}. "
                "The pipeline must define when it runs."
            ),
        )

    def _get_triggers(self) -> dict:
        """Return the trigger configuration dict, handling PyYAML 'on'→True quirk."""
        if "on" in self.pipeline:
            return self.pipeline["on"] or {}
        if True in self.pipeline:
            return self.pipeline[True] or {}
        return {}

    def test_push_trigger_is_configured(self):
        """The pipeline must trigger on push events."""
        triggers = self._get_triggers()
        if isinstance(triggers, list):
            has_push = "push" in triggers
        elif isinstance(triggers, dict):
            has_push = "push" in triggers
        else:
            has_push = False
        self.assertTrue(
            has_push,
            msg=(
                f"'push' trigger not found in {self.pipeline_path.name}. "
                "The pipeline must run on every push per the upgrade spec."
            ),
        )

    def test_pull_request_trigger_is_configured(self):
        """The pipeline must trigger on pull_request events."""
        triggers = self._get_triggers()
        if isinstance(triggers, list):
            has_pr = "pull_request" in triggers
        elif isinstance(triggers, dict):
            has_pr = "pull_request" in triggers
        else:
            has_pr = False
        self.assertTrue(
            has_pr,
            msg=(
                f"'pull_request' trigger not found in {self.pipeline_path.name}. "
                "The pipeline must run on pull requests per the upgrade spec."
            ),
        )


class TestCIPipelineJobConfiguration(unittest.TestCase):
    """Verify that each job contains the minimum required configuration."""

    def setUp(self):
        ci_file = _find_ci_workflow_file()
        if ci_file is None:
            self.skipTest("No GitHub Actions CI workflow file found.")
        self.pipeline_path = ci_file
        self.pipeline = _load_yaml(ci_file)
        if "jobs" not in self.pipeline or not isinstance(self.pipeline["jobs"], dict):
            self.skipTest(
                f"{ci_file.name} does not use GitHub Actions 'jobs:' format — "
                "skipping job-level configuration checks."
            )
        self.jobs = self.pipeline["jobs"]

    def _find_job(self, *keywords) -> tuple:
        """Return (job_name, job_dict) for the first job whose name matches any keyword."""
        for name, config in self.jobs.items():
            if any(kw in name.lower() for kw in keywords):
                return name, config or {}
        return None, {}

    def test_test_job_has_runs_on(self):
        """The test job must specify a runner via 'runs-on'."""
        name, job = self._find_job("test")
        if not name:
            self.skipTest("No 'test' job found — covered by stage presence test.")
        self.assertIn(
            "runs-on",
            job,
            msg=f"Job '{name}' is missing 'runs-on' key. A runner must be specified.",
        )

    def test_test_job_has_steps(self):
        """The test job must define at least one step."""
        name, job = self._find_job("test")
        if not name:
            self.skipTest("No 'test' job found — covered by stage presence test.")
        steps = job.get("steps", [])
        self.assertGreater(
            len(steps),
            0,
            msg=f"Job '{name}' has no steps defined. At minimum, a test run step is required.",
        )

    def test_lint_job_has_runs_on(self):
        """The lint job must specify a runner via 'runs-on'."""
        name, job = self._find_job("lint")
        if not name:
            self.skipTest("No 'lint' job found — covered by stage presence test.")
        self.assertIn(
            "runs-on",
            job,
            msg=f"Job '{name}' is missing 'runs-on' key.",
        )

    def test_lint_job_has_steps(self):
        """The lint job must define at least one step."""
        name, job = self._find_job("lint")
        if not name:
            self.skipTest("No 'lint' job found — covered by stage presence test.")
        steps = job.get("steps", [])
        self.assertGreater(
            len(steps),
            0,
            msg=f"Job '{name}' has no steps defined.",
        )

    def test_sast_job_has_runs_on(self):
        """The SAST job must specify a runner via 'runs-on'."""
        name, job = self._find_job("sast", "security", "scan")
        if not name:
            self.skipTest("No SAST job found — covered by stage presence test.")
        self.assertIn(
            "runs-on",
            job,
            msg=f"Job '{name}' is missing 'runs-on' key.",
        )

    def test_sast_job_has_steps(self):
        """The SAST job must define at least one step."""
        name, job = self._find_job("sast", "security", "scan")
        if not name:
            self.skipTest("No SAST job found — covered by stage presence test.")
        steps = job.get("steps", [])
        self.assertGreater(
            len(steps),
            0,
            msg=f"Job '{name}' has no steps defined. A SAST scan step is required.",
        )

    def test_sast_job_uses_a_known_sast_tool(self):
        """
        The SAST job steps must reference a known SAST tool action or command.
        Accepted tools: CodeQL, Semgrep, Snyk, Trivy, Bandit, ESLint security plugin,
        Checkmarx, SonarQube, GitHub Advanced Security.
        """
        name, job = self._find_job("sast", "security", "scan")
        if not name:
            self.skipTest("No SAST job found — covered by stage presence test.")
        steps = job.get("steps", []) or []
        known_sast_indicators = [
            "codeql",
            "semgrep",
            "snyk",
            "trivy",
            "bandit",
            "sonar",
            "checkmarx",
            "advanced-security",
            "security-scan",
            "ghas",
            "anchore",
            "grype",
            "gosec",
            "brakeman",
            "spotbugs",
            "pmd",
        ]
        step_text = str(steps).lower()
        found_tool = any(indicator in step_text for indicator in known_sast_indicators)
        self.assertTrue(
            found_tool,
            msg=(
                f"SAST job '{name}' does not appear to use a recognized SAST tool. "
                f"Steps content: {steps}. "
                f"Expected one of: {known_sast_indicators}"
            ),
        )

    def test_test_job_includes_dependency_install_step(self):
        """
        The test job must include a dependency installation step before running tests.
        Checks for common install commands.
        """
        name, job = self._find_job("test")
        if not name:
            self.skipTest("No 'test' job found.")
        steps = job.get("steps", []) or []
        install_indicators = [
            "npm ci",
            "npm install",
            "pip install",
            "yarn install",
            "mvn",
            "gradle",
            "bundle install",
            "composer install",
            "go mod",
            "cargo build",
            "dotnet restore",
            "apt-get install",
            "apk add",
        ]
        step_text = str(steps).lower()
        has_install = any(indicator in step_text for indicator in install_indicators)
        self.assertTrue(
            has_install,
            msg=(
                f"Test job '{name}' does not appear to install dependencies before running tests. "
                f"Steps: {steps}"
            ),
        )


class TestCISetupNotesDocument(unittest.TestCase):
    """Verify that CI_SETUP_NOTES.md exists as required by the upgrade spec tasks."""

    def test_ci_setup_notes_file_exists(self):
        """
        The upgrade spec requires a CI_SETUP_NOTES.md file at the repo root
        documenting the language, runtime, and build tool decisions.
        """
        notes_file = REPO_ROOT / "CI_SETUP_NOTES.md"
        self.assertTrue(
            notes_file.exists(),
            msg=(
                f"CI_SETUP_NOTES.md not found at {notes_file}. "
                "The upgrade spec requires this file to document the language/runtime/build tool "
                "decisions and locally runnable commands."
            ),
        )

    def test_ci_setup_notes_is_not_empty(self):
        """CI_SETUP_NOTES.md must contain actual content, not be a placeholder stub."""
        notes_file = REPO_ROOT / "CI_SETUP_NOTES.md"
        if not notes_file.exists():
            self.skipTest("CI_SETUP_NOTES.md does not exist — covered by existence test.")
        content = notes_file.read_text(encoding="utf-8").strip()
        self.assertGreater(
            len(content),
            50,
            msg=(
                "CI_SETUP_NOTES.md exists but appears to be empty or a minimal stub. "
                "It must document the language, runtime version, build tool, and runnable commands."
            ),
        )

    def test_ci_setup_notes_documents_language_or_runtime(self):
        """CI_SETUP_NOTES.md must mention the language or runtime being used."""
        notes_file = REPO_ROOT / "CI_SETUP_NOTES.md"
        if not notes_file.exists():
            self.skipTest("CI_SETUP_NOTES.md does not exist.")
        content = notes_file.read_text(encoding="utf-8").lower()
        language_keywords = [
            "python",
            "node",
            "javascript",
            "typescript",
            "java",
            "go",
            "ruby",
            "rust",
            "php",
            "dotnet",
            ".net",
            "c#",
            "kotlin",
            "scala",
            "swift",
            "language",
            "runtime",
        ]
        mentions_language = any(kw in content for kw in language_keywords)
        self.assertTrue(
            mentions_language,
            msg=(
                "CI_SETUP_NOTES.md does not appear to document the language or runtime. "
                "Per the upgrade spec, it must record the confirmed language/runtime version."
            ),
        )


class TestNoPreviousAbsenceOfPipeline(unittest.TestCase):
    """
    Regression guard: verify the repository is no longer in the 'no pipeline' state
    described in the upgrade spec's Current State section.
    """

    def test_pipeline_config_is_not_absent(self):
        """
        The spec states the current state has 'no pipeline definition files present'.
        After the upgrade, at least one must exist.
        """
        pipeline_locations = [
            _GITHUB_WORKFLOW_DIR,
            _GITLAB_CI_FILE,
            _BITBUCKET_PIPELINES_FILE,
            _CIRCLECI_DIR / "config.yml",
            _JENKINS_FILE,
            _AZURE_PIPELINES_FILE,
        ]
        any_exists = any(p.exists() for p in pipeline_locations)
        self.assertTrue(
            any_exists,
            msg=(
                "Repository is still in the pre-upgrade state: no CI/CD pipeline "
                "configuration file exists. The upgrade has not been applied."
            ),
        )

    def test_gitignore_includes_cache_directories(self):
        """
        The upgrade spec requires .gitignore entries for CI cache directories.
        Verify .gitignore exists and contains at least one cache-related entry.
        """
        gitignore = REPO_ROOT / ".gitignore"
        if not gitignore.exists():
            self.skipTest(".gitignore does not exist — cannot validate cache entries.")
        content = gitignore.read_text(encoding="utf-8")
        cache_patterns = [
            ".cache",
            "node_modules",
            "__pycache__",
            "*.pyc",
            ".gradle",
            "target/",
            "dist/",
            "build/",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
        ]
        has_cache_entry = any(pattern in content for pattern in cache_patterns)
        self.assertTrue(
            has_cache_entry,
            msg=(
                ".gitignore exists but does not contain any CI cache directory entries. "
                f"Expected at least one of: {cache_patterns}"
            ),
        )


class TestPipelineVersionPinning(unittest.TestCase):
    """
    Verify that the pipeline pins action versions and runtime versions
    rather than using floating 'latest' references (security best practice).
    """

    def setUp(self):
        ci_file = _find_ci_workflow_file()
        if ci_file is None:
            self.skipTest("No GitHub Actions CI workflow file found.")
        self.pipeline_path = ci_file
        self.pipeline_content = ci_file.read_text(encoding="utf-8")

    def test_pipeline_does_not_use_only_latest_tags(self):
        """
        Actions should be pinned to a specific version (e.g., @v3, @sha) rather
        than @latest, which is a security anti-pattern.
        """
        import re

        latest_pattern = re.compile(r"uses:\s+\S+@latest", re.IGNORECASE)
        matches = latest_pattern.findall(self.pipeline_content)
        self.assertEqual(
            matches,
            [],
            msg=(
                "The pipeline uses '@latest' for one or more actions, which is a security "
                f"anti-pattern. Found: {matches}. Pin actions to a specific version tag or SHA."
            ),
        )

    def test_pipeline_specifies_runner_os(self):
        """
        At least one job must specify a concrete runner OS (ubuntu, windows, macos)
        rather than an unspecified runner.
        """
        runner_keywords = ["ubuntu", "windows", "macos", "self-hosted"]
        content_lower = self.pipeline_content.lower()
        has_runner = any(kw in content_lower for kw in runner_keywords)
        self.assertTrue(
            has_runner,
            msg=(
                "No concrete runner OS found in the pipeline configuration. "
                f"Expected one of: {runner_keywords}"
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)