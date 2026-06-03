"""
Upgrade validation tests for: Document required environment variables and local setup instructions

These tests verify that the documentation upgrade succeeded by checking:
- Required documentation files exist at expected paths
- .env.example contains required structure and fields
- docs/local-setup.md (or README.md) contains required sections
- Environment variable reference table is present and well-formed
- Secrets guidance section exists
- No placeholder TODOs remain in final documentation
"""

import os
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).parent.parent.resolve()

ENV_EXAMPLE_CANDIDATES = [
    REPO_ROOT / ".env.example",
    REPO_ROOT / ".env.sample",
]

SETUP_DOC_CANDIDATES = [
    REPO_ROOT / "docs" / "local-setup.md",
    REPO_ROOT / "docs" / "setup.md",
    REPO_ROOT / "README.md",
]

REQUIRED_SETUP_SECTIONS = [
    "prerequisites",
    "clone",
    "env",
    "install",
    "run",
]

REQUIRED_TABLE_COLUMNS = [
    "variable name",
    "description",
    "required",
    "default",
    "example",
]

REQUIRED_SECRETS_KEYWORDS = [
    "secret",
    "credential",
    "commit",
]


def _find_existing(candidates):
    for path in candidates:
        if path.exists():
            return path
    return None


def _read(path):
    return path.read_text(encoding="utf-8")


class TestEnvExampleExists(unittest.TestCase):
    """Verify .env.example (or .env.sample) exists at the repository root."""

    def setUp(self):
        self.env_example_path = _find_existing(ENV_EXAMPLE_CANDIDATES)

    def test_env_example_file_exists(self):
        self.assertIsNotNone(
            self.env_example_path,
            msg=(
                "No .env.example or .env.sample found at repository root. "
                "Expected one of: "
                + ", ".join(str(p) for p in ENV_EXAMPLE_CANDIDATES)
            ),
        )

    def test_env_example_is_not_empty(self):
        if self.env_example_path is None:
            self.skipTest(".env.example not found — covered by test_env_example_file_exists")
        content = _read(self.env_example_path)
        self.assertGreater(
            len(content.strip()),
            0,
            msg=f"{self.env_example_path} exists but is empty.",
        )


class TestEnvExampleStructure(unittest.TestCase):
    """Verify .env.example has correct structure: comments, placeholders, required/optional markers."""

    def setUp(self):
        path = _find_existing(ENV_EXAMPLE_CANDIDATES)
        if path is None:
            self.content = None
            self.lines = []
        else:
            self.content = _read(path)
            self.lines = self.content.splitlines()

    def _skip_if_missing(self):
        if self.content is None:
            self.skipTest(".env.example not found — covered by TestEnvExampleExists")

    def test_contains_at_least_one_variable_assignment(self):
        self._skip_if_missing()
        assignments = [
            line for line in self.lines
            if re.match(r"^[A-Z][A-Z0-9_]*\s*=", line.strip())
        ]
        self.assertGreater(
            len(assignments),
            0,
            msg=(
                ".env.example must contain at least one environment variable assignment "
                "in the form VARIABLE_NAME=value."
            ),
        )

    def test_contains_inline_comments_for_variables(self):
        self._skip_if_missing()
        comment_lines = [line for line in self.lines if line.strip().startswith("#")]
        self.assertGreater(
            len(comment_lines),
            0,
            msg=(
                ".env.example must contain inline or block comments describing variables. "
                "No comment lines (starting with #) were found."
            ),
        )

    def test_contains_required_or_optional_markers(self):
        self._skip_if_missing()
        lower = self.content.lower()
        has_marker = ("required" in lower) or ("optional" in lower)
        self.assertTrue(
            has_marker,
            msg=(
                ".env.example must indicate which variables are required and which are optional. "
                "Neither 'required' nor 'optional' was found in the file."
            ),
        )

    def test_no_real_secrets_committed(self):
        """Placeholder values must not look like real secrets (long hex/base64 strings)."""
        self._skip_if_missing()
        suspicious_pattern = re.compile(
            r"^[A-Z][A-Z0-9_]*\s*=\s*[A-Za-z0-9+/]{32,}={0,2}\s*$"
        )
        violations = [
            line for line in self.lines
            if suspicious_pattern.match(line.strip())
        ]
        self.assertEqual(
            violations,
            [],
            msg=(
                ".env.example appears to contain real secret values (long base64/hex strings). "
                "Use placeholder values such as 'your-secret-here'. "
                "Suspicious lines:\n" + "\n".join(violations)
            ),
        )


class TestSetupDocumentationExists(unittest.TestCase):
    """Verify that a local setup documentation file exists."""

    def setUp(self):
        self.setup_doc_path = _find_existing(SETUP_DOC_CANDIDATES)

    def test_setup_documentation_file_exists(self):
        self.assertIsNotNone(
            self.setup_doc_path,
            msg=(
                "No local setup documentation file found. "
                "Expected one of: "
                + ", ".join(str(p) for p in SETUP_DOC_CANDIDATES)
            ),
        )

    def test_setup_documentation_is_not_empty(self):
        if self.setup_doc_path is None:
            self.skipTest("Setup doc not found — covered by test_setup_documentation_file_exists")
        content = _read(self.setup_doc_path)
        self.assertGreater(
            len(content.strip()),
            0,
            msg=f"{self.setup_doc_path} exists but is empty.",
        )


class TestSetupDocumentationSections(unittest.TestCase):
    """Verify the setup documentation contains all required sections."""

    def setUp(self):
        path = _find_existing(SETUP_DOC_CANDIDATES)
        if path is None:
            self.content = None
        else:
            self.content = _read(path).lower()

    def _skip_if_missing(self):
        if self.content is None:
            self.skipTest("Setup doc not found — covered by TestSetupDocumentationExists")

    def test_contains_prerequisites_section(self):
        self._skip_if_missing()
        self.assertIn(
            "prerequisite",
            self.content,
            msg="Setup documentation must contain a 'Prerequisites' section.",
        )

    def test_contains_clone_or_repository_instructions(self):
        self._skip_if_missing()
        has_clone = ("clone" in self.content) or ("git clone" in self.content)
        self.assertTrue(
            has_clone,
            msg=(
                "Setup documentation must include instructions for cloning the repository "
                "(expected 'clone' or 'git clone')."
            ),
        )

    def test_contains_env_file_copy_instructions(self):
        self._skip_if_missing()
        has_env_copy = (
            ".env.example" in self.content
            or ".env.sample" in self.content
            or "cp .env" in self.content
            or "copy .env" in self.content
        )
        self.assertTrue(
            has_env_copy,
            msg=(
                "Setup documentation must include instructions for copying .env.example to .env. "
                "Expected references to '.env.example', 'cp .env', or 'copy .env'."
            ),
        )

    def test_contains_dependency_installation_instructions(self):
        self._skip_if_missing()
        install_keywords = ["install", "npm install", "pip install", "bundle install", "yarn", "poetry", "composer"]
        has_install = any(kw in self.content for kw in install_keywords)
        self.assertTrue(
            has_install,
            msg=(
                "Setup documentation must include dependency installation instructions. "
                "Expected one of: " + ", ".join(install_keywords)
            ),
        )

    def test_contains_run_or_start_instructions(self):
        self._skip_if_missing()
        run_keywords = ["run", "start", "serve", "launch", "npm start", "python", "rails server", "docker"]
        has_run = any(kw in self.content for kw in run_keywords)
        self.assertTrue(
            has_run,
            msg=(
                "Setup documentation must include instructions for running the application locally. "
                "Expected one of: " + ", ".join(run_keywords)
            ),
        )


class TestEnvironmentVariableReferenceTable(unittest.TestCase):
    """Verify the setup documentation contains a well-formed environment variable reference table."""

    def setUp(self):
        path = _find_existing(SETUP_DOC_CANDIDATES)
        if path is None:
            self.content = None
        else:
            self.content = _read(path).lower()

    def _skip_if_missing(self):
        if self.content is None:
            self.skipTest("Setup doc not found — covered by TestSetupDocumentationExists")

    def test_table_has_variable_name_column(self):
        self._skip_if_missing()
        self.assertIn(
            "variable name",
            self.content,
            msg=(
                "Environment variable reference table must include a 'Variable Name' column header."
            ),
        )

    def test_table_has_description_column(self):
        self._skip_if_missing()
        self.assertIn(
            "description",
            self.content,
            msg=(
                "Environment variable reference table must include a 'Description' column header."
            ),
        )

    def test_table_has_required_optional_column(self):
        self._skip_if_missing()
        has_column = ("required" in self.content) and ("optional" in self.content)
        self.assertTrue(
            has_column,
            msg=(
                "Environment variable reference table must include a 'Required/Optional' column "
                "with both 'required' and 'optional' values present."
            ),
        )

    def test_table_has_default_value_column(self):
        self._skip_if_missing()
        self.assertIn(
            "default",
            self.content,
            msg=(
                "Environment variable reference table must include a 'Default Value' column header."
            ),
        )

    def test_table_has_example_value_column(self):
        self._skip_if_missing()
        self.assertIn(
            "example",
            self.content,
            msg=(
                "Environment variable reference table must include an 'Example Value' column header."
            ),
        )

    def test_table_uses_markdown_table_syntax(self):
        self._skip_if_missing()
        has_table_syntax = "|" in self.content and "---" in self.content
        self.assertTrue(
            has_table_syntax,
            msg=(
                "Environment variable reference table must use Markdown table syntax "
                "(pipe '|' characters and separator rows with '---')."
            ),
        )


class TestSecretsAndSensitiveValuesSection(unittest.TestCase):
    """Verify the setup documentation contains a secrets and sensitive values guidance section."""

    def setUp(self):
        path = _find_existing(SETUP_DOC_CANDIDATES)
        if path is None:
            self.content = None
        else:
            self.content = _read(path).lower()

    def _skip_if_missing(self):
        if self.content is None:
            self.skipTest("Setup doc not found — covered by TestSetupDocumentationExists")

    def test_secrets_section_exists(self):
        self._skip_if_missing()
        has_secrets = "secret" in self.content or "sensitive" in self.content
        self.assertTrue(
            has_secrets,
            msg=(
                "Setup documentation must contain a 'Secrets & Sensitive Values' section "
                "or equivalent guidance. Expected 'secret' or 'sensitive' in the document."
            ),
        )

    def test_do_not_commit_credentials_warning_exists(self):
        self._skip_if_missing()
        has_warning = (
            ("do not commit" in self.content)
            or ("never commit" in self.content)
            or ("don't commit" in self.content)
            or ("not commit" in self.content)
        )
        self.assertTrue(
            has_warning,
            msg=(
                "Setup documentation must explicitly warn contributors not to commit real credentials. "
                "Expected phrases like 'do not commit', 'never commit', or 'not commit'."
            ),
        )

    def test_instructions_for_obtaining_secrets_exist(self):
        self._skip_if_missing()
        obtain_keywords = ["obtain", "request", "contact", "ask", "vault", "secrets manager", "1password", "lastpass", "bitwarden", "keybase"]
        has_obtain = any(kw in self.content for kw in obtain_keywords)
        self.assertTrue(
            has_obtain,
            msg=(
                "Setup documentation must explain how contributors can obtain secret values. "
                "Expected one of: " + ", ".join(obtain_keywords)
            ),
        )


class TestEnvironmentSpecificDocumentation(unittest.TestCase):
    """Verify that environment-specific variable differences are documented."""

    def setUp(self):
        path = _find_existing(SETUP_DOC_CANDIDATES)
        if path is None:
            self.content = None
        else:
            self.content = _read(path).lower()

    def _skip_if_missing(self):
        if self.content is None:
            self.skipTest("Setup doc not found — covered by TestSetupDocumentationExists")

    def test_multiple_environments_referenced(self):
        self._skip_if_missing()
        env_keywords = ["development", "staging", "production"]
        found = [kw for kw in env_keywords if kw in self.content]
        self.assertGreaterEqual(
            len(found),
            2,
            msg=(
                "Setup documentation must reference at least two deployment environments "
                "(e.g., development, staging, production) to document environment-specific "
                "variable differences. Found: " + str(found)
            ),
        )


class TestNoUnresolvedPlaceholders(unittest.TestCase):
    """Verify that documentation does not contain unresolved TODO placeholders from the spec."""

    TODO_PATTERN = re.compile(r"\bTODO\b", re.IGNORECASE)

    def _check_file(self, path):
        if path is None or not path.exists():
            return []
        content = _read(path)
        lines_with_todos = [
            (i + 1, line)
            for i, line in enumerate(content.splitlines())
            if self.TODO_PATTERN.search(line)
        ]
        return lines_with_todos

    def test_env_example_has_no_unresolved_todos(self):
        path = _find_existing(ENV_EXAMPLE_CANDIDATES)
        violations = self._check_file(path)
        self.assertEqual(
            violations,
            [],
            msg=(
                f"{path} contains unresolved TODO placeholders. "
                "All TODOs must be resolved before the upgrade is considered complete. "
                "Lines: " + str(violations)
            ),
        )

    def test_setup_doc_has_no_unresolved_todos(self):
        path = _find_existing(SETUP_DOC_CANDIDATES)
        violations = self._check_file(path)
        self.assertEqual(
            violations,
            [],
            msg=(
                f"{path} contains unresolved TODO placeholders. "
                "All TODOs must be resolved before the upgrade is considered complete. "
                "Lines: " + str(violations)
            ),
        )


class TestDocumentationVersionAndCurrency(unittest.TestCase):
    """Verify the setup documentation reflects the current state of the project."""

    def setUp(self):
        path = _find_existing(SETUP_DOC_CANDIDATES)
        if path is None:
            self.content = None
            self.path = None
        else:
            self.content = _read(path)
            self.path = path

    def _skip_if_missing(self):
        if self.content is None:
            self.skipTest("Setup doc not found — covered by TestSetupDocumentationExists")

    def test_setup_doc_has_minimum_length(self):
        """Documentation must be substantive — not just a stub."""
        self._skip_if_missing()
        word_count = len(self.content.split())
        self.assertGreaterEqual(
            word_count,
            150,
            msg=(
                f"Setup documentation at {self.path} appears to be a stub "
                f"(only {word_count} words). "
                "A complete setup guide should have at least 150 words."
            ),
        )

    def test_env_example_and_setup_doc_variable_names_are_consistent(self):
        """Variable names in .env.example should appear in the setup doc reference table."""
        self._skip_if_missing()
        env_path = _find_existing(ENV_EXAMPLE_CANDIDATES)
        if env_path is None:
            self.skipTest(".env.example not found — covered by TestEnvExampleExists")

        env_content = _read(env_path)
        assignment_pattern = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=", re.MULTILINE)
        variable_names = assignment_pattern.findall(env_content)

        if not variable_names:
            self.skipTest("No variable assignments found in .env.example")

        setup_content_lower = self.content.lower()
        missing = [
            name for name in variable_names
            if name.lower() not in setup_content_lower
        ]

        self.assertEqual(
            missing,
            [],
            msg=(
                "The following environment variables are defined in .env.example "
                "but not referenced in the setup documentation. "
                "All variables must appear in the reference table:\n"
                + "\n".join(missing)
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)