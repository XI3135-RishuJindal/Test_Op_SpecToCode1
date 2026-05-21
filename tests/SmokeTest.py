"""
Upgrade Validation Tests: Update Project Documentation to Reflect Modernized Stack

These tests verify that the documentation upgrade succeeded by checking:
1. Key documentation files exist and are accessible
2. Outdated/deprecated references have been removed or replaced
3. New stack references are present in the correct locations
4. Documentation structure is consistent with the modernized stack
"""

import os
import re
import glob
import unittest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _read(rel_path: str) -> str:
    """Return the contents of a file relative to the repo root, or '' if missing."""
    full = os.path.join(REPO_ROOT, rel_path)
    if not os.path.isfile(full):
        return ""
    with open(full, encoding="utf-8") as fh:
        return fh.read()


def _file_exists(rel_path: str) -> bool:
    return os.path.isfile(os.path.join(REPO_ROOT, rel_path))


def _find_docs_files(extensions=(".md", ".rst", ".txt")) -> list:
    """Return all documentation files under the repo root."""
    found = []
    for ext in extensions:
        found.extend(
            glob.glob(os.path.join(REPO_ROOT, "**", f"*{ext}"), recursive=True)
        )
    # Exclude hidden dirs and common non-doc dirs
    excluded_dirs = {".git", "node_modules", "__pycache__", ".tox", "venv", ".venv"}
    return [
        f for f in found
        if not any(part in excluded_dirs for part in f.split(os.sep))
    ]


# ---------------------------------------------------------------------------
# Test Suite
# ---------------------------------------------------------------------------

class TestDocumentationUpgradeSucceeded(unittest.TestCase):
    """Validates that the documentation has been updated to reflect the modernized stack."""

    # ------------------------------------------------------------------
    # 1. Core documentation files exist
    # ------------------------------------------------------------------

    def test_readme_exists(self):
        """README.md must exist at the repository root after the upgrade."""
        self.assertTrue(
            _file_exists("README.md"),
            "README.md not found at repository root — documentation upgrade may be incomplete.",
        )

    def test_readme_is_non_empty(self):
        """README.md must contain substantive content."""
        content = _read("README.md")
        self.assertGreater(
            len(content.strip()),
            50,
            "README.md appears to be empty or near-empty after the upgrade.",
        )

    def test_docs_directory_exists(self):
        """A docs/ directory (or equivalent) should be present."""
        docs_dir = os.path.join(REPO_ROOT, "docs")
        # Accept docs/ OR a non-empty set of .md files at root as valid documentation presence
        has_docs_dir = os.path.isdir(docs_dir)
        has_root_md = len(glob.glob(os.path.join(REPO_ROOT, "*.md"))) > 0
        self.assertTrue(
            has_docs_dir or has_root_md,
            "Neither a docs/ directory nor any Markdown files were found — "
            "documentation upgrade may not have been applied.",
        )

    # ------------------------------------------------------------------
    # 2. README reflects the modernized stack (version assertion)
    # ------------------------------------------------------------------

    def test_readme_does_not_reference_placeholder_todo_stack(self):
        """README.md must not contain unresolved TODO placeholders for stack versions."""
        content = _read("README.md")
        # Unresolved placeholders left by the upgrade task indicate incomplete work
        forbidden_patterns = [
            r"TODO.*version",
            r"TODO.*stack",
            r"TODO.*runtime",
            r"TODO.*framework",
            r"\[INSERT.*VERSION\]",
            r"\[INSERT.*STACK\]",
        ]
        for pattern in forbidden_patterns:
            self.assertIsNone(
                re.search(pattern, content, re.IGNORECASE),
                f"README.md contains an unresolved placeholder matching '{pattern}'. "
                "The documentation upgrade is incomplete.",
            )

    def test_readme_contains_stack_section(self):
        """README.md should contain a section describing the technology stack."""
        content = _read("README.md")
        stack_keywords = [
            "stack", "technology", "runtime", "language", "framework",
            "requirements", "prerequisites", "built with",
        ]
        found = any(kw.lower() in content.lower() for kw in stack_keywords)
        self.assertTrue(
            found,
            "README.md does not appear to contain any stack/technology description. "
            "The modernized stack documentation may be missing.",
        )

    def test_readme_contains_setup_instructions(self):
        """README.md must contain setup or installation instructions."""
        content = _read("README.md")
        setup_keywords = [
            "install", "setup", "getting started", "quick start",
            "how to run", "usage", "build",
        ]
        found = any(kw.lower() in content.lower() for kw in setup_keywords)
        self.assertTrue(
            found,
            "README.md does not contain setup/installation instructions. "
            "The documentation upgrade should include updated onboarding steps.",
        )

    # ------------------------------------------------------------------
    # 3. Deprecated references removed across all documentation
    # ------------------------------------------------------------------

    def test_no_docs_reference_deprecated_placeholder_versions(self):
        """
        No documentation file should contain obviously stale placeholder version strings
        that indicate the upgrade task was not completed.
        """
        stale_patterns = [
            r"\bTODO\b.*\bversion\b",
            r"\bFIXME\b.*\bversion\b",
            r"\[OLD[_ ]VERSION\]",
            r"\[DEPRECATED[_ ]STACK\]",
            r"\bpre-modernization\b",
        ]
        violations = []
        for filepath in _find_docs_files():
            rel = os.path.relpath(filepath, REPO_ROOT)
            try:
                with open(filepath, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            for pattern in stale_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    violations.append(f"{rel} matches pattern '{pattern}'")

        self.assertEqual(
            violations,
            [],
            "The following documentation files contain stale/deprecated placeholder "
            "references that should have been removed by the upgrade:\n"
            + "\n".join(violations),
        )

    def test_no_docs_contain_conflicting_old_and_new_stack_markers(self):
        """
        Documentation files must not simultaneously reference both 'old stack' and
        'new stack' markers, which would indicate an incomplete migration.
        """
        old_markers = ["old-stack", "legacy-stack", "pre-modernization", "old_runtime"]
        new_markers = ["modernized", "new stack", "updated stack", "current stack"]

        conflicts = []
        for filepath in _find_docs_files():
            rel = os.path.relpath(filepath, REPO_ROOT)
            try:
                with open(filepath, encoding="utf-8", errors="replace") as fh:
                    text = fh.read().lower()
            except OSError:
                continue
            has_old = any(m in text for m in old_markers)
            has_new = any(m in text for m in new_markers)
            if has_old and has_new:
                conflicts.append(rel)

        self.assertEqual(
            conflicts,
            [],
            "The following files appear to reference both old and new stack markers, "
            "suggesting an incomplete documentation migration:\n"
            + "\n".join(conflicts),
        )

    # ------------------------------------------------------------------
    # 4. New configuration / contribution documentation present
    # ------------------------------------------------------------------

    def test_contribution_guide_exists_or_readme_covers_contributing(self):
        """A CONTRIBUTING guide or equivalent section must exist after the upgrade."""
        has_contributing_file = (
            _file_exists("CONTRIBUTING.md")
            or _file_exists("CONTRIBUTING.rst")
            or _file_exists("docs/CONTRIBUTING.md")
            or _file_exists(".github/CONTRIBUTING.md")
        )
        readme_covers_contributing = "contribut" in _read("README.md").lower()
        self.assertTrue(
            has_contributing_file or readme_covers_contributing,
            "No CONTRIBUTING guide found and README.md does not mention contributing. "
            "The upgrade tasks require contribution guidelines to be updated.",
        )

    def test_no_broken_internal_markdown_links(self):
        """
        Internal Markdown links (e.g. [text](./path)) must point to files that exist.
        Broken links indicate documentation was restructured without updating references.
        """
        broken = []
        md_files = [f for f in _find_docs_files(extensions=(".md",))]
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)#\s]+)\)')

        for filepath in md_files:
            rel_file = os.path.relpath(filepath, REPO_ROOT)
            try:
                with open(filepath, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
            except OSError:
                continue
            for _label, target in link_pattern.findall(text):
                # Skip external URLs and anchors-only
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                # Resolve relative to the file's directory
                base_dir = os.path.dirname(filepath)
                resolved = os.path.normpath(os.path.join(base_dir, target))
                if not os.path.exists(resolved):
                    broken.append(f"{rel_file} → {target}")

        self.assertEqual(
            broken,
            [],
            "The following internal documentation links are broken after the upgrade. "
            "Update or remove them:\n" + "\n".join(broken),
        )

    # ------------------------------------------------------------------
    # 5. Documentation upgrade completeness marker (optional but recommended)
    # ------------------------------------------------------------------

    def test_readme_does_not_say_wip_or_draft_in_title(self):
        """
        The README title must not indicate it is a work-in-progress or draft,
        which would signal the documentation upgrade was not finalised.
        """
        content = _read("README.md")
        first_lines = content.strip().splitlines()[:5]
        for line in first_lines:
            self.assertNotRegex(
                line,
                re.compile(r"\b(WIP|DRAFT|DO NOT USE|OUTDATED)\b", re.IGNORECASE),
                f"README.md title area contains a WIP/DRAFT marker: '{line.strip()}'. "
                "The documentation upgrade must be finalised before merging.",
            )

    def test_all_docs_files_are_utf8_readable(self):
        """All documentation files must be readable as UTF-8 without errors."""
        unreadable = []
        for filepath in _find_docs_files():
            rel = os.path.relpath(filepath, REPO_ROOT)
            try:
                with open(filepath, encoding="utf-8") as fh:
                    fh.read()
            except (UnicodeDecodeError, OSError) as exc:
                unreadable.append(f"{rel}: {exc}")

        self.assertEqual(
            unreadable,
            [],
            "The following documentation files cannot be read as UTF-8. "
            "Fix encoding issues introduced during the upgrade:\n"
            + "\n".join(unreadable),
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)