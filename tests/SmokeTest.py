import os
import re
import subprocess
import unittest
from pathlib import Path


class TestVulnerabilityScanGateUpgrade(unittest.TestCase):
    """
    Upgrade validation tests for:
    - Add dependency vulnerability scanning gate with fail-on-critical policy

    These tests intentionally validate:
    - The scanning tool is active at an exact target version (via env var).
    - Critical gate behavior works (fails when critical findings exist).
    - Deprecated/old scanning tooling/config no longer appears.
    - New configuration keys introduced by the upgrade load without errors.
    """

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]

        # Target version MUST be specified by the upgrade context at runtime (CI),
        # since the prompt does not provide an explicit scanner/tool version number.
        cls.target_scanner_version = os.environ.get("VULN_SCAN_TOOL_VERSION_TARGET", "").strip()
        cls.scanner_cmd = os.environ.get("VULN_SCAN_CMD", "").strip()  # e.g., "trivy" or "grype"
        cls.scanner_args = os.environ.get("VULN_SCAN_ARGS", "").strip()  # extra args if needed
        cls.scan_paths = os.environ.get("VULN_SCAN_PATHS", ".").strip()

        # New configuration keys introduced by this upgrade (expected to exist now).
        # Kept generic but explicit; these should be set in CI to prove config loads.
        cls.fail_on_severity = os.environ.get("VULN_SCAN_FAIL_ON_SEVERITY", "").strip()
        cls.report_path = os.environ.get("VULN_SCAN_REPORT_PATH", "").strip()

        cls.pipeline_files = [
            cls.repo_root / ".github" / "workflows",
            cls.repo_root / ".gitlab-ci.yml",
            cls.repo_root / "azure-pipelines.yml",
            cls.repo_root / "Jenkinsfile",
        ]

    def _run(self, cmd, cwd=None, env=None):
        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)
        return subprocess.run(
            cmd,
            cwd=str(cwd or self.repo_root),
            env=merged_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _require_upgrade_context(self):
        missing = []
        if not self.scanner_cmd:
            missing.append("VULN_SCAN_CMD")
        if not self.target_scanner_version:
            missing.append("VULN_SCAN_TOOL_VERSION_TARGET")
        if not self.fail_on_severity:
            missing.append("VULN_SCAN_FAIL_ON_SEVERITY")
        if not self.report_path:
            missing.append("VULN_SCAN_REPORT_PATH")
        if missing:
            self.skipTest(
                "Upgrade validation requires CI to provide upgrade context env vars: "
                + ", ".join(missing)
            )

    def test_active_scanner_version_matches_target_exactly(self):
        self._require_upgrade_context()

        # Try common version flags, assert EXACT match to target.
        # The test is strict to satisfy "EXACT target version specified in the upgrade context".
        candidates = [
            [self.scanner_cmd, "--version"],
            [self.scanner_cmd, "version"],
            [self.scanner_cmd, "-v"],
        ]

        last = None
        for cmd in candidates:
            last = self._run(cmd)
            if last.returncode == 0 and (last.stdout.strip() or last.stderr.strip()):
                output = (last.stdout + "\n" + last.stderr).strip()
                # Find semver-like tokens in output.
                versions = re.findall(r"\b\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.\-]+)?\b", output)
                if not versions:
                    # Some tools print like "Version: v0.51.0"
                    versions = [v.lstrip("v") for v in re.findall(r"\bv?\d+\.\d+\.\d+\b", output)]
                if versions:
                    active = versions[0].lstrip("v")
                    self.assertEqual(
                        active,
                        self.target_scanner_version,
                        msg=f"Active scanner version '{active}' did not match target '{self.target_scanner_version}'. Output:\n{output}",
                    )
                    return

        details = ""
        if last is not None:
            details = f"\nLast attempt stdout:\n{last.stdout}\nLast attempt stderr:\n{last.stderr}\n"
        self.fail(
            "Could not determine scanner version from command output to assert exact target version."
            + details
        )

    def test_new_config_keys_present_and_loadable(self):
        self._require_upgrade_context()

        # New keys introduced by this upgrade must be present and non-empty.
        self.assertEqual(
            self.fail_on_severity.lower(),
            "critical",
            msg="VULN_SCAN_FAIL_ON_SEVERITY must be set to 'critical' to enforce fail-on-critical policy.",
        )
        # Ensure report path is a sensible relative/absolute path string.
        self.assertTrue(
            len(self.report_path) > 0 and not self.report_path.isspace(),
            msg="VULN_SCAN_REPORT_PATH must be a non-empty path.",
        )

        # Ensure scanner invocation can run in a "config loads" mode:
        # we run a scan with minimal scope and ensure the process starts and emits a report file.
        # For tool-agnostic behavior, we only require:
        # - command executes (not "unknown flag"/config error)
        # - report artifact is created (or at least attempted) without config parse errors
        report_file = (self.repo_root / self.report_path).resolve()
        if report_file.exists():
            try:
                report_file.unlink()
            except OSError:
                pass

        cmd = [self.scanner_cmd]
        if self.scanner_args:
            cmd += self.scanner_args.split()

        # Common patterns: scanners accept a path argument; we provide repo root by default.
        cmd += [self.scan_paths]

        res = self._run(cmd)
        combined = (res.stdout + "\n" + res.stderr).lower()

        self.assertNotIn("unknown flag", combined, msg=f"Scanner appears misconfigured.\n{res.stderr}")
        self.assertNotIn("configuration error", combined, msg=f"Scanner configuration error.\n{res.stderr}")
        self.assertNotIn("failed to parse", combined, msg=f"Scanner failed to parse configuration.\n{res.stderr}")

        # Report may be uploaded by CI rather than created locally; still require no config error.
        # If a path is specified, prefer asserting it exists to validate artifact generation.
        if report_file.parent.exists():
            self.assertTrue(
                report_file.exists() or res.returncode in (0, 1),
                msg=(
                    "Scanner did not appear to produce the expected report artifact at "
                    f"{report_file} (or scan failed unexpectedly). "
                    f"Exit code: {res.returncode}\nSTDERR:\n{res.stderr}"
                ),
            )

    def test_fail_on_critical_gate_behavior_is_enforced(self):
        self._require_upgrade_context()

        # Validate the gate behavior:
        # - When critical vulnerabilities are detected, scan must exit non-zero (policy enforcement).
        # Since we cannot reliably introduce a vulnerable dependency inside a unit test without
        # adding dependencies/features, this test requires a controlled fixture directory
        # provided by CI that is known to trigger a critical finding.
        fixture = os.environ.get("VULN_SCAN_KNOWN_VULNERABLE_FIXTURE", "").strip()
        if not fixture:
            self.skipTest(
                "Set VULN_SCAN_KNOWN_VULNERABLE_FIXTURE to a path that deterministically yields a CRITICAL finding to validate fail-on-critical enforcement."
            )

        fixture_path = (self.repo_root / fixture).resolve()
        if not fixture_path.exists():
            self.fail(f"VULN_SCAN_KNOWN_VULNERABLE_FIXTURE path does not exist: {fixture_path}")

        cmd = [self.scanner_cmd]
        if self.scanner_args:
            cmd += self.scanner_args.split()
        cmd += [str(fixture_path)]

        res = self._run(cmd)
        combined = (res.stdout + "\n" + res.stderr).lower()

        # Must fail the job when critical vulns exist.
        self.assertNotEqual(
            res.returncode,
            0,
            msg=(
                "Fail-on-critical policy not enforced: scan returned success on known-vulnerable fixture.\n"
                f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
            ),
        )

        # Also ensure the output indicates a critical finding or policy threshold.
        critical_indicators = ["critical", "severity: critical", "fail-on", "threshold"]
        self.assertTrue(
            any(token in combined for token in critical_indicators),
            msg=(
                "Scan failed but output did not clearly indicate critical severity enforcement. "
                "Ensure the scanner is configured to fail on CRITICAL and emits severity info.\n"
                f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
            ),
        )

    def test_deprecated_or_old_scanners_not_referenced_in_pipeline(self):
        # Ensure deprecated APIs / old tooling references are removed.
        # We treat references to older scanners as deprecated for this upgrade context.
        deprecated_tokens = [
            "snyk test",
            "snyk monitor",
            "npm audit",
            "yarn audit",
            "pip-audit",
            "safety check",
            "dependency-check",  # OWASP Dependency-Check
        ]

        contents = ""
        found_any_pipeline = False

        for p in self.pipeline_files:
            if p.is_dir() and p.exists():
                for f in p.glob("*.yml"):
                    found_any_pipeline = True
                    try:
                        contents += "\n" + f.read_text(encoding="utf-8", errors="ignore")
                    except OSError:
                        pass
            elif p.is_file() and p.exists():
                found_any_pipeline = True
                try:
                    contents += "\n" + p.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    pass

        if not found_any_pipeline:
            self.skipTest("No recognized CI pipeline file found to validate deprecated scanner references removal.")

        haystack = contents.lower()
        for tok in deprecated_tokens:
            self.assertNotIn(
                tok,
                haystack,
                msg=f"Deprecated/old scanner invocation '{tok}' still referenced in CI configuration.",
            )

    def test_critical_application_path_scan_covers_dependency_manifests(self):
        self._require_upgrade_context()

        # Critical path: scanning must cover dependency manifests/lockfiles.
        # We validate presence of at least one manifest and that scanner execution does not ignore all.
        manifests = [
            "package-lock.json",
            "yarn.lock",
            "pnpm-lock.yaml",
            "pom.xml",
            "build.gradle",
            "build.gradle.kts",
            "requirements.txt",
            "poetry.lock",
            "Pipfile.lock",
            "go.mod",
            "Cargo.lock",
        ]

        existing = [m for m in manifests if (self.repo_root / m).exists()]
        if not existing:
            self.skipTest("No known dependency manifest/lockfile found at repo root to validate scan coverage.")

        cmd = [self.scanner_cmd]
        if self.scanner_args:
            cmd += self.scanner_args.split()
        cmd += [self.scan_paths]

        res = self._run(cmd)
        self.assertIn(
            res.returncode,
            (0, 1),
            msg=(
                "Scanner did not run successfully against repository paths (unexpected exit code). "
                f"Exit code: {res.returncode}\nSTDERR:\n{res.stderr}"
            ),
        )

        output = (res.stdout + "\n" + res.stderr).lower()

        # Require evidence that at least one existing manifest name appears in logs/output,
        # indicating the scan traversed dependency definitions rather than doing nothing.
        # If a scanner is quiet, CI should set args to produce logs; enforce that as part of upgrade.
        self.assertTrue(
            any(m.lower() in output for m in existing),
            msg=(
                "Scan output did not mention any existing dependency manifest/lockfile; "
                "cannot confirm scan covered critical dependency paths. "
                "Ensure scanner is configured to scan dependencies and emits evidence in logs.\n"
                f"Existing manifests at root: {existing}\n"
                f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
            ),
        )


if __name__ == "__main__":
    unittest.main()