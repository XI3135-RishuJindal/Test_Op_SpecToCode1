import unittest
from pathlib import Path
import re
import yaml


class TestCodeQLUpgradeValidation(unittest.TestCase):
    """
    Upgrade validation tests for enabling GitHub CodeQL SAST in CI with baseline queries.

    These tests verify:
    - The CodeQL workflow uses the expected (target) action versions.
    - Critical CI paths exist (workflow triggers, init/analyze/upload sequence, permissions).
    - Deprecated APIs/usages are not present (e.g., old CodeQL action major versions).
    - New configuration keys required by the upgrade load without errors.
    """

    TARGET_CODEQL_ACTION_MAJOR = "v3"
    WORKFLOW_PATH = Path(".github/workflows/codeql.yml")

    def _load_codeql_workflow(self):
        self.assertTrue(self.WORKFLOW_PATH.exists(), f"Missing workflow file: {self.WORKFLOW_PATH}")
        raw = self.WORKFLOW_PATH.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(raw)
        except Exception as e:
            self.fail(f"Failed to parse {self.WORKFLOW_PATH} as YAML: {e}")
        self.assertIsInstance(data, dict, "Workflow YAML did not parse to an object")
        return raw, data

    def _iter_steps(self, workflow_dict):
        jobs = workflow_dict.get("jobs") or {}
        for job_id, job in jobs.items():
            steps = (job or {}).get("steps") or []
            for idx, step in enumerate(steps):
                yield job_id, idx, step

    def test_codeql_workflow_exists_and_parses(self):
        _, wf = self._load_codeql_workflow()
        self.assertIn("jobs", wf, "Workflow missing 'jobs' section")

    def test_target_codeql_action_version_is_active_exact_major(self):
        """
        Version assertion: ensure we are using the target CodeQL action major version.
        Target: latest stable -> actions major v3.
        """
        _, wf = self._load_codeql_workflow()

        uses_values = []
        for _, _, step in self._iter_steps(wf):
            if isinstance(step, dict) and "uses" in step:
                uses_values.append(step["uses"])

        self.assertTrue(uses_values, "No 'uses' steps found; expected GitHub Actions steps using CodeQL actions")

        codeql_uses = [u for u in uses_values if isinstance(u, str) and u.startswith("github/codeql-action/")]
        self.assertTrue(codeql_uses, "No github/codeql-action/* steps found in workflow")

        bad_versions = []
        expected_prefix = f"github/codeql-action/"
        for u in codeql_uses:
            # Expect: github/codeql-action/<action>@v3 (or v3.x.x if pinned)
            if "@" not in u:
                bad_versions.append(u)
                continue
            action, ref = u.split("@", 1)
            self.assertTrue(action.startswith(expected_prefix), f"Unexpected CodeQL action path: {action}")
            if not (ref == self.TARGET_CODEQL_ACTION_MAJOR or ref.startswith(self.TARGET_CODEQL_ACTION_MAJOR + ".")):
                bad_versions.append(u)

        self.assertFalse(
            bad_versions,
            "CodeQL actions not at target version. Expected major v3 for latest stable. Offenders:\n"
            + "\n".join(bad_versions),
        )

    def test_deprecated_codeql_action_versions_not_used(self):
        """
        Deprecated API/usages: ensure old major versions are not present (v1/v2).
        """
        raw, _ = self._load_codeql_workflow()
        self.assertNotRegex(raw, r"github/codeql-action/[^@\s]+@v1(\W|$)", "Deprecated CodeQL action v1 found")
        self.assertNotRegex(raw, r"github/codeql-action/[^@\s]+@v2(\W|$)", "Deprecated CodeQL action v2 found")

    def test_workflow_triggers_include_push_pull_request_and_schedule(self):
        """
        Critical application path: ensure the workflow runs on PRs, pushes, and on a schedule.
        """
        _, wf = self._load_codeql_workflow()

        on_block = wf.get("on")
        self.assertIsNotNone(on_block, "Workflow missing required 'on' triggers")

        # YAML can parse "on" into dict; in rare cases it may be a string/list.
        self.assertIsInstance(on_block, (dict, list, str), "Unexpected type for 'on' block")

        if isinstance(on_block, dict):
            self.assertIn("push", on_block, "Missing 'push' trigger in CodeQL workflow")
            self.assertIn("pull_request", on_block, "Missing 'pull_request' trigger in CodeQL workflow")
            self.assertIn("schedule", on_block, "Missing 'schedule' trigger in CodeQL workflow")
            schedule = on_block.get("schedule")
            self.assertIsInstance(schedule, list, "'on.schedule' must be a list")
            self.assertTrue(len(schedule) >= 1, "Expected at least one scheduled run entry under 'on.schedule'")
            self.assertTrue(
                any(isinstance(x, dict) and "cron" in x and str(x["cron"]).strip() for x in schedule),
                "Expected a non-empty cron entry in 'on.schedule'",
            )
        else:
            self.fail("Workflow 'on' block must be a mapping that includes push/pull_request/schedule for this upgrade")

    def test_permissions_include_security_events_write_and_contents_read(self):
        """
        Critical application path: ensure required permissions are declared.
        """
        _, wf = self._load_codeql_workflow()

        perms = wf.get("permissions")
        self.assertIsInstance(perms, dict, "Workflow must declare top-level 'permissions' as a mapping")

        self.assertIn("security-events", perms, "Missing 'permissions.security-events' required for CodeQL upload")
        self.assertEqual(
            str(perms.get("security-events")).strip(),
            "write",
            "permissions.security-events must be 'write' for CodeQL result upload",
        )

        self.assertIn("contents", perms, "Missing 'permissions.contents' (should be minimal 'read')")
        self.assertEqual(
            str(perms.get("contents")).strip(),
            "read",
            "permissions.contents should be 'read' for minimal permissions",
        )

    def test_codeql_steps_present_init_and_analyze(self):
        """
        Critical application path: ensure the workflow actually runs CodeQL (init + analyze).
        """
        _, wf = self._load_codeql_workflow()

        init_steps = []
        analyze_steps = []
        upload_steps = []

        for job_id, _, step in self._iter_steps(wf):
            if not isinstance(step, dict):
                continue
            uses = step.get("uses")
            if not isinstance(uses, str):
                continue
            if uses.startswith("github/codeql-action/init@"):
                init_steps.append((job_id, step))
            if uses.startswith("github/codeql-action/analyze@"):
                analyze_steps.append((job_id, step))
            if uses.startswith("github/codeql-action/upload-sarif@"):
                upload_steps.append((job_id, step))

        self.assertTrue(init_steps, "Missing CodeQL init step (github/codeql-action/init@...)")
        self.assertTrue(analyze_steps, "Missing CodeQL analyze step (github/codeql-action/analyze@...)")
        self.assertTrue(
            analyze_steps or upload_steps,
            "Expected analyze and/or upload-sarif step to publish results",
        )

    def test_baseline_query_suite_security_extended_configured(self):
        """
        New configuration key introduced/required by upgrade: query suite selection.
        Verify CodeQL init uses queries: security-extended.
        """
        _, wf = self._load_codeql_workflow()

        found_init = False
        found_queries_security_extended = False

        for _, _, step in self._iter_steps(wf):
            if not isinstance(step, dict):
                continue
            uses = step.get("uses")
            if not (isinstance(uses, str) and uses.startswith("github/codeql-action/init@")):
                continue

            found_init = True
            with_block = step.get("with") or {}
            self.assertIsInstance(with_block, dict, "CodeQL init step 'with' must be a mapping when present")

            # Accept either queries or query-suite configuration style as string containing security-extended.
            queries_val = with_block.get("queries")
            query_suite_val = with_block.get("query-suite")  # allow alternate naming if used
            config_file = with_block.get("config-file")

            if isinstance(queries_val, str) and "security-extended" in queries_val:
                found_queries_security_extended = True
            if isinstance(query_suite_val, str) and "security-extended" in query_suite_val:
                found_queries_security_extended = True

            # If config-file is used, ensure it exists and is valid YAML.
            if isinstance(config_file, str) and config_file.strip():
                cfg_path = Path(config_file)
                self.assertTrue(cfg_path.exists(), f"CodeQL config-file referenced but not found: {config_file}")
                try:
                    cfg_data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
                except Exception as e:
                    self.fail(f"Failed to parse CodeQL config file {config_file}: {e}")
                self.assertIsInstance(cfg_data, dict, "CodeQL config file did not parse to an object")

                # If a config file is used, ensure it contains the intended suite selection somewhere.
                cfg_text = cfg_path.read_text(encoding="utf-8")
                if "security-extended" in cfg_text:
                    found_queries_security_extended = True

        self.assertTrue(found_init, "No CodeQL init step found to validate query suite configuration")
        self.assertTrue(
            found_queries_security_extended,
            "Baseline query suite 'security-extended' not configured. "
            "Expected in init.with.queries or init.with.query-suite or referenced config-file.",
        )

    def test_no_legacy_codeql_workflow_keys_or_third_party_actions(self):
        """
        Deprecated/incorrect configuration guardrails:
        - Ensure the workflow does not use legacy CodeQL action repos.
        """
        raw, _ = self._load_codeql_workflow()
        self.assertNotIn("github/codeql-action@",
                         raw,
                         "Unexpected legacy usage 'github/codeql-action@...' (missing sub-action like init/analyze)")
        self.assertNotRegex(raw, r"\bcodeql-action\b(?!/)", "Unexpected ambiguous 'codeql-action' reference")

    def test_workflow_has_failure_on_execution_errors_not_alerts(self):
        """
        CI gate requirement: fail workflow on CodeQL execution errors.
        Pragmatic validation: analyze step should not explicitly ignore errors.
        """
        _, wf = self._load_codeql_workflow()

        analyze_steps = []
        for _, _, step in self._iter_steps(wf):
            if isinstance(step, dict) and isinstance(step.get("uses"), str) and step["uses"].startswith("github/codeql-action/analyze@"):
                analyze_steps.append(step)

        self.assertTrue(analyze_steps, "No analyze step found for validation")

        for step in analyze_steps:
            with_block = step.get("with") or {}
            if with_block:
                self.assertIsInstance(with_block, dict, "Analyze step 'with' must be a mapping when present")
                # Prevent configurations that would mask execution issues.
                # (CodeQL action uses 'upload' and 'output' etc; no universal ignore-errors key, but ensure no explicit continue-on-error at step level.)
            self.assertNotIn(
                "continue-on-error",
                step,
                "Analyze step must not set 'continue-on-error'; workflow should fail on CodeQL execution errors",
            )


if __name__ == "__main__":
    unittest.main()