import os
import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


class TestCIBaselineUpgradeValidation(unittest.TestCase):
    """
    Upgrade validation tests for: "Validate CI baseline end-to-end and define operational runbook".

    This validates that the repository now contains the required CI baseline and runbook documentation,
    and that CI workflow/config changes are present and consistent with the upgrade goal.
    """

    def test_target_upgrade_goal_matches_expected(self):
        # Exact target "version" context is not applicable for this upgrade.
        # Enforce that our expected goal text is present in docs to prevent drift.
        baseline_doc = REPO_ROOT / "docs" / "ci-baseline.md"
        runbook_doc = REPO_ROOT / "docs" / "runbook-ci.md"

        self.assertTrue(
            baseline_doc.exists(),
            "docs/ci-baseline.md must exist to document the CI baseline definition and validation results.",
        )
        self.assertTrue(
            runbook_doc.exists(),
            "docs/runbook-ci.md must exist to provide the CI operational runbook.",
        )

        baseline_text = baseline_doc.read_text(encoding="utf-8", errors="replace")
        runbook_text = runbook_doc.read_text(encoding="utf-8", errors="replace")

        # Ensure both documents reflect the upgrade's intent (baseline validation + operational runbook).
        self.assertRegex(
            baseline_text,
            re.compile(r"\bCI\b.*\bbaseline\b", re.IGNORECASE | re.DOTALL),
            "docs/ci-baseline.md should clearly describe the CI baseline.",
        )
        self.assertRegex(
            baseline_text,
            re.compile(r"\bend-?to-?end\b|\bE2E\b", re.IGNORECASE),
            "docs/ci-baseline.md should include end-to-end validation criteria or results.",
        )
        self.assertRegex(
            runbook_text,
            re.compile(r"\brunbook\b|\btroubleshoot(ing)?\b|\bon-?call\b|\bescalat", re.IGNORECASE),
            "docs/runbook-ci.md should provide operational guidance (runbook/troubleshooting/escalation).",
        )

    def test_ci_workflows_present_and_parseable(self):
        workflows_dir = REPO_ROOT / ".github" / "workflows"
        self.assertTrue(
            workflows_dir.exists() and workflows_dir.is_dir(),
            ".github/workflows/ must exist (CI baseline inventory depends on it).",
        )

        workflow_files = sorted(
            [p for p in workflows_dir.glob("*.yml")] + [p for p in workflows_dir.glob("*.yaml")]
        )
        self.assertGreater(
            len(workflow_files),
            0,
            "At least one workflow file (.yml/.yaml) must exist in .github/workflows/.",
        )

        # Minimal parse: ensure each workflow has a name and 'on:' trigger. Avoid adding YAML deps.
        for wf in workflow_files:
            text = wf.read_text(encoding="utf-8", errors="replace")
            self.assertRegex(
                text,
                re.compile(r"(?m)^\s*name\s*:\s*\S+"),
                f"{wf} must define a workflow name.",
            )
            self.assertRegex(
                text,
                re.compile(r"(?m)^\s*on\s*:\s*"),
                f"{wf} must define triggers (on:).",
            )

    def test_critical_ci_paths_defined_in_baseline_doc(self):
        """
        Critical paths for this upgrade are the operational/validation paths:
        - baseline success criteria are defined
        - required checks / branch protection are documented
        - artifacts/log retention/access documented
        - run links or evidence of execution documented
        """
        baseline_doc = REPO_ROOT / "docs" / "ci-baseline.md"
        self.assertTrue(baseline_doc.exists(), "docs/ci-baseline.md must exist.")

        text = baseline_doc.read_text(encoding="utf-8", errors="replace")

        # Baseline success criteria must be defined.
        self.assertRegex(
            text,
            re.compile(r"\bsuccess criteria\b|\bdefinition of done\b|\bgreen\b", re.IGNORECASE),
            "docs/ci-baseline.md must define baseline success criteria (what 'end-to-end green' means).",
        )

        # Required checks / branch protection should be recorded.
        self.assertRegex(
            text,
            re.compile(r"\brequired (status )?checks\b|\bbranch protection\b", re.IGNORECASE),
            "docs/ci-baseline.md must document required checks and/or branch protection rules.",
        )

        # Artifact/log retention and accessibility should be documented.
        self.assertRegex(
            text,
            re.compile(r"\bartifact\b|\bretention\b|\blogs?\b|\bdownload\b", re.IGNORECASE),
            "docs/ci-baseline.md must document artifact/log retention and accessibility.",
        )

        # Evidence of end-to-end execution (run links, durations, outcomes).
        self.assertRegex(
            text,
            re.compile(r"\brun\b.*\blink\b|\bhttps?://\S+\b|\bduration\b|\bpass(ed)?\b|\bfail(ed)?\b", re.IGNORECASE),
            "docs/ci-baseline.md should include evidence of executions (run links/durations/outcomes).",
        )

    def test_deprecated_ci_doc_paths_removed_or_redirected(self):
        """
        Deprecated API equivalent for this upgrade: prior doc locations/names should not be used anymore.
        Enforce that old/ambiguous doc names do not appear as the canonical source.

        We consider these deprecated/undesired:
        - docs/ci.md (ambiguous)
        - docs/runbook.md (too generic)
        """
        deprecated_paths = [
            REPO_ROOT / "docs" / "ci.md",
            REPO_ROOT / "docs" / "runbook.md",
        ]

        for p in deprecated_paths:
            self.assertFalse(
                p.exists(),
                f"Deprecated/ambiguous doc file should not exist after upgrade: {p}. "
                f"Use docs/ci-baseline.md and docs/runbook-ci.md instead.",
            )

        # Also ensure README references the new docs (replacement works).
        readme_candidates = [REPO_ROOT / "README.md", REPO_ROOT / "docs" / "README.md"]
        readme = next((p for p in readme_candidates if p.exists()), None)
        self.assertIsNotNone(
            readme,
            "A README.md or docs/README.md must exist to link to CI baseline and runbook docs.",
        )
        readme_text = readme.read_text(encoding="utf-8", errors="replace")
        self.assertRegex(
            readme_text,
            re.compile(r"docs/ci-baseline\.md", re.IGNORECASE),
            f"{readme} must link to docs/ci-baseline.md.",
        )
        self.assertRegex(
            readme_text,
            re.compile(r"docs/runbook-ci\.md", re.IGNORECASE),
            f"{readme} must link to docs/runbook-ci.md.",
        )

    def test_new_configuration_keys_load_without_errors(self):
        """
        New configuration keys introduced by this upgrade are documentation/config expectations:
        - docs/ci-baseline.md exists and includes required sections
        - docs/runbook-ci.md exists and includes required sections
        This test treats them as "config" inputs that must be loadable/readable.
        """
        for doc in (REPO_ROOT / "docs" / "ci-baseline.md", REPO_ROOT / "docs" / "runbook-ci.md"):
            self.assertTrue(doc.exists(), f"Required doc is missing: {doc}")
            # Read should not raise; also validate non-empty.
            text = doc.read_text(encoding="utf-8", errors="strict")
            self.assertGreater(
                len(text.strip()),
                0,
                f"{doc} must not be empty.",
            )

        # Ensure repository does not declare containerization for this upgrade (None).
        # If a Dockerfile exists, it should not be required/mentioned as part of CI baseline upgrade.
        dockerfile = REPO_ROOT / "Dockerfile"
        if dockerfile.exists():
            # Allow Dockerfile to exist historically, but ensure baseline doc doesn't *require* it.
            baseline_text = (REPO_ROOT / "docs" / "ci-baseline.md").read_text(encoding="utf-8", errors="replace")
            self.assertNotRegex(
                baseline_text,
                re.compile(r"\brequires?\b.*\bdocker\b|\bdocker\b.*\brequired\b", re.IGNORECASE),
                "Upgrade context specifies Containerized: None; baseline docs must not require Docker to run CI.",
            )

    def test_runtime_version_assertion_is_not_applicable(self):
        """
        Version assertion requirement: this upgrade explicitly does NOT change language/runtime/build tool,
        and the context provides no target runtime/framework version.

        Enforce that CI baseline docs explicitly state versions are N/A for this task to prevent
        future confusion and accidental coupling to a runtime upgrade.
        """
        baseline_doc = REPO_ROOT / "docs" / "ci-baseline.md"
        self.assertTrue(baseline_doc.exists(), "docs/ci-baseline.md must exist.")
        text = baseline_doc.read_text(encoding="utf-8", errors="replace")

        self.assertRegex(
            text,
            re.compile(r"\bversions?\b.*\bN/A\b|\bEOL\b.*\bN/A\b|\bCVE\b.*\bN/A\b", re.IGNORECASE),
            "docs/ci-baseline.md must indicate that versions/EOL/CVEs are N/A for this upgrade (no runtime target).",
        )


if __name__ == "__main__":
    # Allow running directly: python -m unittest -q
    unittest.main()