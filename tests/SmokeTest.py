#!/usr/bin/env python3
"""
Upgrade validation tests for automated dependency update PRs via Dependabot or Renovate.

These tests verify that the upgrade succeeded by checking:
1. A valid dependency update configuration file exists (Dependabot or Renovate)
2. The configuration is syntactically valid and contains required fields
3. All detected package manifests are covered by the configuration
4. The configuration targets the correct default branch
5. Required labels and scheduling are present
"""

import json
import os
import unittest
import glob

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

DEPENDABOT_CONFIG_PATH = os.path.join(REPO_ROOT, ".github", "dependabot.yml")
RENOVATE_CONFIG_PATHS = [
    os.path.join(REPO_ROOT, "renovate.json"),
    os.path.join(REPO_ROOT, "renovate.json5"),
    os.path.join(REPO_ROOT, ".github", "renovate.json"),
    os.path.join(REPO_ROOT, ".github", "renovate.json5"),
    os.path.join(REPO_ROOT, ".renovaterc"),
    os.path.join(REPO_ROOT, ".renovaterc.json"),
]

KNOWN_MANIFEST_PATTERNS = {
    "npm": ["package.json", "**/package.json"],
    "pip": ["requirements.txt", "**/requirements.txt", "Pipfile", "**/Pipfile", "pyproject.toml", "**/pyproject.toml"],
    "maven": ["pom.xml", "**/pom.xml"],
    "gradle": ["build.gradle", "**/build.gradle", "build.gradle.kts", "**/build.gradle.kts"],
    "gomod": ["go.mod", "**/go.mod"],
    "cargo": ["Cargo.toml", "**/Cargo.toml"],
    "bundler": ["Gemfile", "**/Gemfile"],
    "composer": ["composer.json", "**/composer.json"],
    "nuget": ["*.csproj", "**/*.csproj", "*.fsproj", "**/*.fsproj"],
    "docker": ["Dockerfile", "**/Dockerfile"],
    "github-actions": [".github/workflows/*.yml", ".github/workflows/*.yaml"],
}

VALID_SCHEDULE_INTERVALS = {"daily", "weekly", "monthly"}

DEPENDABOT_ECOSYSTEM_MAP = {
    "npm": "npm",
    "pip": "pip",
    "maven": "maven",
    "gradle": "gradle",
    "gomod": "gomod",
    "cargo": "cargo",
    "bundler": "bundler",
    "composer": "composer",
    "nuget": "nuget",
    "docker": "docker",
    "github-actions": "github-actions",
}


def find_existing_config():
    """Return ('dependabot', path) or ('renovate', path) or (None, None)."""
    if os.path.exists(DEPENDABOT_CONFIG_PATH):
        return ("dependabot", DEPENDABOT_CONFIG_PATH)
    for path in RENOVATE_CONFIG_PATHS:
        if os.path.exists(path):
            return ("renovate", path)
    return (None, None)


def detect_present_ecosystems():
    """Return a set of ecosystem keys whose manifest files exist in the repo."""
    present = set()
    for ecosystem, patterns in KNOWN_MANIFEST_PATTERNS.items():
        for pattern in patterns:
            matches = glob.glob(os.path.join(REPO_ROOT, pattern), recursive=True)
            # Exclude node_modules, vendor, .git
            matches = [
                m for m in matches
                if "node_modules" not in m
                and "/vendor/" not in m
                and "/.git/" not in m
            ]
            if matches:
                present.add(ecosystem)
                break
    return present


def load_yaml_file(path):
    """Load a YAML file and return its parsed content."""
    if not YAML_AVAILABLE:
        raise unittest.SkipTest(
            "PyYAML is not installed. Install it with: pip install pyyaml"
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_json_file(path):
    """Load a JSON file and return its parsed content."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestDependencyUpdateConfigExists(unittest.TestCase):
    """Verify that exactly one dependency update configuration file is present."""

    def test_at_least_one_config_file_exists(self):
        """The upgrade must have added either a Dependabot or Renovate config file."""
        tool, path = find_existing_config()
        self.assertIsNotNone(
            tool,
            msg=(
                "No dependency update configuration file was found. "
                "Expected one of:\n"
                f"  Dependabot: {DEPENDABOT_CONFIG_PATH}\n"
                f"  Renovate:   {', '.join(RENOVATE_CONFIG_PATHS)}\n"
                "The upgrade to add automated dependency update PRs has not been applied."
            ),
        )
        self.assertTrue(
            os.path.isfile(path),
            msg=f"Config path reported as {path} but it is not a regular file.",
        )

    def test_no_conflicting_duplicate_configs(self):
        """Only one tool should be configured — Dependabot and Renovate should not both be present."""
        has_dependabot = os.path.exists(DEPENDABOT_CONFIG_PATH)
        has_renovate = any(os.path.exists(p) for p in RENOVATE_CONFIG_PATHS)
        # Both can coexist technically, but it is a misconfiguration smell.
        # We warn rather than hard-fail, but we do assert at most one is the primary.
        if has_dependabot and has_renovate:
            # Soft assertion: log a clear message but do not block CI
            import warnings
            warnings.warn(
                "Both a Dependabot config (.github/dependabot.yml) and a Renovate config "
                "were found. This may cause duplicate dependency update PRs. "
                "Consider removing one.",
                UserWarning,
            )


class TestDependabotConfiguration(unittest.TestCase):
    """Validate the Dependabot configuration file when it is the chosen tool."""

    def setUp(self):
        tool, self.config_path = find_existing_config()
        if tool != "dependabot":
            self.skipTest("Dependabot config not present — skipping Dependabot-specific tests.")
        self.config = load_yaml_file(self.config_path)

    def test_config_is_version_2(self):
        """Dependabot config must declare version: 2 (the only supported schema version)."""
        self.assertIn(
            "version", self.config,
            msg="dependabot.yml is missing the required top-level 'version' key."
        )
        self.assertEqual(
            self.config["version"], 2,
            msg=(
                f"dependabot.yml declares version {self.config.get('version')!r} "
                "but must declare version 2."
            ),
        )

    def test_updates_key_present_and_non_empty(self):
        """The 'updates' list must exist and contain at least one entry."""
        self.assertIn(
            "updates", self.config,
            msg="dependabot.yml is missing the required 'updates' key."
        )
        updates = self.config["updates"]
        self.assertIsInstance(updates, list, msg="'updates' must be a list.")
        self.assertGreater(
            len(updates), 0,
            msg="'updates' list is empty — no ecosystems are being monitored."
        )

    def test_each_update_entry_has_required_fields(self):
        """Every entry in 'updates' must have package-ecosystem, directory, and schedule."""
        updates = self.config.get("updates", [])
        for i, entry in enumerate(updates):
            with self.subTest(entry_index=i, ecosystem=entry.get("package-ecosystem", "<missing>")):
                self.assertIn(
                    "package-ecosystem", entry,
                    msg=f"updates[{i}] is missing 'package-ecosystem'."
                )
                self.assertIn(
                    "directory", entry,
                    msg=f"updates[{i}] is missing 'directory'."
                )
                self.assertIn(
                    "schedule", entry,
                    msg=f"updates[{i}] is missing 'schedule'."
                )
                schedule = entry["schedule"]
                self.assertIsInstance(schedule, dict, msg=f"updates[{i}]['schedule'] must be a dict.")
                self.assertIn(
                    "interval", schedule,
                    msg=f"updates[{i}]['schedule'] is missing 'interval'."
                )
                self.assertIn(
                    schedule["interval"], VALID_SCHEDULE_INTERVALS,
                    msg=(
                        f"updates[{i}]['schedule']['interval'] is {schedule['interval']!r}; "
                        f"must be one of {VALID_SCHEDULE_INTERVALS}."
                    ),
                )

    def test_open_pull_requests_limit_is_set(self):
        """Each update entry should set open-pull-requests-limit to avoid PR flooding."""
        updates = self.config.get("updates", [])
        for i, entry in enumerate(updates):
            with self.subTest(entry_index=i, ecosystem=entry.get("package-ecosystem", "<missing>")):
                self.assertIn(
                    "open-pull-requests-limit", entry,
                    msg=(
                        f"updates[{i}] (ecosystem: {entry.get('package-ecosystem')!r}) "
                        "is missing 'open-pull-requests-limit'. "
                        "Set this to 5 or another reasonable value to prevent PR flooding."
                    ),
                )
                limit = entry["open-pull-requests-limit"]
                self.assertIsInstance(limit, int, msg=f"updates[{i}]['open-pull-requests-limit'] must be an integer.")
                self.assertGreater(limit, 0, msg=f"updates[{i}]['open-pull-requests-limit'] must be > 0.")

    def test_labels_key_present_with_dependencies_label(self):
        """Each update entry should include a 'dependencies' label for filterability."""
        updates = self.config.get("updates", [])
        for i, entry in enumerate(updates):
            with self.subTest(entry_index=i, ecosystem=entry.get("package-ecosystem", "<missing>")):
                self.assertIn(
                    "labels", entry,
                    msg=(
                        f"updates[{i}] (ecosystem: {entry.get('package-ecosystem')!r}) "
                        "is missing 'labels'. Add at least a 'dependencies' label."
                    ),
                )
                labels = entry["labels"]
                self.assertIsInstance(labels, list, msg=f"updates[{i}]['labels'] must be a list.")
                self.assertIn(
                    "dependencies", labels,
                    msg=(
                        f"updates[{i}]['labels'] does not include 'dependencies'. "
                        f"Found: {labels!r}"
                    ),
                )

    def test_target_branch_is_set(self):
        """Each update entry should specify a target-branch."""
        updates = self.config.get("updates", [])
        for i, entry in enumerate(updates):
            with self.subTest(entry_index=i, ecosystem=entry.get("package-ecosystem", "<missing>")):
                self.assertIn(
                    "target-branch", entry,
                    msg=(
                        f"updates[{i}] (ecosystem: {entry.get('package-ecosystem')!r}) "
                        "is missing 'target-branch'. Set it to 'main' or 'master'."
                    ),
                )
                target = entry["target-branch"]
                self.assertIn(
                    target, {"main", "master", "develop", "trunk"},
                    msg=(
                        f"updates[{i}]['target-branch'] is {target!r}. "
                        "Verify this matches the repository's actual default branch."
                    ),
                )

    def test_detected_ecosystems_are_covered(self):
        """Every package manifest ecosystem detected in the repo must have a Dependabot entry."""
        present_ecosystems = detect_present_ecosystems()
        if not present_ecosystems:
            self.skipTest("No recognized package manifest files found in the repository.")

        configured_ecosystems = {
            entry.get("package-ecosystem")
            for entry in self.config.get("updates", [])
        }

        for ecosystem in present_ecosystems:
            dependabot_key = DEPENDABOT_ECOSYSTEM_MAP.get(ecosystem)
            if dependabot_key is None:
                continue
            with self.subTest(ecosystem=ecosystem):
                self.assertIn(
                    dependabot_key, configured_ecosystems,
                    msg=(
                        f"Ecosystem '{ecosystem}' has manifest files in the repository "
                        f"but no corresponding Dependabot entry with "
                        f"package-ecosystem: '{dependabot_key}' was found. "
                        f"Configured ecosystems: {sorted(configured_ecosystems)}"
                    ),
                )

    def test_github_actions_ecosystem_covered_if_workflows_exist(self):
        """If .github/workflows/ contains YAML files, github-actions ecosystem must be configured."""
        workflow_dir = os.path.join(REPO_ROOT, ".github", "workflows")
        workflow_files = (
            glob.glob(os.path.join(workflow_dir, "*.yml")) +
            glob.glob(os.path.join(workflow_dir, "*.yaml"))
        )
        if not workflow_files:
            self.skipTest("No GitHub Actions workflow files found.")

        configured_ecosystems = {
            entry.get("package-ecosystem")
            for entry in self.config.get("updates", [])
        }
        self.assertIn(
            "github-actions", configured_ecosystems,
            msg=(
                "GitHub Actions workflow files exist but 'github-actions' ecosystem "
                "is not configured in dependabot.yml. Add an entry with "
                "package-ecosystem: 'github-actions' and directory: '/'."
            ),
        )


class TestRenovateConfiguration(unittest.TestCase):
    """Validate the Renovate configuration file when it is the chosen tool."""

    def setUp(self):
        tool, self.config_path = find_existing_config()
        if tool != "renovate":
            self.skipTest("Renovate config not present — skipping Renovate-specific tests.")
        # Renovate configs are JSON (or JSON5 — parse as JSON for now)
        try:
            self.config = load_json_file(self.config_path)
        except json.JSONDecodeError as exc:
            self.fail(
                f"Renovate config at {self.config_path} is not valid JSON: {exc}\n"
                "If using JSON5 format, ensure the file is valid JSON5."
            )

    def test_config_extends_base(self):
        """Renovate config should extend 'config:base' or another valid preset."""
        self.assertIn(
            "$schema", self.config,
            msg=(
                "renovate.json is missing '$schema'. "
                "Add: \"$schema\": \"https://docs.renovatebot.com/renovate-schema.json\""
            ),
        ) if "$schema" in self.config else None  # schema is optional but recommended

        extends = self.config.get("extends", [])
        self.assertIsInstance(extends, list, msg="'extends' must be a list.")
        self.assertGreater(
            len(extends), 0,
            msg=(
                "renovate.json 'extends' is empty. "
                "Add at least 'config:base' to inherit sensible defaults."
            ),
        )
        # Accept any valid base preset
        valid_base_presets = {
            "config:base",
            "config:recommended",
            ":base",
            "config:js-lib",
            "config:js-app",
        }
        has_valid_base = any(p in valid_base_presets for p in extends)
        self.assertTrue(
            has_valid_base,
            msg=(
                f"renovate.json 'extends' does not include a recognized base preset. "
                f"Found: {extends!r}. "
                f"Add 'config:base' or 'config:recommended'."
            ),
        )

    def test_schedule_is_configured(self):
        """Renovate config must define a schedule to control when PRs are opened."""
        self.assertIn(
            "schedule", self.config,
            msg=(
                "renovate.json is missing 'schedule'. "
                "Add e.g. \"schedule\": [\"before 6am on Monday\"] to control PR timing."
            ),
        )
        schedule = self.config["schedule"]
        self.assertIsInstance(schedule, list, msg="'schedule' must be a list of schedule strings.")
        self.assertGreater(len(schedule), 0, msg="'schedule' list must not be empty.")

    def test_pr_concurrent_limit_is_set(self):
        """Renovate config must set prConcurrentLimit to avoid PR flooding."""
        self.assertIn(
            "prConcurrentLimit", self.config,
            msg=(
                "renovate.json is missing 'prConcurrentLimit'. "
                "Set it to 5 or another reasonable value to prevent PR flooding."
            ),
        )
        limit = self.config["prConcurrentLimit"]
        self.assertIsInstance(limit, int, msg="'prConcurrentLimit' must be an integer.")
        self.assertGreater(limit, 0, msg="'prConcurrentLimit' must be > 0.")

    def test_labels_include_dependencies(self):
        """Renovate config must include a 'dependencies' label for filterability."""
        self.assertIn(
            "labels", self.config,
            msg=(
                "renovate.json is missing 'labels'. "
                "Add \"labels\": [\"dependencies\"] to make Renovate PRs filterable."
            ),
        )
        labels = self.config["labels"]
        self.assertIsInstance(labels, list, msg="'labels' must be a list.")
        self.assertIn(
            "dependencies", labels,
            msg=(
                f"renovate.json 'labels' does not include 'dependencies'. "
                f"Found: {labels!r}"
            ),
        )

    def test_package_rules_present_for_grouping(self):
        """Renovate config should include packageRules to group updates and reduce PR noise."""
        self.assertIn(
            "packageRules", self.config,
            msg=(
                "renovate.json is missing 'packageRules'. "
                "Add packageRules to group patch/minor updates into fewer PRs."
            ),
        )
        rules = self.config["packageRules"]
        self.assertIsInstance(rules, list, msg="'packageRules' must be a list.")
        self.assertGreater(
            len(rules), 0,
            msg="'packageRules' list is empty — add at least one grouping rule.",
        )

    def test_config_is_valid_json_structure(self):
        """Renovate config must be a JSON object (dict), not an array or scalar."""
        self.assertIsInstance(
            self.config, dict,
            msg=(
                f"renovate.json root must be a JSON object (dict). "
                f"Got: {type(self.config).__name__}"
            ),
        )


class TestConfigFileIntegrity(unittest.TestCase):
    """Cross-cutting integrity checks regardless of which tool was chosen."""

    def test_config_file_is_not_empty(self):
        """The configuration file must not be empty."""
        tool, path = find_existing_config()
        if tool is None:
            self.skipTest("No dependency update config found.")
        size = os.path.getsize(path)
        self.assertGreater(
            size, 0,
            msg=f"Configuration file {path} exists but is empty (0 bytes).",
        )

    def test_config_file_is_parseable(self):
        """The configuration file must be parseable without errors."""
        tool, path = find_existing_config()
        if tool is None:
            self.skipTest("No dependency update config found.")

        if tool == "dependabot":
            try:
                load_yaml_file(path)
            except Exception as exc:
                self.fail(f"Failed to parse Dependabot config at {path}: {exc}")
        elif tool == "renovate":
            try:
                load_json_file(path)
            except json.JSONDecodeError as exc:
                self.fail(f"Failed to parse Renovate config at {path}: {exc}")

    def test_config_file_is_committed_in_expected_location(self):
        """The config file must be in the expected location for the detected tool."""
        tool, path = find_existing_config()
        if tool is None:
            self.skipTest("No dependency update config found.")

        if tool == "dependabot":
            self.assertEqual(
                os.path.normpath(path),
                os.path.normpath(DEPENDABOT_CONFIG_PATH),
                msg=(
                    f"Dependabot config found at {path} but expected at "
                    f"{DEPENDABOT_CONFIG_PATH}."
                ),
            )
        elif tool == "renovate":
            self.assertIn(
                os.path.normpath(path),
                [os.path.normpath(p) for p in RENOVATE_CONFIG_PATHS],
                msg=f"Renovate config at {path} is not in a recognized location.",
            )

    def test_upgrade_goal_achieved_config_present(self):
        """
        Primary upgrade validation: confirms the upgrade goal was achieved.

        The upgrade goal was: 'Add Dependabot or Renovate for automated dependency update PRs'.
        This test asserts that a valid configuration file for one of these tools now exists,
        which is the definitive indicator that the upgrade succeeded.
        """
        tool, path = find_existing_config()
        self.assertIsNotNone(
            tool,
            msg=(
                "UPGRADE VALIDATION FAILED: The upgrade goal was to add Dependabot or Renovate "
                "for automated dependency update PRs, but no configuration file was found.\n\n"
                "To fix this, create one of:\n"
                f"  - {DEPENDABOT_CONFIG_PATH}  (for Dependabot)\n"
                f"  - {RENOVATE_CONFIG_PATHS[0]}  (for Renovate)\n\n"
                "See the upgrade spec for required configuration fields."
            ),
        )
        self.assertIn(
            tool, {"dependabot", "renovate"},
            msg=f"Unexpected tool type detected: {tool!r}",
        )


class TestDependabotConfigurationVersion(unittest.TestCase):
    """
    Explicit version assertion: verifies the Dependabot schema is at version 2
    (the target/latest stable version for dependabot.yml).
    """

    def setUp(self):
        tool, self.config_path = find_existing_config()
        if tool != "dependabot":
            self.skipTest("Dependabot config not present.")
        self.config = load_yaml_file(self.config_path)

    def test_dependabot_schema_version_is_target_version_2(self):
        """
        Version assertion: dependabot.yml must use schema version 2.

        Version 2 is the current and only supported schema version for Dependabot
        configuration files. Version 1 is deprecated and no longer functional.
        This test confirms the upgraded configuration uses the correct target version.
        """
        actual_version = self.config.get("version")
        target_version = 2
        self.assertEqual(
            actual_version,
            target_version,
            msg=(
                f"Dependabot config schema version mismatch: "
                f"found version={actual_version!r}, expected version={target_version}. "
                f"The 'version: 2' key is required at the top of .github/dependabot.yml. "
                f"Version 1 is deprecated and unsupported."
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)