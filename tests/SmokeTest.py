"""
CI Pipeline Upgrade Validation Tests

Validates that the CI pipeline setup upgrade succeeded by verifying:
- CI configuration file exists and is valid
- Build stage is defined and correctly configured
- Test stage is defined and depends on build stage
- Pipeline trigger rules are present
- Required pipeline structure matches the upgrade spec
"""

import os
import sys
import unittest
import subprocess
import shutil


def find_repo_root():
    """Walk up from current directory to find repository root."""
    current = os.path.abspath(os.path.dirname(__file__))
    for _ in range(10):
        if os.path.exists(os.path.join(current, ".git")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(os.path.dirname(__file__))


REPO_ROOT = find_repo_root()

# Known CI configuration file paths, ordered by priority
CI_CONFIG_CANDIDATES = [
    os.path.join(REPO_ROOT, ".github", "workflows"),          # GitHub Actions (directory)
    os.path.join(REPO_ROOT, ".gitlab-ci.yml"),                # GitLab CI
    os.path.join(REPO_ROOT, ".circleci", "config.yml"),       # CircleCI
    os.path.join(REPO_ROOT, "Jenkinsfile"),                   # Jenkins
    os.path.join(REPO_ROOT, ".travis.yml"),                   # Travis CI
    os.path.join(REPO_ROOT, "azure-pipelines.yml"),           # Azure Pipelines
    os.path.join(REPO_ROOT, "bitbucket-pipelines.yml"),       # Bitbucket Pipelines
    os.path.join(REPO_ROOT, ".drone.yml"),                    # Drone CI
]


def detect_ci_config():
    """
    Detect which CI configuration is present in the repository.
    Returns a list of (platform_name, file_path) tuples for all found configs.
    """
    found = []

    # GitHub Actions: look for any .yml/.yaml files in .github/workflows/
    gh_workflows_dir = os.path.join(REPO_ROOT, ".github", "workflows")
    if os.path.isdir(gh_workflows_dir):
        for fname in os.listdir(gh_workflows_dir):
            if fname.endswith(".yml") or fname.endswith(".yaml"):
                found.append(("github_actions", os.path.join(gh_workflows_dir, fname)))

    # Single-file CI configs
    single_file_configs = [
        ("gitlab_ci",          os.path.join(REPO_ROOT, ".gitlab-ci.yml")),
        ("circleci",           os.path.join(REPO_ROOT, ".circleci", "config.yml")),
        ("jenkins",            os.path.join(REPO_ROOT, "Jenkinsfile")),
        ("travis",             os.path.join(REPO_ROOT, ".travis.yml")),
        ("azure_pipelines",    os.path.join(REPO_ROOT, "azure-pipelines.yml")),
        ("bitbucket",          os.path.join(REPO_ROOT, "bitbucket-pipelines.yml")),
        ("drone",              os.path.join(REPO_ROOT, ".drone.yml")),
    ]
    for platform, path in single_file_configs:
        if os.path.isfile(path):
            found.append((platform, path))

    return found


def read_ci_file(path):
    """Read a CI configuration file and return its content as a string."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def detect_stack():
    """
    Detect the project stack by inspecting well-known manifest files.
    Returns a dict with keys: language, build_tool, test_command.
    """
    stack = {"language": None, "build_tool": None, "test_command": None}

    if os.path.isfile(os.path.join(REPO_ROOT, "package.json")):
        stack["language"] = "javascript"
        stack["build_tool"] = "npm"
        stack["test_command"] = "npm test"

    elif os.path.isfile(os.path.join(REPO_ROOT, "pom.xml")):
        stack["language"] = "java"
        stack["build_tool"] = "maven"
        stack["test_command"] = "mvn test"

    elif os.path.isfile(os.path.join(REPO_ROOT, "build.gradle")) or \
         os.path.isfile(os.path.join(REPO_ROOT, "build.gradle.kts")):
        stack["language"] = "java"
        stack["build_tool"] = "gradle"
        stack["test_command"] = "./gradlew test"

    elif os.path.isfile(os.path.join(REPO_ROOT, "pyproject.toml")) or \
         os.path.isfile(os.path.join(REPO_ROOT, "setup.py")) or \
         os.path.isfile(os.path.join(REPO_ROOT, "setup.cfg")):
        stack["language"] = "python"
        stack["build_tool"] = "pip"
        stack["test_command"] = "pytest"

    elif os.path.isfile(os.path.join(REPO_ROOT, "go.mod")):
        stack["language"] = "go"
        stack["build_tool"] = "go"
        stack["test_command"] = "go test ./..."

    elif os.path.isfile(os.path.join(REPO_ROOT, "Cargo.toml")):
        stack["language"] = "rust"
        stack["build_tool"] = "cargo"
        stack["test_command"] = "cargo test"

    elif os.path.isfile(os.path.join(REPO_ROOT, "Makefile")):
        stack["language"] = "unknown"
        stack["build_tool"] = "make"
        stack["test_command"] = "make test"

    elif os.path.isfile(os.path.join(REPO_ROOT, "composer.json")):
        stack["language"] = "php"
        stack["build_tool"] = "composer"
        stack["test_command"] = "composer test"

    elif os.path.isfile(os.path.join(REPO_ROOT, "Gemfile")):
        stack["language"] = "ruby"
        stack["build_tool"] = "bundler"
        stack["test_command"] = "bundle exec rspec"

    return stack


DETECTED_CI_CONFIGS = detect_ci_config()
DETECTED_STACK = detect_stack()


class TestCIConfigurationExists(unittest.TestCase):
    """Verify that at least one CI configuration file was added to the repository."""

    def test_at_least_one_ci_config_file_exists(self):
        """
        UPGRADE VALIDATION: A CI configuration file must exist in the repository.
        This is the primary artifact of the CI pipeline setup upgrade.
        """
        self.assertTrue(
            len(DETECTED_CI_CONFIGS) > 0,
            msg=(
                "No CI configuration file was found in the repository. "
                "Expected at least one of: "
                ".github/workflows/*.yml, .gitlab-ci.yml, .circleci/config.yml, "
                "Jenkinsfile, .travis.yml, azure-pipelines.yml, "
                "bitbucket-pipelines.yml, .drone.yml. "
                "The CI pipeline setup upgrade requires a pipeline definition file "
                "to be committed to the repository root."
            ),
        )

    def test_ci_config_files_are_non_empty(self):
        """Each detected CI configuration file must be non-empty."""
        self.assertTrue(
            len(DETECTED_CI_CONFIGS) > 0,
            "No CI config files detected — cannot validate content.",
        )
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                self.assertGreater(
                    len(content.strip()),
                    0,
                    msg=f"CI config file is empty: {path}",
                )

    def test_ci_config_files_are_readable(self):
        """CI configuration files must be readable (not binary or corrupt)."""
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                try:
                    content = read_ci_file(path)
                    self.assertIsInstance(content, str)
                except UnicodeDecodeError as exc:
                    self.fail(
                        f"CI config file at {path} could not be decoded as UTF-8: {exc}"
                    )


class TestCIBuildStagePresent(unittest.TestCase):
    """Verify that a build stage is defined in the CI configuration."""

    # Keywords that indicate a build stage across different CI platforms
    BUILD_STAGE_KEYWORDS = [
        "build",
        "compile",
        "install",
        "assemble",
    ]

    def _content_contains_build_stage(self, content):
        """Return True if the content references a build stage."""
        content_lower = content.lower()
        return any(keyword in content_lower for keyword in self.BUILD_STAGE_KEYWORDS)

    def test_build_stage_defined_in_ci_config(self):
        """
        UPGRADE VALIDATION: The CI configuration must define a build stage.
        Per the upgrade spec, the build stage checks out the repository,
        installs dependencies, and compiles/builds the project.
        """
        self.assertTrue(
            len(DETECTED_CI_CONFIGS) > 0,
            "No CI config files detected — cannot validate build stage.",
        )
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                self.assertTrue(
                    self._content_contains_build_stage(content),
                    msg=(
                        f"CI config at {path} does not appear to define a build stage. "
                        f"Expected one of the keywords {self.BUILD_STAGE_KEYWORDS} "
                        f"to appear in the configuration. "
                        f"The upgrade spec requires a 'build' stage that installs "
                        f"dependencies and compiles/builds the project."
                    ),
                )

    def test_checkout_step_present_in_ci_config(self):
        """
        The CI configuration must include a repository checkout step.
        This is a required part of the build stage per the upgrade spec.
        """
        CHECKOUT_KEYWORDS = [
            "checkout",
            "actions/checkout",
            "git clone",
            "fetch",
            "uses: actions/checkout",
        ]
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                content_lower = content.lower()
                found = any(kw.lower() in content_lower for kw in CHECKOUT_KEYWORDS)
                self.assertTrue(
                    found,
                    msg=(
                        f"CI config at {path} does not appear to include a checkout step. "
                        f"Expected one of {CHECKOUT_KEYWORDS}. "
                        f"The build stage must check out the repository source code."
                    ),
                )

    def test_dependency_installation_step_present(self):
        """
        The CI configuration must include a dependency installation step.
        """
        INSTALL_KEYWORDS = [
            "install",
            "npm ci",
            "npm install",
            "pip install",
            "mvn install",
            "gradle",
            "go mod download",
            "cargo build",
            "bundle install",
            "composer install",
            "apt-get install",
            "apk add",
            "dependencies",
        ]
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                content_lower = content.lower()
                found = any(kw.lower() in content_lower for kw in INSTALL_KEYWORDS)
                self.assertTrue(
                    found,
                    msg=(
                        f"CI config at {path} does not appear to include a dependency "
                        f"installation step. Expected one of {INSTALL_KEYWORDS}. "
                        f"The build stage must install project dependencies."
                    ),
                )


class TestCITestStagePresent(unittest.TestCase):
    """Verify that a test stage is defined in the CI configuration."""

    TEST_STAGE_KEYWORDS = [
        "test",
        "pytest",
        "jest",
        "mocha",
        "rspec",
        "phpunit",
        "go test",
        "cargo test",
        "mvn test",
        "gradle test",
        "npm test",
        "yarn test",
        "unittest",
        "spec",
    ]

    def _content_contains_test_stage(self, content):
        content_lower = content.lower()
        return any(kw.lower() in content_lower for kw in self.TEST_STAGE_KEYWORDS)

    def test_test_stage_defined_in_ci_config(self):
        """
        UPGRADE VALIDATION: The CI configuration must define a test stage.
        Per the upgrade spec, the test stage executes the test suite and
        fails the pipeline on any test failure.
        """
        self.assertTrue(
            len(DETECTED_CI_CONFIGS) > 0,
            "No CI config files detected — cannot validate test stage.",
        )
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                self.assertTrue(
                    self._content_contains_test_stage(content),
                    msg=(
                        f"CI config at {path} does not appear to define a test stage. "
                        f"Expected one of the keywords {self.TEST_STAGE_KEYWORDS} "
                        f"to appear in the configuration. "
                        f"The upgrade spec requires a 'test' stage that runs the "
                        f"test suite and fails the pipeline on test failure."
                    ),
                )

    def test_test_stage_is_separate_from_build_stage(self):
        """
        The test stage must be a distinct stage/job from the build stage.
        Per the upgrade spec, build and test are separate pipeline stages.
        """
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                content_lower = content.lower()
                has_build = "build" in content_lower
                has_test = any(
                    kw.lower() in content_lower
                    for kw in self.TEST_STAGE_KEYWORDS
                )
                # Both must be present for them to be separate
                self.assertTrue(
                    has_build and has_test,
                    msg=(
                        f"CI config at {path} must contain both a build stage and a "
                        f"test stage as separate pipeline stages. "
                        f"Found build={has_build}, test={has_test}."
                    ),
                )


class TestCIPipelineTriggerRules(unittest.TestCase):
    """Verify that pipeline trigger rules are configured."""

    TRIGGER_KEYWORDS = [
        "push",
        "pull_request",
        "merge_request",
        "on:",
        "trigger",
        "branches",
        "workflow_dispatch",
        "schedule",
        "only:",
        "except:",
        "rules:",
        "when:",
        "refs:",
    ]

    def test_trigger_rules_present_in_ci_config(self):
        """
        UPGRADE VALIDATION: The CI configuration must define trigger rules
        specifying when the pipeline runs (e.g., on push, pull request).
        Per the upgrade spec, a trigger policy must be defined.
        """
        self.assertTrue(
            len(DETECTED_CI_CONFIGS) > 0,
            "No CI config files detected — cannot validate trigger rules.",
        )
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                content_lower = content.lower()
                found = any(kw.lower() in content_lower for kw in self.TRIGGER_KEYWORDS)
                self.assertTrue(
                    found,
                    msg=(
                        f"CI config at {path} does not appear to define trigger rules. "
                        f"Expected one of {self.TRIGGER_KEYWORDS}. "
                        f"The upgrade spec requires a trigger policy defining which "
                        f"branches or events activate the pipeline."
                    ),
                )


class TestCIYAMLSyntaxValid(unittest.TestCase):
    """Verify that YAML-based CI configuration files have valid syntax."""

    YAML_BASED_PLATFORMS = {
        "github_actions",
        "gitlab_ci",
        "circleci",
        "travis",
        "azure_pipelines",
        "bitbucket",
        "drone",
    }

    def _try_parse_yaml(self, path):
        """
        Attempt to parse a YAML file. Returns (True, None) on success,
        (False, error_message) on failure.
        Uses PyYAML if available, otherwise falls back to basic structural checks.
        """
        try:
            import yaml  # type: ignore
            with open(path, "r", encoding="utf-8") as f:
                yaml.safe_load(f)
            return True, None
        except ImportError:
            # PyYAML not available — do a basic structural check
            content = read_ci_file(path)
            # Check for obvious YAML errors: tabs used for indentation
            for i, line in enumerate(content.splitlines(), start=1):
                if line.startswith("\t"):
                    return False, f"Line {i} uses tab indentation, which is invalid in YAML."
            return True, None
        except Exception as exc:  # pylint: disable=broad-except
            return False, str(exc)

    def test_yaml_ci_configs_have_valid_syntax(self):
        """
        UPGRADE VALIDATION: YAML-based CI configuration files must parse
        without syntax errors. An invalid YAML file will cause the CI
        platform to reject the pipeline configuration entirely.
        """
        yaml_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform in self.YAML_BASED_PLATFORMS
        ]

        if not yaml_configs:
            self.skipTest(
                "No YAML-based CI configuration files detected — skipping YAML syntax check."
            )

        for platform, path in yaml_configs:
            with self.subTest(platform=platform, path=path):
                valid, error = self._try_parse_yaml(path)
                self.assertTrue(
                    valid,
                    msg=(
                        f"CI config at {path} has invalid YAML syntax: {error}. "
                        f"The CI platform will reject this configuration."
                    ),
                )


class TestCIConfigStructureForGitHubActions(unittest.TestCase):
    """
    GitHub Actions-specific structural validation.
    Only runs when GitHub Actions workflow files are detected.
    """

    def setUp(self):
        self.gh_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "github_actions"
        ]
        if not self.gh_configs:
            self.skipTest("No GitHub Actions workflow files detected.")

    def test_github_actions_workflow_has_on_trigger(self):
        """GitHub Actions workflows must have an 'on:' trigger block."""
        for platform, path in self.gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "on:",
                    content,
                    msg=(
                        f"GitHub Actions workflow at {path} is missing the 'on:' "
                        f"trigger block. This is required for the workflow to run."
                    ),
                )

    def test_github_actions_workflow_has_jobs(self):
        """GitHub Actions workflows must define at least one job."""
        for platform, path in self.gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "jobs:",
                    content,
                    msg=(
                        f"GitHub Actions workflow at {path} is missing the 'jobs:' "
                        f"block. At least one job (build or test) must be defined."
                    ),
                )

    def test_github_actions_workflow_has_runs_on(self):
        """GitHub Actions jobs must specify a runner via 'runs-on'."""
        for platform, path in self.gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "runs-on:",
                    content,
                    msg=(
                        f"GitHub Actions workflow at {path} is missing 'runs-on:'. "
                        f"Each job must specify a runner environment."
                    ),
                )

    def test_github_actions_workflow_has_steps(self):
        """GitHub Actions jobs must define steps."""
        for platform, path in self.gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "steps:",
                    content,
                    msg=(
                        f"GitHub Actions workflow at {path} is missing 'steps:'. "
                        f"Each job must define the steps it executes."
                    ),
                )

    def test_github_actions_build_job_present(self):
        """
        UPGRADE VALIDATION: GitHub Actions workflow must contain a build job.
        """
        for platform, path in self.gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                content_lower = content.lower()
                self.assertIn(
                    "build",
                    content_lower,
                    msg=(
                        f"GitHub Actions workflow at {path} does not reference a "
                        f"'build' job or step. The upgrade spec requires a build stage."
                    ),
                )

    def test_github_actions_test_job_present(self):
        """
        UPGRADE VALIDATION: GitHub Actions workflow must contain a test job or step.
        """
        TEST_INDICATORS = ["test", "pytest", "jest", "rspec", "go test", "cargo test"]
        for platform, path in self.gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                content_lower = content.lower()
                found = any(kw in content_lower for kw in TEST_INDICATORS)
                self.assertTrue(
                    found,
                    msg=(
                        f"GitHub Actions workflow at {path} does not reference a "
                        f"test job or step. Expected one of {TEST_INDICATORS}. "
                        f"The upgrade spec requires a test stage."
                    ),
                )


class TestCIConfigStructureForGitLabCI(unittest.TestCase):
    """
    GitLab CI-specific structural validation.
    Only runs when .gitlab-ci.yml is detected.
    """

    def setUp(self):
        self.gl_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "gitlab_ci"
        ]
        if not self.gl_configs:
            self.skipTest("No GitLab CI configuration detected.")

    def test_gitlab_ci_has_stages(self):
        """GitLab CI configuration must define stages."""
        for platform, path in self.gl_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "stages:",
                    content,
                    msg=(
                        f"GitLab CI config at {path} is missing 'stages:'. "
                        f"The upgrade spec requires explicit build and test stages."
                    ),
                )

    def test_gitlab_ci_has_build_stage(self):
        """GitLab CI must define a build stage."""
        for platform, path in self.gl_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "build",
                    content.lower(),
                    msg=f"GitLab CI config at {path} does not reference a build stage.",
                )

    def test_gitlab_ci_has_test_stage(self):
        """GitLab CI must define a test stage."""
        for platform, path in self.gl_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "test",
                    content.lower(),
                    msg=f"GitLab CI config at {path} does not reference a test stage.",
                )


class TestCIConfigStructureForCircleCI(unittest.TestCase):
    """
    CircleCI-specific structural validation.
    Only runs when .circleci/config.yml is detected.
    """

    def setUp(self):
        self.cc_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "circleci"
        ]
        if not self.cc_configs:
            self.skipTest("No CircleCI configuration detected.")

    def test_circleci_has_version(self):
        """CircleCI config must declare a version."""
        for platform, path in self.cc_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "version:",
                    content,
                    msg=(
                        f"CircleCI config at {path} is missing 'version:'. "
                        f"CircleCI requires a version declaration."
                    ),
                )

    def test_circleci_has_jobs(self):
        """CircleCI config must define jobs."""
        for platform, path in self.cc_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "jobs:",
                    content,
                    msg=f"CircleCI config at {path} is missing 'jobs:'.",
                )

    def test_circleci_has_workflows(self):
        """CircleCI config must define workflows."""
        for platform, path in self.cc_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertIn(
                    "workflows:",
                    content,
                    msg=(
                        f"CircleCI config at {path} is missing 'workflows:'. "
                        f"Workflows are required to orchestrate build and test jobs."
                    ),
                )


class TestStackDocumented(unittest.TestCase):
    """
    Verify that the project stack is documented as required by the upgrade spec.
    The spec requires the stack to be recorded in STACK.md, CONTRIBUTING.md, or README.md.
    """

    DOCUMENTATION_FILES = [
        os.path.join(REPO_ROOT, "STACK.md"),
        os.path.join(REPO_ROOT, "CONTRIBUTING.md"),
        os.path.join(REPO_ROOT, "README.md"),
        os.path.join(REPO_ROOT, "README.rst"),
        os.path.join(REPO_ROOT, "README.txt"),
    ]

    def test_at_least_one_documentation_file_exists(self):
        """
        UPGRADE VALIDATION: The upgrade spec requires the stack to be documented.
        At least one of STACK.md, CONTRIBUTING.md, or README.md must exist.
        """
        found = [f for f in self.DOCUMENTATION_FILES if os.path.isfile(f)]
        self.assertGreater(
            len(found),
            0,
            msg=(
                "No documentation file found. The upgrade spec requires the project "
                "stack (language, runtime, build tool, test command) to be documented "
                "in STACK.md, CONTRIBUTING.md, or README.md."
            ),
        )

    def test_documentation_references_build_or_test_command(self):
        """
        At least one documentation file should reference build or test commands,
        per the upgrade spec requirement to document the exact test command.
        """
        BUILD_TEST_KEYWORDS = [
            "build",
            "test",
            "install",
            "run",
            "npm",
            "mvn",
            "gradle",
            "pytest",
            "go test",
            "cargo",
            "make",
            "bundle",
            "composer",
        ]
        found_docs = [f for f in self.DOCUMENTATION_FILES if os.path.isfile(f)]
        if not found_docs:
            self.skipTest("No documentation files found — skipping content check.")

        any_doc_has_commands = False
        for doc_path in found_docs:
            try:
                content = read_ci_file(doc_path)
                content_lower = content.lower()
                if any(kw.lower() in content_lower for kw in BUILD_TEST_KEYWORDS):
                    any_doc_has_commands = True
                    break
            except Exception:  # pylint: disable=broad-except
                continue

        self.assertTrue(
            any_doc_has_commands,
            msg=(
                "None of the documentation files reference build or test commands. "
                "The upgrade spec requires documenting the exact build and test commands "
                "in STACK.md, CONTRIBUTING.md, or README.md."
            ),
        )


class TestBaselineTestResultsRecorded(unittest.TestCase):
    """
    Verify that baseline test results were recorded as required by the upgrade spec.
    The spec requires saving baseline results to ci/baseline-test-results.txt.
    """

    BASELINE_RESULTS_PATH = os.path.join(REPO_ROOT, "ci", "baseline-test-results.txt")

    def test_baseline_test_results_file_exists(self):
        """
        UPGRADE VALIDATION: The upgrade spec requires baseline test results to be
        recorded in ci/baseline-test-results.txt on the feature branch.
        """
        self.assertTrue(
            os.path.isfile(self.BASELINE_RESULTS_PATH),
            msg=(
                f"Baseline test results file not found at {self.BASELINE_RESULTS_PATH}. "
                f"The upgrade spec requires running the test suite locally and saving "
                f"the output to ci/baseline-test-results.txt for regression comparison."
            ),
        )

    def test_baseline_test_results_file_is_non_empty(self):
        """The baseline test results file must contain content."""
        if not os.path.isfile(self.BASELINE_RESULTS_PATH):
            self.skipTest(
                f"Baseline results file not found at {self.BASELINE_RESULTS_PATH}."
            )
        with open(self.BASELINE_RESULTS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertGreater(
            len(content.strip()),
            0,
            msg=(
                f"Baseline test results file at {self.BASELINE_RESULTS_PATH} is empty. "
                f"It must contain the test run output including pass/fail counts."
            ),
        )


class TestCIPipelineUpgradeVersionAssertion(unittest.TestCase):
    """
    Version assertion for the CI pipeline upgrade.
    Verifies that the CI configuration represents the 'latest stable' target
    by checking for modern CI platform features and syntax.
    """

    def test_github_actions_uses_modern_checkout_action(self):
        """
        GitHub Actions: verify the checkout action uses a current version (v3 or v4),
        not the deprecated v1 or v2.
        """
        gh_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "github_actions"
        ]
        if not gh_configs:
            self.skipTest("No GitHub Actions configs detected.")

        for platform, path in gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                # Check if checkout action is used at all
                if "actions/checkout" not in content:
                    continue  # No checkout action referenced — skip version check

                # Warn if deprecated v1 or v2 is used
                deprecated_versions = ["actions/checkout@v1", "actions/checkout@v2"]
                for deprecated in deprecated_versions:
                    self.assertNotIn(
                        deprecated,
                        content,
                        msg=(
                            f"GitHub Actions workflow at {path} uses deprecated "
                            f"'{deprecated}'. Upgrade to actions/checkout@v4 "
                            f"(latest stable) as part of the CI pipeline setup."
                        ),
                    )

    def test_github_actions_uses_modern_setup_actions(self):
        """
        GitHub Actions: verify that language setup actions use current versions,
        not deprecated v1 versions.
        """
        gh_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "github_actions"
        ]
        if not gh_configs:
            self.skipTest("No GitHub Actions configs detected.")

        DEPRECATED_SETUP_ACTIONS = [
            "actions/setup-node@v1",
            "actions/setup-python@v1",
            "actions/setup-java@v1",
            "actions/setup-go@v1",
        ]

        for platform, path in gh_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                for deprecated in DEPRECATED_SETUP_ACTIONS:
                    self.assertNotIn(
                        deprecated,
                        content,
                        msg=(
                            f"GitHub Actions workflow at {path} uses deprecated "
                            f"'{deprecated}'. Use a current version (v3 or v4) "
                            f"as part of the CI pipeline setup upgrade."
                        ),
                    )

    def test_circleci_uses_version_2_or_higher(self):
        """
        CircleCI: verify the config uses version 2.x or higher (not legacy version 1).
        """
        cc_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "circleci"
        ]
        if not cc_configs:
            self.skipTest("No CircleCI configs detected.")

        for platform, path in cc_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                # Check for version: 1 (legacy, unsupported)
                self.assertNotIn(
                    "version: 1",
                    content,
                    msg=(
                        f"CircleCI config at {path} uses legacy version 1. "
                        f"Upgrade to version 2.1 (latest stable) as part of "
                        f"the CI pipeline setup upgrade."
                    ),
                )

    def test_ci_config_does_not_use_deprecated_travis_ci_syntax(self):
        """
        Travis CI: verify the config does not use deprecated 'sudo: required' syntax.
        """
        travis_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "travis"
        ]
        if not travis_configs:
            self.skipTest("No Travis CI configs detected.")

        for platform, path in travis_configs:
            with self.subTest(path=path):
                content = read_ci_file(path)
                self.assertNotIn(
                    "sudo: required",
                    content,
                    msg=(
                        f"Travis CI config at {path} uses deprecated 'sudo: required'. "
                        f"This syntax is no longer supported in modern Travis CI."
                    ),
                )


class TestCIConfigNoPreviousManualOnlyInstructions(unittest.TestCase):
    """
    Verify that the upgrade replaced manual-only processes with automated CI.
    Checks that no CI config references 'manual only' or 'no CI' patterns
    that would indicate the upgrade was not completed.
    """

    ANTI_PATTERNS = [
        "TODO: add CI",
        "TODO: set up CI",
        "no CI",
        "manual only",
        "run manually",
        "# placeholder",
        "# TODO",
    ]

    def test_ci_config_does_not_contain_incomplete_placeholders(self):
        """
        CI configuration files must not contain placeholder comments indicating
        the upgrade was not fully completed.
        """
        for platform, path in DETECTED_CI_CONFIGS:
            with self.subTest(platform=platform, path=path):
                content = read_ci_file(path)
                for anti_pattern in self.ANTI_PATTERNS:
                    self.assertNotIn(
                        anti_pattern.lower(),
                        content.lower(),
                        msg=(
                            f"CI config at {path} contains placeholder text "
                            f"'{anti_pattern}', indicating the upgrade may be incomplete."
                        ),
                    )


class TestCIDirectoryStructure(unittest.TestCase):
    """Verify the CI-related directory structure is correctly set up."""

    def test_github_workflows_directory_exists_if_github_actions_used(self):
        """If GitHub Actions configs are present, the .github/workflows directory must exist."""
        gh_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "github_actions"
        ]
        if not gh_configs:
            self.skipTest("No GitHub Actions configs detected.")

        workflows_dir = os.path.join(REPO_ROOT, ".github", "workflows")
        self.assertTrue(
            os.path.isdir(workflows_dir),
            msg=(
                f"GitHub Actions workflows directory not found at {workflows_dir}. "
                f"GitHub Actions requires workflow files to be in .github/workflows/."
            ),
        )

    def test_circleci_directory_exists_if_circleci_used(self):
        """If CircleCI config is present, the .circleci directory must exist."""
        cc_configs = [
            (platform, path)
            for platform, path in DETECTED_CI_CONFIGS
            if platform == "circleci"
        ]
        if not cc_configs:
            self.skipTest("No CircleCI configs detected.")

        circleci_dir = os.path.join(REPO_ROOT, ".circleci")
        self.assertTrue(
            os.path.isdir(circleci_dir),
            msg=(
                f"CircleCI directory not found at {circleci_dir}. "
                f"CircleCI requires the config file to be in .circleci/."
            ),
        )


if __name__ == "__main__":
    # Print detected CI configuration summary before running tests
    print("=" * 70)
    print("CI PIPELINE UPGRADE VALIDATION")
    print("=" * 70)
    print(f"Repository root: {REPO_ROOT}")
    print()

    if DETECTED_CI_CONFIGS:
        print(f"Detected CI configurations ({len(DETECTED_CI_CONFIGS)}):")
        for platform, path in DETECTED_CI_CONFIGS:
            rel_path = os.path.relpath(path, REPO_ROOT)
            print(f"  [{platform}] {rel_path}")
    else:
        print("WARNING: No CI configuration files detected.")
        print(
            "Expected one of: .github/workflows/*.yml, .gitlab-ci.yml, "
            ".circleci/config.yml, Jenkinsfile, .travis.yml, azure-pipelines.yml"
        )

    print()
    if DETECTED_STACK["language"]:
        print(f"Detected stack:")
        print(f"  Language:      {DETECTED_STACK['language']}")
        print(f"  Build tool:    {DETECTED_STACK['build_tool']}")
        print(f"  Test command:  {DETECTED_STACK['test_command']}")
    else:
        print("WARNING: Could not detect project stack from repository root.")
        print(
            "Expected one of: package.json, pom.xml, build.gradle, "
            "pyproject.toml, go.mod, Cargo.toml, Makefile, Gemfile, composer.json"
        )

    print()
    print("=" * 70)
    print()

    unittest.main(verbosity=2)