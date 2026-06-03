"""
Upgrade Validation Tests: Document Required Environment Variables and Local Setup Instructions

These tests verify that the documentation upgrade succeeded by checking:
1. Required documentation files exist at expected paths
2. .env.example exists and contains properly formatted entries
3. Local setup documentation exists and covers required sections
4. Environment variable reference table is present with required columns
5. Key documentation sections are present (secrets guidance, env-specific notes, etc.)
"""

import os
import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


class TestEnvExampleFileExists(unittest.TestCase):
    """Verify .env.example exists at the repository root."""

    def setUp(self):
        self.env_example_path = REPO_ROOT / ".env.example"

    def test_env_example_file_exists(self):
        self.assertTrue(
            self.env_example_path.exists(),
            f".env.example not found at repository root: {self.env_example_path}",
        )

    def test_env_example_is_not_empty(self):
        self.assertTrue(
            self.env_example_path.exists(),
            ".env.example does not exist — cannot check contents",
        )
        content = self.env_example_path.read_text(encoding="utf-8")
        self.assertTrue(
            len(content.strip()) > 0,
            ".env.example exists but is empty",
        )

    def test_env_example_has_at_least_one_variable_entry(self):
        """At least one KEY=value or KEY= line must be present."""
        self.assertTrue(
            self.env_example_path.exists(),
            ".env.example does not exist",
        )
        content = self.env_example_path.read_text(encoding="utf-8")
        variable_lines = [
            line for line in content.splitlines()
            if re.match(r"^[A-Z_][A-Z0-9_]*\s*=", line.strip())
        ]
        self.assertGreater(
            len(variable_lines),
            0,
            ".env.example contains no KEY=value entries. "
            "Expected at least one environment variable definition.",
        )

    def test_env_example_entries_have_inline_comments_or_descriptions(self):
        """
        Each non-blank, non-comment line should either have an inline comment
        or be preceded by a comment line describing it.
        """
        self.assertTrue(
            self.env_example_path.exists(),
            ".env.example does not exist",
        )
        content = self.env_example_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        variable_lines_with_index = [
            (i, line) for i, line in enumerate(lines)
            if re.match(r"^[A-Z_][A-Z0-9_]*\s*=", line.strip())
        ]

        undocumented = []
        for idx, line in variable_lines_with_index:
            has_inline_comment = "#" in line
            has_preceding_comment = (
                idx > 0 and lines[idx - 1].strip().startswith("#")
            )
            if not has_inline_comment and not has_preceding_comment:
                undocumented.append(line.strip())

        self.assertEqual(
            undocumented,
            [],
            f"The following .env.example entries have no inline comment or "
            f"preceding comment line describing them:\n"
            + "\n".join(f"  {e}" for e in undocumented),
        )

    def test_env_example_indicates_required_or_optional_for_each_variable(self):
        """
        Each variable entry (or its associated comment) should indicate
        whether it is required or optional.
        """
        self.assertTrue(
            self.env_example_path.exists(),
            ".env.example does not exist",
        )
        content = self.env_example_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        variable_lines_with_index = [
            (i, line) for i, line in enumerate(lines)
            if re.match(r"^[A-Z_][A-Z0-9_]*\s*=", line.strip())
        ]

        missing_required_optional = []
        for idx, line in variable_lines_with_index:
            context_lines = []
            if idx > 0:
                context_lines.append(lines[idx - 1])
            if idx > 1:
                context_lines.append(lines[idx - 2])
            context_lines.append(line)
            combined = " ".join(context_lines).lower()
            if "required" not in combined and "optional" not in combined:
                missing_required_optional.append(line.strip())

        self.assertEqual(
            missing_required_optional,
            [],
            "The following .env.example entries do not indicate whether they "
            "are required or optional (expected 'required' or 'optional' in "
            "the entry or its preceding comment lines):\n"
            + "\n".join(f"  {e}" for e in missing_required_optional),
        )

    def test_env_example_does_not_contain_real_secrets(self):
        """
        .env.example must not contain obviously real credentials.
        Checks for common secret patterns (long hex strings, JWT tokens, etc.)
        that should never appear in a committed example file.
        """
        self.assertTrue(
            self.env_example_path.exists(),
            ".env.example does not exist",
        )
        content = self.env_example_path.read_text(encoding="utf-8")

        suspicious_patterns = [
            (r"(?<==)[A-Za-z0-9+/]{40,}={0,2}", "long base64-like string"),
            (r"(?<==)[0-9a-f]{32,}", "long hex string (possible secret)"),
            (r"eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{20,}", "JWT token"),
            (r"(?<==)sk-[A-Za-z0-9]{20,}", "API key pattern (sk-)"),
            (r"(?<==)ghp_[A-Za-z0-9]{36}", "GitHub personal access token"),
        ]

        found = []
        for pattern, description in suspicious_patterns:
            matches = re.findall(pattern, content)
            if matches:
                found.append(f"{description}: {matches[:2]}")

        self.assertEqual(
            found,
            [],
            ".env.example appears to contain real secrets or credentials:\n"
            + "\n".join(f"  {f}" for f in found),
        )


class TestLocalSetupDocumentationExists(unittest.TestCase):
    """Verify that local setup documentation exists at an expected path."""

    CANDIDATE_PATHS = [
        REPO_ROOT / "docs" / "local-setup.md",
        REPO_ROOT / "docs" / "setup.md",
        REPO_ROOT / "docs" / "LOCAL_SETUP.md",
        REPO_ROOT / "docs" / "SETUP.md",
        REPO_ROOT / "README.md",
    ]

    def _find_setup_doc(self):
        """Return the first candidate path that exists, or None."""
        for path in self.CANDIDATE_PATHS:
            if path.exists():
                return path
        return None

    def test_setup_documentation_file_exists(self):
        doc = self._find_setup_doc()
        self.assertIsNotNone(
            doc,
            "No local setup documentation found. Expected one of:\n"
            + "\n".join(f"  {p}" for p in self.CANDIDATE_PATHS),
        )

    def test_setup_doc_is_not_empty(self):
        doc = self._find_setup_doc()
        self.assertIsNotNone(doc, "No setup documentation file found")
        content = doc.read_text(encoding="utf-8")
        self.assertGreater(
            len(content.strip()),
            0,
            f"Setup documentation at {doc} is empty",
        )


class TestLocalSetupDocumentationContent(unittest.TestCase):
    """Verify that local setup documentation covers all required sections."""

    CANDIDATE_PATHS = [
        REPO_ROOT / "docs" / "local-setup.md",
        REPO_ROOT / "docs" / "setup.md",
        REPO_ROOT / "docs" / "LOCAL_SETUP.md",
        REPO_ROOT / "docs" / "SETUP.md",
        REPO_ROOT / "README.md",
    ]

    def _find_setup_doc(self):
        for path in self.CANDIDATE_PATHS:
            if path.exists():
                return path
        return None

    def _get_content(self):
        doc = self._find_setup_doc()
        if doc is None:
            self.skipTest("No setup documentation file found — skipping content checks")
        return doc.read_text(encoding="utf-8").lower()

    def test_prerequisites_section_present(self):
        content = self._get_content()
        self.assertIn(
            "prerequisite",
            content,
            "Setup documentation must include a 'Prerequisites' section",
        )

    def test_clone_repo_instructions_present(self):
        content = self._get_content()
        self.assertTrue(
            "clone" in content or "git clone" in content,
            "Setup documentation must include instructions for cloning the repository",
        )

    def test_copy_env_example_instructions_present(self):
        content = self._get_content()
        self.assertTrue(
            ".env.example" in content or "env.example" in content,
            "Setup documentation must reference .env.example and instruct "
            "developers to copy it to .env",
        )

    def test_copy_env_to_dotenv_step_present(self):
        content = self._get_content()
        self.assertTrue(
            "cp .env.example .env" in content
            or "copy .env.example .env" in content
            or ("copy" in content and ".env" in content)
            or ("cp" in content and ".env" in content),
            "Setup documentation must include a step to copy .env.example to .env",
        )

    def test_install_dependencies_step_present(self):
        content = self._get_content()
        self.assertTrue(
            "install" in content and ("depend" in content or "npm install" in content
                                       or "pip install" in content
                                       or "bundle install" in content
                                       or "yarn" in content
                                       or "install dependencies" in content),
            "Setup documentation must include a step for installing dependencies",
        )

    def test_run_application_locally_step_present(self):
        content = self._get_content()
        self.assertTrue(
            "run" in content or "start" in content or "serve" in content,
            "Setup documentation must include instructions for running the application locally",
        )

    def test_environment_variable_reference_table_present(self):
        """
        The documentation must contain a reference table for environment variables.
        Checks for markdown table syntax or a structured list with variable names.
        """
        content = self._get_content()
        has_markdown_table = "|" in content and "---" in content
        has_variable_section = (
            "variable name" in content
            or "environment variable" in content
            or "env var" in content
        )
        self.assertTrue(
            has_markdown_table or has_variable_section,
            "Setup documentation must include an environment variable reference "
            "table (markdown table with | separators, or a section titled "
            "'Environment Variables')",
        )

    def test_reference_table_has_required_columns(self):
        """
        The environment variable table must include columns for:
        Variable Name, Description, Required/Optional, Default Value, Example Value.
        """
        content = self._get_content()
        required_column_keywords = [
            ("variable name", "variable"),
            ("description",),
            ("required", "optional"),
            ("default",),
            ("example",),
        ]
        missing = []
        for keyword_group in required_column_keywords:
            if not any(kw in content for kw in keyword_group):
                missing.append(" / ".join(keyword_group))

        self.assertEqual(
            missing,
            [],
            "Environment variable reference table is missing columns for: "
            + ", ".join(missing),
        )

    def test_secrets_section_present(self):
        """
        Documentation must include a section warning about secrets and
        instructing contributors not to commit real credentials.
        """
        content = self._get_content()
        self.assertTrue(
            "secret" in content or "credential" in content or "sensitive" in content,
            "Setup documentation must include a 'Secrets & Sensitive Values' section "
            "warning contributors not to commit real credentials",
        )

    def test_do_not_commit_secrets_warning_present(self):
        content = self._get_content()
        self.assertTrue(
            ("do not commit" in content or "never commit" in content
             or "don't commit" in content or "not commit" in content),
            "Setup documentation must explicitly warn contributors never to commit "
            "real secrets or credentials",
        )

    def test_how_to_obtain_secrets_documented(self):
        """
        Documentation must explain how contributors can obtain secret values.
        """
        content = self._get_content()
        self.assertTrue(
            "obtain" in content
            or "request" in content
            or "ask" in content
            or "contact" in content
            or "vault" in content
            or "secrets manager" in content
            or "1password" in content
            or "lastpass" in content
            or "bitwarden" in content
            or "how to get" in content
            or "how to obtain" in content,
            "Setup documentation must explain how contributors can obtain secret values",
        )

    def test_environment_specific_differences_documented(self):
        """
        Documentation must note any differences between development, staging,
        and production environment variable values.
        """
        content = self._get_content()
        has_dev = "development" in content or "local" in content
        has_staging = "staging" in content
        has_prod = "production" in content or "prod" in content
        self.assertTrue(
            has_dev and (has_staging or has_prod),
            "Setup documentation must document environment-specific differences "
            "(development vs staging vs production) for environment variables",
        )


class TestEnvExampleAndDocumentationConsistency(unittest.TestCase):
    """
    Verify that variables listed in .env.example are also documented
    in the local setup documentation reference table.
    """

    CANDIDATE_PATHS = [
        REPO_ROOT / "docs" / "local-setup.md",
        REPO_ROOT / "docs" / "setup.md",
        REPO_ROOT / "docs" / "LOCAL_SETUP.md",
        REPO_ROOT / "docs" / "SETUP.md",
        REPO_ROOT / "README.md",
    ]

    def _find_setup_doc(self):
        for path in self.CANDIDATE_PATHS:
            if path.exists():
                return path
        return None

    def _get_env_example_variables(self):
        env_example_path = REPO_ROOT / ".env.example"
        if not env_example_path.exists():
            return []
        content = env_example_path.read_text(encoding="utf-8")
        variables = []
        for line in content.splitlines():
            match = re.match(r"^([A-Z_][A-Z0-9_]*)\s*=", line.strip())
            if match:
                variables.append(match.group(1))
        return variables

    def test_all_env_example_variables_appear_in_setup_docs(self):
        env_example_path = REPO_ROOT / ".env.example"
        if not env_example_path.exists():
            self.skipTest(".env.example not found — skipping consistency check")

        doc = self._find_setup_doc()
        if doc is None:
            self.skipTest("No setup documentation found — skipping consistency check")

        variables = self._get_env_example_variables()
        if not variables:
            self.skipTest(".env.example has no variable entries — skipping consistency check")

        doc_content = doc.read_text(encoding="utf-8")

        missing_from_docs = [
            var for var in variables if var not in doc_content
        ]

        self.assertEqual(
            missing_from_docs,
            [],
            "The following variables are defined in .env.example but are NOT "
            "documented in the setup documentation reference table:\n"
            + "\n".join(f"  {v}" for v in missing_from_docs),
        )


class TestNoEnvFilesWithRealSecretsCommitted(unittest.TestCase):
    """
    Verify that .env (with real values) is not committed to the repository.
    Only .env.example (or .env.sample) should be tracked.
    """

    def test_dotenv_file_is_not_committed(self):
        """
        .env should not exist as a tracked file. Its presence at the repo root
        is a warning sign (it may contain real secrets).
        This test checks that .env is listed in .gitignore.
        """
        gitignore_path = REPO_ROOT / ".gitignore"
        if not gitignore_path.exists():
            self.skipTest(".gitignore not found — skipping .env gitignore check")

        content = gitignore_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines()]

        dotenv_ignored = any(
            line in (".env", "*.env", ".env.*") or line.startswith(".env")
            for line in lines
            if not line.startswith("#")
        )

        self.assertTrue(
            dotenv_ignored,
            ".env is not listed in .gitignore. Real secret files must be "
            "excluded from version control. Add '.env' to .gitignore.",
        )

    def test_env_example_is_not_gitignored(self):
        """
        .env.example must NOT be gitignored — it should be committed so all
        developers can use it as a template.
        """
        gitignore_path = REPO_ROOT / ".gitignore"
        if not gitignore_path.exists():
            self.skipTest(".gitignore not found — skipping check")

        content = gitignore_path.read_text(encoding="utf-8")
        lines = [line.strip() for line in content.splitlines()]

        env_example_ignored = any(
            line == ".env.example" or line == "*.env.example"
            for line in lines
            if not line.startswith("#")
        )

        self.assertFalse(
            env_example_ignored,
            ".env.example is listed in .gitignore but it should be committed "
            "to the repository so developers can use it as a template.",
        )


class TestDocumentationVersionAndCompleteness(unittest.TestCase):
    """
    Verify that the documentation upgrade is complete and up-to-date.
    """

    CANDIDATE_PATHS = [
        REPO_ROOT / "docs" / "local-setup.md",
        REPO_ROOT / "docs" / "setup.md",
        REPO_ROOT / "docs" / "LOCAL_SETUP.md",
        REPO_ROOT / "docs" / "SETUP.md",
        REPO_ROOT / "README.md",
    ]

    def _find_setup_doc(self):
        for path in self.CANDIDATE_PATHS:
            if path.exists():
                return path
        return None

    def test_setup_documentation_has_minimum_length(self):
        """
        A meaningful setup guide should be at least 500 characters long.
        This guards against placeholder or stub documentation.
        """
        doc = self._find_setup_doc()
        if doc is None:
            self.skipTest("No setup documentation found")
        content = doc.read_text(encoding="utf-8")
        self.assertGreaterEqual(
            len(content.strip()),
            500,
            f"Setup documentation at {doc} appears too short "
            f"({len(content.strip())} chars). A complete setup guide should "
            f"be at least 500 characters.",
        )

    def test_docs_directory_exists(self):
        """
        A docs/ directory should exist for structured documentation.
        """
        docs_dir = REPO_ROOT / "docs"
        self.assertTrue(
            docs_dir.exists() and docs_dir.is_dir(),
            "A 'docs/' directory should exist at the repository root for "
            "structured project documentation.",
        )

    def test_env_example_has_placeholder_values_not_empty_values(self):
        """
        Variables in .env.example should have placeholder values (not just KEY=)
        so developers know what format is expected.
        """
        env_example_path = REPO_ROOT / ".env.example"
        if not env_example_path.exists():
            self.skipTest(".env.example not found")

        content = env_example_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        empty_value_lines = []
        for line in lines:
            stripped = line.strip()
            if re.match(r"^[A-Z_][A-Z0-9_]*\s*=$", stripped):
                empty_value_lines.append(stripped)

        if empty_value_lines:
            # Warn but do not fail — some variables legitimately have no default
            # This is a soft check; adjust to assertFail if policy requires placeholders
            pass

        # Hard check: at least half of variable entries should have a value or placeholder
        all_var_lines = [
            line.strip() for line in lines
            if re.match(r"^[A-Z_][A-Z0-9_]*\s*=", line.strip())
        ]
        if len(all_var_lines) == 0:
            self.skipTest("No variable entries in .env.example")

        lines_with_values = [
            line for line in all_var_lines
            if not re.match(r"^[A-Z_][A-Z0-9_]*\s*=$", line)
        ]

        ratio = len(lines_with_values) / len(all_var_lines)
        self.assertGreaterEqual(
            ratio,
            0.5,
            f"More than half of .env.example entries have empty values. "
            f"Provide placeholder or example values so developers know the "
            f"expected format. ({len(lines_with_values)}/{len(all_var_lines)} "
            f"have values)",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)