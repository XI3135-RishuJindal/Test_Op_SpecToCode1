# Documentation Upgrade Validation Tests
# Validates that project documentation has been updated to reflect the modernized stack
# Run with: python -m pytest test_docs_upgrade_validation.py -v

import os
import re
import glob
import pathlib
import unittest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).parent.resolve()

# Collect all markdown / rst / txt documentation files in the repository
DOC_EXTENSIONS = {".md", ".rst", ".txt"}
DOC_DIRS = [".", "docs", "doc", "documentation"]

def _find_doc_files():
    found = []
    for d in DOC_DIRS:
        base = REPO_ROOT / d
        if not base.exists():
            continue
        for ext in DOC_EXTENSIONS:
            found.extend(base.glob(f"**/*{ext}"))
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for f in found:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def _read(path: pathlib.Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _all_doc_text() -> str:
    return "\n".join(_read(f) for f in _find_doc_files())


# ---------------------------------------------------------------------------
# Patterns that indicate OUTDATED / pre-modernization content
# These should NOT appear in documentation after the upgrade.
# ---------------------------------------------------------------------------

DEPRECATED_PATTERNS = [
    # Generic "old stack" markers that writers sometimes leave behind
    r"\bold[_\s-]?stack\b",
    r"\blegacy[_\s-]?stack\b",
    r"\bpre[_\s-]?modernization\b",
    r"\bdeprecated[_\s-]?version\b",
    # Placeholder / TODO markers that must be resolved before the upgrade is complete
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bXXX\b",
    # Common stale-version sentinels (adjust if your project uses specific old versions)
    r"\bEOL\b",
]

# ---------------------------------------------------------------------------
# Patterns that MUST be present after the upgrade
# ---------------------------------------------------------------------------

REQUIRED_PATTERNS = [
    # The modernized-stack section heading or keyword
    r"modernized[_\s-]?stack|modernized stack",
    # A CHANGELOG entry for the documentation update
    r"(?i)(changelog|release[_\s-]?notes)",
    # At least one version reference (e.g. "v1.2", "1.2.3", "version 3")
    r"v?\d+\.\d+",
]

# ---------------------------------------------------------------------------
# Required files
# ---------------------------------------------------------------------------

REQUIRED_FILES = [
    "README.md",
    "CHANGELOG.md",
]


class TestDocumentationUpgradeValidation(unittest.TestCase):
    """Validates that the documentation upgrade to reflect the modernized stack
    has been completed successfully."""

    # ------------------------------------------------------------------
    # 1. Required files exist
    # ------------------------------------------------------------------

    def test_required_documentation_files_exist(self):
        """README.md and CHANGELOG.md must exist at the repository root."""
        missing = []
        for filename in REQUIRED_FILES:
            path = REPO_ROOT / filename
            if not path.exists():
                missing.append(filename)
        self.assertEqual(
            missing,
            [],
            msg=(
                f"Required documentation files are missing after the upgrade: "
                f"{missing}. These files must be created as part of the "
                f"documentation modernization."
            ),
        )

    # ------------------------------------------------------------------
    # 2. Documentation files are non-empty
    # ------------------------------------------------------------------

    def test_required_documentation_files_are_non_empty(self):
        """README.md and CHANGELOG.md must contain substantive content."""
        for filename in REQUIRED_FILES:
            path = REPO_ROOT / filename
            if not path.exists():
                self.skipTest(f"{filename} does not exist — covered by existence test.")
            content = _read(path).strip()
            self.assertGreater(
                len(content),
                50,
                msg=(
                    f"{filename} appears to be empty or nearly empty "
                    f"({len(content)} chars). The upgrade requires substantive "
                    f"documentation content."
                ),
            )

    # ------------------------------------------------------------------
    # 3. No deprecated / stale patterns remain
    # ------------------------------------------------------------------

    def test_no_deprecated_patterns_in_documentation(self):
        """Deprecated or pre-modernization markers must not appear in docs."""
        violations = []
        for doc_file in _find_doc_files():
            content = _read(doc_file)
            for pattern in DEPRECATED_PATTERNS:
                matches = re.findall(pattern, content, flags=re.IGNORECASE)
                if matches:
                    rel = doc_file.relative_to(REPO_ROOT)
                    violations.append(
                        f"  {rel}: pattern '{pattern}' matched {len(matches)} time(s)"
                    )
        self.assertEqual(
            violations,
            [],
            msg=(
                "The following deprecated/stale patterns were found in documentation "
                "after the upgrade. They must be removed or replaced:\n"
                + "\n".join(violations)
            ),
        )

    # ------------------------------------------------------------------
    # 4. Required modernized-stack content is present
    # ------------------------------------------------------------------

    def test_required_modernized_content_present(self):
        """Documentation must contain markers indicating the modernized stack."""
        combined = _all_doc_text()
        missing_patterns = []
        for pattern in REQUIRED_PATTERNS:
            if not re.search(pattern, combined, flags=re.IGNORECASE):
                missing_patterns.append(pattern)
        self.assertEqual(
            missing_patterns,
            [],
            msg=(
                "The following required content patterns were NOT found anywhere in "
                "the documentation after the upgrade:\n"
                + "\n".join(f"  - {p}" for p in missing_patterns)
                + "\nEnsure the modernized stack is described in the docs."
            ),
        )

    # ------------------------------------------------------------------
    # 5. README describes the modernized stack
    # ------------------------------------------------------------------

    def test_readme_references_modernized_stack(self):
        """README.md must explicitly reference the modernized stack."""
        readme = REPO_ROOT / "README.md"
        if not readme.exists():
            self.skipTest("README.md does not exist — covered by existence test.")
        content = _read(readme)
        self.assertTrue(
            re.search(r"modernized[_\s-]?stack|modernized stack", content, re.IGNORECASE),
            msg=(
                "README.md does not reference the modernized stack. "
                "Update README.md to describe the current technology stack."
            ),
        )

    # ------------------------------------------------------------------
    # 6. CHANGELOG contains an entry for the documentation update
    # ------------------------------------------------------------------

    def test_changelog_contains_documentation_update_entry(self):
        """CHANGELOG.md must contain an entry for the documentation modernization."""
        changelog = REPO_ROOT / "CHANGELOG.md"
        if not changelog.exists():
            self.skipTest("CHANGELOG.md does not exist — covered by existence test.")
        content = _read(changelog)
        has_doc_entry = re.search(
            r"(documentation|docs)[^\n]*(moderniz|updat|stack)",
            content,
            flags=re.IGNORECASE,
        )
        self.assertIsNotNone(
            has_doc_entry,
            msg=(
                "CHANGELOG.md does not appear to contain an entry for the "
                "documentation modernization. Add a changelog entry describing "
                "the documentation update."
            ),
        )

    # ------------------------------------------------------------------
    # 7. No broken internal links (relative markdown links)
    # ------------------------------------------------------------------

    def test_internal_markdown_links_resolve(self):
        """Relative links in markdown files must point to existing files."""
        broken = []
        for doc_file in _find_doc_files():
            if doc_file.suffix.lower() != ".md":
                continue
            content = _read(doc_file)
            # Match [text](relative/path) — skip http/https/mailto/anchors
            for match in re.finditer(r"\[([^\]]*)\]\(([^)]+)\)", content):
                href = match.group(2).strip()
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                # Strip anchor fragment
                href_path = href.split("#")[0]
                if not href_path:
                    continue
                target = (doc_file.parent / href_path).resolve()
                if not target.exists():
                    rel = doc_file.relative_to(REPO_ROOT)
                    broken.append(f"  {rel}: broken link → '{href}'")
        self.assertEqual(
            broken,
            [],
            msg=(
                "The following internal links in documentation are broken after "
                "the upgrade:\n" + "\n".join(broken)
            ),
        )

    # ------------------------------------------------------------------
    # 8. Documentation files are discoverable (at least one doc file exists)
    # ------------------------------------------------------------------

    def test_at_least_one_documentation_file_exists(self):
        """At least one documentation file must be present in the repository."""
        doc_files = _find_doc_files()
        self.assertGreater(
            len(doc_files),
            0,
            msg=(
                "No documentation files (.md, .rst, .txt) were found in the "
                "repository. The upgrade requires documentation to be present."
            ),
        )

    # ------------------------------------------------------------------
    # 9. Version references are consistent (no conflicting version strings)
    # ------------------------------------------------------------------

    def test_version_references_are_present_in_readme(self):
        """README.md must contain at least one explicit version reference."""
        readme = REPO_ROOT / "README.md"
        if not readme.exists():
            self.skipTest("README.md does not exist — covered by existence test.")
        content = _read(readme)
        version_matches = re.findall(r"v?\d+\.\d+(?:\.\d+)?", content)
        self.assertGreater(
            len(version_matches),
            0,
            msg=(
                "README.md contains no version references (e.g. '1.2.3' or 'v2.0'). "
                "The modernized stack documentation must specify the target versions "
                "of the runtime, language, or key dependencies."
            ),
        )

    # ------------------------------------------------------------------
    # 10. Upgrade target version assertion
    # ------------------------------------------------------------------

    def test_documentation_reflects_latest_stable_target(self):
        """Documentation must indicate it targets the 'latest stable' version
        of the stack, as specified in the upgrade goal."""
        combined = _all_doc_text()
        has_latest = re.search(
            r"latest[_\s-]?stable|current[_\s-]?stable|up[_\s-]?to[_\s-]?date",
            combined,
            flags=re.IGNORECASE,
        )
        self.assertIsNotNone(
            has_latest,
            msg=(
                "No documentation file references 'latest stable', 'current stable', "
                "or 'up-to-date' stack. The upgrade goal requires documentation to "
                "reflect the latest stable versions. Update the docs accordingly."
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)