# Documentation Upgrade Validation Tests
# Validates that developer and operational documentation update succeeded
# Run with: python -m pytest test_docs_upgrade_validation.py -v

import os
import re
import glob
import subprocess
import pytest
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration — adjust these paths to match your repository layout
# ---------------------------------------------------------------------------

REPO_ROOT = Path(os.environ.get("REPO_ROOT", Path(__file__).parent.parent))
DOCS_DIR = REPO_ROOT / os.environ.get("DOCS_DIR", "docs")
README_PATH = REPO_ROOT / "README.md"

# Files that MUST exist after the documentation upgrade
REQUIRED_DOC_FILES = [
    DOCS_DIR / "development.md",
    DOCS_DIR / "operations" / "runbook.md",
    DOCS_DIR / "operations" / "deployment.md",
    DOCS_DIR / "operations" / "rollback.md",
    DOCS_DIR / "configuration.md",
    DOCS_DIR / "onboarding.md",
    README_PATH,
]

# Sections that MUST appear in the developer onboarding / README
REQUIRED_ONBOARDING_SECTIONS = [
    "## Prerequisites",
    "## Setup",
    "## Running",
    "## Testing",
]

# Sections that MUST appear in the operational runbook
REQUIRED_RUNBOOK_SECTIONS = [
    "## Deployment",
    "## Rollback",
    "## Incident Response",
    "## Monitoring",
]

# Sections that MUST appear in the configuration reference
REQUIRED_CONFIG_SECTIONS = [
    "## Configuration",
]

# Placeholder strings that indicate documentation is still a stub / TODO
FORBIDDEN_PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bPLACEHOLDER\b",
    r"\bLOREM IPSUM\b",
    r"<INSERT",
    r"\[TBD\]",
    r"\[TBC\]",
]

# Deprecated section headings that must NOT appear in updated docs
DEPRECATED_SECTION_PATTERNS = [
    r"## Legacy Setup",
    r"## Old Deployment Process",
    r"## Deprecated Configuration",
]


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def read_file(path: Path) -> str:
    """Return file contents as a string, or empty string if file is missing."""
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def collect_all_doc_files() -> list:
    """Return all Markdown files under DOCS_DIR and the repo root README."""
    md_files = list(DOCS_DIR.rglob("*.md")) if DOCS_DIR.exists() else []
    if README_PATH.exists():
        md_files.append(README_PATH)
    rst_files = list(DOCS_DIR.rglob("*.rst")) if DOCS_DIR.exists() else []
    return md_files + rst_files


# ---------------------------------------------------------------------------
# 1. Version / upgrade completion assertion
#    The "version" for a documentation upgrade is validated by confirming
#    that a docs/VERSION or docs/CHANGELOG entry records the modernization
#    update, and that the docs directory itself exists and is non-empty.
# ---------------------------------------------------------------------------

class TestUpgradeVersionAssertion:
    """Verify that the documentation upgrade has been applied at the target state."""

    def test_docs_directory_exists(self):
        """DOCS_DIR must exist — created as part of the upgrade."""
        assert DOCS_DIR.exists(), (
            f"Documentation directory '{DOCS_DIR}' does not exist. "
            "The documentation upgrade has not been applied."
        )

    def test_docs_directory_is_not_empty(self):
        """DOCS_DIR must contain at least one document file."""
        doc_files = collect_all_doc_files()
        assert len(doc_files) > 0, (
            f"No documentation files found under '{DOCS_DIR}'. "
            "The documentation upgrade produced no output."
        )

    def test_changelog_or_version_records_modernization(self):
        """
        A CHANGELOG.md or docs/VERSION file must reference the modernization
        update so that the upgrade can be traced.
        """
        candidate_paths = [
            REPO_ROOT / "CHANGELOG.md",
            REPO_ROOT / "CHANGELOG",
            DOCS_DIR / "CHANGELOG.md",
            DOCS_DIR / "VERSION",
            REPO_ROOT / "VERSION",
        ]
        found_reference = False
        keywords = ["modernization", "documentation update", "docs upgrade", "doc update"]
        for path in candidate_paths:
            if path.exists():
                content = path.read_text(encoding="utf-8").lower()
                if any(kw in content for kw in keywords):
                    found_reference = True
                    break

        assert found_reference, (
            "No CHANGELOG or VERSION file records the documentation modernization update. "
            "Add an entry referencing 'documentation update' or 'modernization' to confirm "
            "the upgrade is complete."
        )

    def test_readme_exists_at_repo_root(self):
        """A README.md must exist at the repository root."""
        assert README_PATH.exists(), (
            f"README.md not found at '{README_PATH}'. "
            "The documentation upgrade must produce a root-level README."
        )


# ---------------------------------------------------------------------------
# 2. Required documentation files exist
# ---------------------------------------------------------------------------

class TestRequiredDocumentationFilesExist:
    """All documentation files mandated by the upgrade spec must be present."""

    @pytest.mark.parametrize("doc_path", REQUIRED_DOC_FILES)
    def test_required_file_exists(self, doc_path):
        assert doc_path.exists(), (
            f"Required documentation file '{doc_path}' is missing. "
            "Ensure the documentation upgrade created this file."
        )

    @pytest.mark.parametrize("doc_path", REQUIRED_DOC_FILES)
    def test_required_file_is_not_empty(self, doc_path):
        if not doc_path.exists():
            pytest.skip(f"File '{doc_path}' does not exist — covered by existence test.")
        content = doc_path.read_text(encoding="utf-8").strip()
        assert len(content) > 0, (
            f"Required documentation file '{doc_path}' is empty. "
            "The upgrade must populate this file with actual content."
        )


# ---------------------------------------------------------------------------
# 3. Critical application paths — required sections present
# ---------------------------------------------------------------------------

class TestOnboardingDocumentationSections:
    """Developer onboarding documentation must contain all required sections."""

    @pytest.fixture(scope="class")
    def onboarding_content(self):
        candidates = [
            DOCS_DIR / "onboarding.md",
            DOCS_DIR / "development.md",
            README_PATH,
        ]
        for path in candidates:
            if path.exists():
                content = path.read_text(encoding="utf-8")
                if len(content.strip()) > 0:
                    return content
        return ""

    @pytest.mark.parametrize("section_heading", REQUIRED_ONBOARDING_SECTIONS)
    def test_onboarding_section_present(self, onboarding_content, section_heading):
        assert section_heading.lower() in onboarding_content.lower(), (
            f"Required onboarding section '{section_heading}' not found. "
            "The updated developer documentation must include this section."
        )


class TestRunbookSections:
    """Operational runbook must contain all required sections."""

    @pytest.fixture(scope="class")
    def runbook_content(self):
        runbook_path = DOCS_DIR / "operations" / "runbook.md"
        if runbook_path.exists():
            return runbook_path.read_text(encoding="utf-8")
        # Fallback: search for any file named runbook
        for path in DOCS_DIR.rglob("runbook*"):
            if path.is_file():
                return path.read_text(encoding="utf-8")
        return ""

    @pytest.mark.parametrize("section_heading", REQUIRED_RUNBOOK_SECTIONS)
    def test_runbook_section_present(self, runbook_content, section_heading):
        if not runbook_content:
            pytest.skip("Runbook file not found — covered by file existence test.")
        assert section_heading.lower() in runbook_content.lower(), (
            f"Required runbook section '{section_heading}' not found. "
            "The updated operational documentation must include this section."
        )


class TestConfigurationDocumentationSections:
    """Configuration reference must contain all required sections."""

    @pytest.fixture(scope="class")
    def config_content(self):
        config_path = DOCS_DIR / "configuration.md"
        if config_path.exists():
            return config_path.read_text(encoding="utf-8")
        return ""

    @pytest.mark.parametrize("section_heading", REQUIRED_CONFIG_SECTIONS)
    def test_config_section_present(self, config_content, section_heading):
        if not config_content:
            pytest.skip("configuration.md not found — covered by file existence test.")
        assert section_heading.lower() in config_content.lower(), (
            f"Required configuration section '{section_heading}' not found. "
            "The updated configuration reference must include this section."
        )

    def test_configuration_doc_references_current_keys(self, config_content):
        """Configuration doc must not reference only legacy/deprecated key names."""
        if not config_content:
            pytest.skip("configuration.md not found.")
        deprecated_key_patterns = [
            r"OLD_CONFIG_KEY",
            r"LEGACY_DB_URL",
            r"DEPRECATED_API_KEY",
        ]
        for pattern in deprecated_key_patterns:
            assert not re.search(pattern, config_content, re.IGNORECASE), (
                f"Deprecated configuration key pattern '{pattern}' found in configuration.md. "
                "Replace with the current configuration key names introduced by the upgrade."
            )


# ---------------------------------------------------------------------------
# 4. Deprecated content must not appear in updated documentation
# ---------------------------------------------------------------------------

class TestDeprecatedContentRemoved:
    """Deprecated sections and patterns must not appear in updated documentation."""

    @pytest.mark.parametrize("doc_path", REQUIRED_DOC_FILES)
    @pytest.mark.parametrize("deprecated_pattern", DEPRECATED_SECTION_PATTERNS)
    def test_deprecated_section_not_present(self, doc_path, deprecated_pattern):
        if not doc_path.exists():
            pytest.skip(f"File '{doc_path}' does not exist.")
        content = read_file(doc_path)
        assert not re.search(deprecated_pattern, content, re.IGNORECASE), (
            f"Deprecated section '{deprecated_pattern}' found in '{doc_path}'. "
            "Remove deprecated sections as part of the documentation upgrade."
        )

    @pytest.mark.parametrize("doc_path", REQUIRED_DOC_FILES)
    @pytest.mark.parametrize("placeholder_pattern", FORBIDDEN_PLACEHOLDER_PATTERNS)
    def test_no_placeholder_content(self, doc_path, placeholder_pattern):
        if not doc_path.exists():
            pytest.skip(f"File '{doc_path}' does not exist.")
        content = read_file(doc_path)
        assert not re.search(placeholder_pattern, content, re.IGNORECASE), (
            f"Placeholder text matching '{placeholder_pattern}' found in '{doc_path}'. "
            "All placeholder content must be replaced with accurate information "
            "before the documentation upgrade is considered complete."
        )


# ---------------------------------------------------------------------------
# 5. New configuration keys introduced by the upgrade load without errors
#    (Validates that any new docs-related CI config files are well-formed)
# ---------------------------------------------------------------------------

class TestNewConfigurationFilesValid:
    """New configuration files introduced by the upgrade must be valid."""

    def test_markdownlinkcheck_config_valid_json_if_present(self):
        """If a markdown-link-check config was added, it must be valid JSON."""
        import json
        candidate_paths = [
            REPO_ROOT / ".mlc_config.json",
            REPO_ROOT / ".markdown-link-check.json",
            DOCS_DIR / ".mlc_config.json",
        ]
        for path in candidate_paths:
            if path.exists():
                try:
                    with open(path, encoding="utf-8") as f:
                        json.load(f)
                except json.JSONDecodeError as exc:
                    pytest.fail(
                        f"markdown-link-check config '{path}' is not valid JSON: {exc}"
                    )

    def test_ci_docs_pipeline_config_exists_if_ci_present(self):
        """
        If a CI directory exists, a docs-related pipeline step must be present
        (broken-link check or docs build step).
        """
        ci_dirs = [
            REPO_ROOT / ".github" / "workflows",
            REPO_ROOT / ".gitlab-ci.yml",
            REPO_ROOT / ".circleci",
            REPO_ROOT / "Jenkinsfile",
        ]
        ci_present = any(
            (p.exists() for p in ci_dirs)
        )
        if not ci_present:
            pytest.skip("No CI configuration directory detected — skipping CI docs step check.")

        docs_ci_keywords = [
            "markdown-link-check",
            "link-check",
            "docs",
            "documentation",
        ]
        found = False
        for ci_dir in ci_dirs:
            if not ci_dir.exists():
                continue
            if ci_dir.is_dir():
                for ci_file in ci_dir.rglob("*"):
                    if ci_file.is_file():
                        content = read_file(ci_file).lower()
                        if any(kw in content for kw in docs_ci_keywords):
                            found = True
                            break
            elif ci_dir.is_file():
                content = read_file(ci_dir).lower()
                if any(kw in content for kw in docs_ci_keywords):
                    found = True
            if found:
                break

        assert found, (
            "No CI pipeline configuration references a documentation or link-check step. "
            "The upgrade spec requires adding a broken-link check step to CI."
        )


# ---------------------------------------------------------------------------
# 6. Broken internal links check (no external HTTP calls)
# ---------------------------------------------------------------------------

class TestInternalDocumentLinks:
    """Internal cross-references within documentation must resolve to existing files."""

    def _extract_internal_links(self, content: str, source_file: Path) -> list:
        """Return list of (link_text, resolved_path) for non-HTTP markdown links."""
        pattern = re.compile(r'\[([^\]]*)\]\(([^)]+)\)')
        links = []
        for match in pattern.finditer(content):
            href = match.group(2).strip()
            # Skip external links and anchors-only
            if href.startswith("http://") or href.startswith("https://"):
                continue
            if href.startswith("#"):
                continue
            # Strip anchor fragment
            href_path = href.split("#")[0]
            if not href_path:
                continue
            resolved = (source_file.parent / href_path).resolve()
            links.append((match.group(1), resolved))
        return links

    def test_internal_links_resolve(self):
        """All internal Markdown links must point to files that exist."""
        broken = []
        for doc_file in collect_all_doc_files():
            content = read_file(doc_file)
            for link_text, resolved_path in self._extract_internal_links(content, doc_file):
                if not resolved_path.exists():
                    broken.append(
                        f"  '{doc_file}' → '{link_text}' → '{resolved_path}' (not found)"
                    )
        assert not broken, (
            "Broken internal documentation links detected after upgrade:\n"
            + "\n".join(broken)
        )


# ---------------------------------------------------------------------------
# 7. Dry-run validation — setup instructions are syntactically executable
# ---------------------------------------------------------------------------

class TestSetupInstructionsSyntax:
    """
    Code blocks in developer documentation must contain syntactically valid
    shell commands (basic sanity check — not full execution).
    """

    OBVIOUSLY_INVALID_PATTERNS = [
        r"^\s*\$\s*$",          # bare dollar sign with no command
        r"<your[- _]",          # unfilled template placeholders like <your-token>
        r"\{\{.*\}\}",          # unfilled template variables like {{variable}}
    ]

    def _extract_code_blocks(self, content: str) -> list:
        """Return list of code block contents from Markdown fenced blocks."""
        pattern = re.compile(r'```(?:bash|sh|shell|console)?\n(.*?)```', re.DOTALL)
        return [m.group(1) for m in pattern.finditer(content)]

    @pytest.mark.parametrize("doc_path", [
        DOCS_DIR / "onboarding.md",
        DOCS_DIR / "development.md",
        README_PATH,
    ])
    def test_code_blocks_have_no_unfilled_placeholders(self, doc_path):
        if not doc_path.exists():
            pytest.skip(f"'{doc_path}' does not exist.")
        content = read_file(doc_path)
        code_blocks = self._extract_code_blocks(content)
        violations = []
        for block in code_blocks:
            for pattern in self.OBVIOUSLY_INVALID_PATTERNS:
                for line in block.splitlines():
                    if re.search(pattern, line):
                        violations.append(f"  Pattern '{pattern}' matched line: {line!r}")
        assert not violations, (
            f"Unfilled placeholders or invalid commands found in code blocks in '{doc_path}':\n"
            + "\n".join(violations)
        )


# ---------------------------------------------------------------------------
# 8. Acceptance criteria completeness check
# ---------------------------------------------------------------------------

class TestAcceptanceCriteriaDocumented:
    """The upgrade spec requires acceptance criteria to be defined and documented."""

    def test_acceptance_criteria_file_or_section_exists(self):
        """
        An acceptance criteria definition must exist either as a dedicated file
        or as a section within the main docs README or contributing guide.
        """
        candidate_files = [
            DOCS_DIR / "ACCEPTANCE_CRITERIA.md",
            DOCS_DIR / "contributing.md",
            DOCS_DIR / "CONTRIBUTING.md",
            REPO_ROOT / "CONTRIBUTING.md",
            README_PATH,
        ]
        acceptance_keywords = [
            "acceptance criteria",
            "definition of done",
            "completeness criteria",
            "documentation complete",
        ]
        found = False
        for path in candidate_files:
            if path.exists():
                content = path.read_text(encoding="utf-8").lower()
                if any(kw in content for kw in acceptance_keywords):
                    found = True
                    break
        assert found, (
            "No acceptance criteria definition found in documentation. "
            "The upgrade spec requires documenting what 'documentation complete' means "
            "(e.g., in CONTRIBUTING.md or README.md)."
        )