import os
import re
import unittest
from pathlib import Path

try:
    import yaml  # type: ignore
except Exception as e:  # pragma: no cover
    yaml = None
    _yaml_import_error = e
else:
    _yaml_import_error = None


class TestCiArtifactPublishingUpgrade(unittest.TestCase):
    """
    Upgrade validation tests for CI configuration changes:
    - Publishes SBOM artifacts
    - Publishes security scan artifacts
    - Uses upload-artifact action at the exact expected version
    - Avoids deprecated set-output
    - New configuration keys for retention/compression load without errors
    """

    # Target upgrade versions / expectations (override via env in CI if needed)
    TARGET_UPLOAD_ARTIFACT_VERSION = os.getenv("TARGET_UPLOAD_ARTIFACT_VERSION", "v4")
    TARGET_RETENTION_DAYS = int(os.getenv("TARGET_ARTIFACT_RETENTION_DAYS", "30"))

    # Common artifact naming patterns (override via env in CI if repo uses different names)
    SBOM_ARTIFACT_NAME_REGEX = re.compile(os.getenv("SBOM_ARTIFACT_NAME_REGEX", r"(?i)\bsbom\b"))
    SECURITY_ARTIFACT_NAME_REGEX = re.compile(os.getenv("SECURITY_ARTIFACT_NAME_REGEX", r"(?i)\b(security|scan|sast|dependency|vuln)\b"))

    def setUp(self) -> None:
        if yaml is None:
            self.fail(f"PyYAML is required to run these tests but is not available: {_yaml_import_error}")

        self.repo_root = Path(__file__).resolve().parents[1]
        self.workflow_dir = self.repo_root / ".github" / "workflows"

        if not self.workflow_dir.exists():
            self.skipTest("No .github/workflows directory found; CI toolchain not detected in repo.")

        self.workflow_files = sorted(
            p for p in self.workflow_dir.glob("*.yml")
            if p.is_file()
        ) + sorted(
            p for p in self.workflow_dir.glob("*.yaml")
            if p.is_file()
        )

        if not self.workflow_files:
            self.skipTest("No workflow YAML files found under .github/workflows.")

        self.workflows = []
        for wf in self.workflow_files:
            content = wf.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
            self.workflows.append((wf, content, data))

    def _iter_steps(self):
        for wf_path, wf_text, wf_data in self.workflows:
            jobs = (wf_data or {}).get("jobs") or {}
            for job_name, job in jobs.items():
                steps = (job or {}).get("steps") or []
                for idx, step in enumerate(steps):
                    yield wf_path, job_name, idx, step, wf_text

    def _find_upload_artifact_steps(self):
        uploads = []
        for wf_path, job_name, idx, step, _ in self._iter_steps():
            uses = (step or {}).get("uses")
            if isinstance(uses, str) and uses.startswith("actions/upload-artifact@"):
                uploads.append((wf_path, job_name, idx, step))
        return uploads

    def _assert_exact_action_version(self, uses_value: str, expected_tag: str):
        # Exact version requirement: must be ...@v4 (or the specific tag passed)
        # This rejects floating/branch refs like @main and older majors.
        if "@" not in uses_value:
            self.fail(f"Invalid uses value without @: {uses_value}")
        action, tag = uses_value.split("@", 1)
        self.assertEqual(action, "actions/upload-artifact", f"Unexpected action for artifact upload: {uses_value}")
        self.assertEqual(tag, expected_tag, f"Artifact upload action must be pinned to exact target version {expected_tag}")

    def test_runtime_framework_version_target_is_active_exact(self):
        """
        Version assertion required by upgrade validation:
        Here the "runtime/framework" is the GitHub Action used to publish artifacts.
        """
        upload_steps = self._find_upload_artifact_steps()
        if not upload_steps:
            self.fail("No actions/upload-artifact steps found. Upgrade requires publishing SBOM and security scan artifacts.")

        for wf_path, job_name, idx, step in upload_steps:
            uses = step.get("uses")
            self.assertIsInstance(uses, str, f"{wf_path}:{job_name}:steps[{idx}] 'uses' must be a string")
            self._assert_exact_action_version(uses, self.TARGET_UPLOAD_ARTIFACT_VERSION)

    def test_critical_paths_sbom_and_security_scan_artifacts_are_uploaded(self):
        """
        Critical paths: SBOM and security scan artifacts are actually uploaded in CI config.
        This checks for at least one upload step that looks like SBOM and one that looks like security scan output.
        """
        upload_steps = self._find_upload_artifact_steps()
        if not upload_steps:
            self.fail("No actions/upload-artifact steps found. Cannot validate artifact publishing.")

        sbom_uploads = []
        sec_uploads = []

        for wf_path, job_name, idx, step in upload_steps:
            with_cfg = (step or {}).get("with") or {}
            name = with_cfg.get("name")
            path = with_cfg.get("path")

            name_str = str(name) if name is not None else ""
            path_str = str(path) if path is not None else ""

            # If name is absent, infer from path.
            combined = f"{name_str} {path_str}".strip()

            if self.SBOM_ARTIFACT_NAME_REGEX.search(combined):
                sbom_uploads.append((wf_path, job_name, idx, combined))
            if self.SECURITY_ARTIFACT_NAME_REGEX.search(combined):
                sec_uploads.append((wf_path, job_name, idx, combined))

        if not sbom_uploads:
            self.fail(
                "No SBOM artifact upload detected. Expected an actions/upload-artifact step with name/path matching SBOM.\n"
                f"Hint: set SBOM_ARTIFACT_NAME_REGEX env var if your naming differs."
            )
        if not sec_uploads:
            self.fail(
                "No security scan artifact upload detected. Expected an actions/upload-artifact step with name/path matching a scan report.\n"
                f"Hint: set SECURITY_ARTIFACT_NAME_REGEX env var if your naming differs."
            )

    def test_deprecated_set_output_api_not_present(self):
        """
        Deprecated API check: ensure no workflow still uses the deprecated ::set-output command.
        """
        offenders = []
        for wf_path, wf_text, _ in self.workflows:
            if "::set-output" in wf_text:
                offenders.append(str(wf_path))
        if offenders:
            self.fail("Deprecated GitHub Actions '::set-output' detected in: " + ", ".join(offenders))

    def test_new_configuration_keys_load_and_are_set_for_artifact_upload(self):
        """
        New config keys introduced/expected by this upgrade:
        - retention-days (artifact retention configuration)
        - compression-level (optional, but supported by upload-artifact@v4)
        Validate they parse and are present where applicable.
        """
        upload_steps = self._find_upload_artifact_steps()
        if not upload_steps:
            self.fail("No actions/upload-artifact steps found. Cannot validate new configuration keys.")

        missing_retention = []
        invalid_retention = []
        compression_type_issues = []

        for wf_path, job_name, idx, step in upload_steps:
            with_cfg = (step or {}).get("with") or {}
            # retention-days should be configured to ensure retention behavior is explicit.
            if "retention-days" not in with_cfg:
                missing_retention.append(f"{wf_path}:{job_name}:steps[{idx}]")
            else:
                val = with_cfg.get("retention-days")
                try:
                    # YAML may parse numbers as int; or may keep as str.
                    retention_val = int(str(val))
                except Exception:
                    invalid_retention.append(f"{wf_path}:{job_name}:steps[{idx}]={val!r}")
                else:
                    if retention_val <= 0:
                        invalid_retention.append(f"{wf_path}:{job_name}:steps[{idx}]={retention_val}")
                    # If an explicit target is provided, assert it matches.
                    self.assertEqual(
                        retention_val,
                        self.TARGET_RETENTION_DAYS,
                        f"{wf_path}:{job_name}:steps[{idx}] retention-days must equal target {self.TARGET_RETENTION_DAYS}"
                    )

            # compression-level is optional but must be valid if present
            if "compression-level" in with_cfg:
                cval = with_cfg.get("compression-level")
                try:
                    c_int = int(str(cval))
                except Exception:
                    compression_type_issues.append(f"{wf_path}:{job_name}:steps[{idx}] compression-level={cval!r} (not an int)")
                else:
                    if c_int < 0 or c_int > 9:
                        compression_type_issues.append(f"{wf_path}:{job_name}:steps[{idx}] compression-level={c_int} (must be 0-9)")

        if invalid_retention:
            self.fail("Invalid retention-days values found: " + "; ".join(invalid_retention))
        if compression_type_issues:
            self.fail("Invalid compression-level values found: " + "; ".join(compression_type_issues))
        if missing_retention:
            self.fail(
                "Missing required 'retention-days' on upload-artifact steps: " + "; ".join(missing_retention)
            )


if __name__ == "__main__":
    unittest.main()