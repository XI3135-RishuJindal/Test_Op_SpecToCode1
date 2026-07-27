import os
import re
import unittest
from pathlib import Path


class TestBaselineInventoryUpgradeValidation(unittest.TestCase):
    """
    Upgrade-validation tests for the baseline-inventory modernization effort.

    These tests verify the deliverable artifact exists and is well-formed, and that
    its required categories are present with explicit values (including "unknown/TODO"
    when applicable), as required by the spec's acceptance criteria.

    Note: The provided upgrade context does not specify any concrete runtime/framework
    target versions nor provide code-level critical paths/deprecated APIs/config keys.
    These tests therefore validate the upgrade deliverable (inventory artifact) itself.
    """

    INVENTORY_PATH = Path("docs/modernization/baseline-inventory.md")

    def _read_inventory(self) -> str:
        self.assertTrue(
            self.INVENTORY_PATH.exists(),
            f"Missing required inventory artifact at {self.INVENTORY_PATH.as_posix()}",
        )
        content = self.INVENTORY_PATH.read_text(encoding="utf-8", errors="replace")
        self.assertTrue(content.strip(), "Inventory artifact exists but is empty")
        return content

    def test_inventory_artifact_exists_and_is_human_readable_markdown(self):
        content = self._read_inventory()
        # Basic markdown heuristics: should contain at least one header or list/table.
        self.assertTrue(
            any(token in content for token in ["# ", "## ", "- ", "|"]),
            "Inventory artifact does not appear to be human-readable Markdown (no headers/lists/tables found).",
        )

    def test_inventory_contains_required_categories_with_non_empty_values(self):
        content = self._read_inventory().lower()

        # Required categories per spec: language, runtime(s), build tool(s), frameworks/major libraries.
        # Acceptance criteria: all fields present; unknowns explicitly marked as unknown/TODO.
        required_category_patterns = {
            "language": [
                r"\blanguage\b",
            ],
            "runtime": [
                r"\bruntime\b",
                r"\bruntimes\b",
            ],
            "build tool": [
                r"\bbuild tool\b",
                r"\bbuild tools\b",
                r"\bbuild tooling\b",
            ],
            "frameworks": [
                r"\bframework\b",
                r"\bframeworks\b",
                r"\bmajor libraries\b",
            ],
        }

        missing = []
        for category, patterns in required_category_patterns.items():
            if not any(re.search(p, content) for p in patterns):
                missing.append(category)

        self.assertFalse(
            missing,
            f"Inventory artifact is missing required categories: {', '.join(missing)}",
        )

        # Ensure that for each category, there is some version/value indication OR explicit unknown/TODO marker.
        # This is intentionally flexible to accommodate different authoring styles.
        def category_has_value_or_unknown(category_regex: str) -> bool:
            # Look for a nearby "version" or value line, or a table row, or explicit unknown/TODO.
            # Search within a window after the category heading/mention.
            m = re.search(category_regex, content)
            if not m:
                return False
            start = m.start()
            window = content[start : min(len(content), start + 800)]
            return bool(
                re.search(r"\bversion\b\s*[:\-]?\s*\S+", window)
                or re.search(r"\bunknown\b", window)
                or re.search(r"\btodo\b", window)
                or re.search(r"\|\s*(language|runtime|build|framework)", window)
            )

        self.assertTrue(
            category_has_value_or_unknown(r"\blanguage\b"),
            "Language category present but does not include a version/value or explicit unknown/TODO marker nearby.",
        )
        self.assertTrue(
            category_has_value_or_unknown(r"\bruntime(s)?\b"),
            "Runtime category present but does not include a version/value or explicit unknown/TODO marker nearby.",
        )
        self.assertTrue(
            category_has_value_or_unknown(r"\bbuild tool(s|ing)?\b"),
            "Build tool category present but does not include a version/value or explicit unknown/TODO marker nearby.",
        )
        self.assertTrue(
            category_has_value_or_unknown(r"\bframework(s)?\b|\bmajor libraries\b"),
            "Frameworks/Major libraries category present but does not include a version/value or explicit unknown/TODO marker nearby.",
        )

    def test_inventory_includes_explicit_unknown_or_todo_for_any_unresolved_values(self):
        content = self._read_inventory()
        # Because the upgrade context explicitly states versions are unknown at this stage,
        # the artifact must explicitly mark unknowns as unknown/TODO per spec.
        self.assertRegex(
            content.lower(),
            r"\b(unknown|todo)\b",
            "Inventory artifact must explicitly mark unknown/unresolved values as 'unknown' or 'TODO' per spec.",
        )

    def test_readme_links_to_inventory_or_inventory_notes_absence_of_readme(self):
        inventory = self._read_inventory().lower()
        readme_candidates = [
            Path("README.md"),
            Path("README.MD"),
            Path("README"),
            Path("readme.md"),
        ]
        readme_path = next((p for p in readme_candidates if p.exists()), None)

        if readme_path is None:
            # Spec: Add link from README OR note “no README present” in the inventory doc.
            self.assertRegex(
                inventory,
                r"\bno readme\b|\breadme\b.*\bnot\b.*\bpresent\b",
                "No README found; inventory must note that no README is present (per spec).",
            )
            return

        readme = readme_path.read_text(encoding="utf-8", errors="replace").lower()

        # Require a link or reference to the inventory path.
        # Allow either markdown link or plain path mention.
        expected_path = self.INVENTORY_PATH.as_posix().lower()
        self.assertTrue(
            expected_path in readme,
            f"README must link to or reference {expected_path} (per spec).",
        )

    def test_inventory_check_is_reproducible_in_ci_environment(self):
        # This test is a proxy for the spec's CI review check: it must be deterministic and file-based.
        # Ensure the inventory path is relative and does not depend on environment-specific absolute paths.
        self.assertFalse(
            str(self.INVENTORY_PATH).startswith(("/", "\\")),
            "Inventory path must be repository-relative to be reproducible in CI.",
        )
        # Ensure the file can be read without requiring special environment.
        _ = self._read_inventory()


if __name__ == "__main__":
    unittest.main()