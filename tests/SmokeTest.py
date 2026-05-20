import os
import re
import unittest

TARGET_RUNTIME_VERSION = 'latest stable'

DOCUMENT_FILES = [
    'README.md',
    'docs/DEPLOYMENT.md',
    'CONTRIBUTING.md',
    'CHANGELOG.md',
]

# Deprecated APIs/configs to check are no longer present (examples, adjust as needed)
DEPRECATED_RUNTIME_REFERENCES = [
    'python2',
    'node v10',
    'OldRuntime',
    'legacy_dependency',
    'DEPRECATED_CONFIG_KEY',
]

# New config keys expected per upgrade (examples, adjust as needed)
NEW_CONFIG_KEYS = [
    'NEW_RUNTIME_CONFIG',
    'REQUIRED_DEPENDENCY_VERSION',
    'UPDATED_BUILD_FLAG',
]

class TestDocumentationUpgrade(unittest.TestCase):

    def test_readme_references_target_runtime_version(self):
        # The README.md must reference the exact new runtime version
        with open('README.md', encoding='utf-8') as f:
            readme = f.read()
        self.assertIn(TARGET_RUNTIME_VERSION, readme,
            f"README.md must mention the upgraded runtime version {TARGET_RUNTIME_VERSION}.")
        # Ensure no references to deprecated runtimes in README
        for old_ref in DEPRECATED_RUNTIME_REFERENCES:
            self.assertNotIn(old_ref, readme,
                f"README.md must not reference deprecated runtime or dependencies: {old_ref}")

    def test_deployment_md_uses_new_config_keys(self):
        with open('docs/DEPLOYMENT.md', encoding='utf-8') as f:
            deploy = f.read()
        # All new config keys should be present
        for key in NEW_CONFIG_KEYS:
            self.assertIn(key, deploy,
                f"docs/DEPLOYMENT.md is missing expected new config key: {key}")
        # Deprecated config keys should not appear
        for dep in DEPRECATED_RUNTIME_REFERENCES:
            self.assertNotIn(dep, deploy,
                f"docs/DEPLOYMENT.md must not reference deprecated key/runtime/dependency: {dep}")

    def test_changelog_mentions_upgrade(self):
        with open('CHANGELOG.md', encoding='utf-8') as f:
            changelog = f.read()
        pattern = re.compile(r'documentation updates.*new runtime.*dependencies.*configuration', re.I | re.S)
        self.assertRegex(
            changelog,
            pattern,
            "CHANGELOG.md must include an entry describing documentation updates for new runtime, dependencies, and configuration"
        )

    def test_contributing_and_docs_have_updated_dependencies(self):
        # CONTRIBUTING.md must document the new dependency stack, not old ones
        with open('CONTRIBUTING.md', encoding='utf-8') as f:
            contrib = f.read()
        for dep in DEPRECATED_RUNTIME_REFERENCES:
            self.assertNotIn(dep, contrib,
                f"CONTRIBUTING.md contains deprecated dependency or runtime reference: {dep}")
        self.assertIn(TARGET_RUNTIME_VERSION, contrib,
            f"CONTRIBUTING.md must refer to the upgraded runtime version: {TARGET_RUNTIME_VERSION}")

    def test_no_files_reference_prior_runtime_or_deprecated_dependency(self):
        # No documentation file should reference deprecated or prior runtimes/dependencies
        for doc_file in DOCUMENT_FILES:
            with open(doc_file, encoding='utf-8') as f:
                contents = f.read()
            for old_ref in DEPRECATED_RUNTIME_REFERENCES:
                self.assertNotIn(
                    old_ref, contents,
                    f"{doc_file} must not reference deprecated runtime, dependency, or config: {old_ref}"
                )

    def test_new_config_keys_do_not_cause_load_errors(self):
        # Simulate loading new config keys (assuming example config yaml or env format in docs)
        # In a real upgrade, this would load actual config; for doc upgrade, check their example usage lines for syntax
        with open('docs/DEPLOYMENT.md', encoding='utf-8') as f:
            deploy = f.read()
        for key in NEW_CONFIG_KEYS:
            key_usages = re.findall(rf'{key}\s*[=:]\s*.+', deploy)
            self.assertTrue(
                key_usages,
                f"Key {key} should appear with sample value or usage in docs/DEPLOYMENT.md"
            )
            # Ensure no typos like double colons, missing values, etc.
            for line in key_usages:
                self.assertRegex(
                    line, rf'^{key}\s*[=:]\s*\S+',
                    f"Key {key} usage malformed in docs/DEPLOYMENT.md: {line}"
                )

if __name__ == '__main__':
    unittest.main()