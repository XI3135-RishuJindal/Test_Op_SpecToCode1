"""
Upgrade validation tests for Bandit and pip-audit GitHub Actions CI integration.

These tests verify that:
1. The security scanning tools (bandit, pip-audit) are installed at expected versions.
2. The GitHub Actions workflow file exists and contains the required security job.
3. Bandit configuration is present and correctly structured.
4. pip-audit can be invoked and produces expected output format.
5. Dev dependency manifest includes pinned bandit and pip-audit entries.
6. Artifact upload steps are present in the workflow for scan reports.
"""

import json
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

# Minimum acceptable versions (inclusive)
BANDIT_MIN_VERSION = (1, 7, 9)
PIP_AUDIT_MIN_VERSION = (2, 7, 3)


def _parse_version(version_str: str):
    """Return a tuple of ints from a version string like '1.7.9'."""
    clean = re.sub(r"[^\d.]", "", version_str.split()[0])
    return tuple(int(x) for x in clean.split(".") if x.isdigit())


def _find_workflow_file():
    """Return the first .yml/.yaml file in .github/workflows/ that contains a
    'security' job, or None if not found."""
    if not WORKFLOWS_DIR.exists():
        return None
    for wf_file in sorted(WORKFLOWS_DIR.glob("*.yml")) + sorted(
        WORKFLOWS_DIR.glob("*.yaml")
    ):
        content = wf_file.read_text(encoding="utf-8")
        if "security" in content.lower():
            return wf_file
    return None


def _load_workflow(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def _find_dev_requirements_file():
    """Return the first dev-requirements file found in the repo root."""
    candidates = [
        "requirements-dev.txt",
        "requirements_dev.txt",
        "requirements-ci.txt",
        "requirements-test.txt",
    ]
    for name in candidates:
        p = REPO_ROOT / name
        if p.exists():
            return p
    # Also check pyproject.toml presence (content checked separately)
    pyproject = REPO_ROOT / "pyproject.toml"
    if pyproject.exists():
        return pyproject
    return None


# ---------------------------------------------------------------------------
# Test classes
# ---------------------------------------------------------------------------


class TestToolsInstalled(unittest.TestCase):
    """Verify bandit and pip-audit are installed at the required versions."""

    def _get_tool_version(self, tool: str) -> tuple:
        result = subprocess.run(
            [sys.executable, "-m", tool, "--version"],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            # Some tools print version to stderr
            version_output = result.stderr.strip() or result.stdout.strip()
        else:
            version_output = result.stdout.strip() or result.stderr.strip()
        return _parse_version(version_output)

    def test_bandit_is_installed(self):
        """bandit must be importable / executable."""
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "--version"],
            capture_output=True,
            text=True,
        )
        self.assertIn(
            result.returncode,
            (0, 1),  # bandit --version may exit 1 on some versions
            msg=f"bandit is not installed or not executable. stderr: {result.stderr}",
        )
        combined = result.stdout + result.stderr
        self.assertRegex(
            combined,
            r"\d+\.\d+",
            msg="bandit --version did not return a recognisable version string.",
        )

    def test_bandit_meets_minimum_version(self):
        """bandit version must be >= 1.7.9."""
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "--version"],
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        version = _parse_version(combined)
        self.assertGreaterEqual(
            version,
            BANDIT_MIN_VERSION,
            msg=(
                f"bandit {version} is below the required minimum "
                f"{BANDIT_MIN_VERSION}. Upgrade bandit to >= 1.7.9."
            ),
        )

    def test_pip_audit_is_installed(self):
        """pip-audit must be importable / executable."""
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "--version"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"pip-audit is not installed or not executable. stderr: {result.stderr}",
        )
        combined = result.stdout + result.stderr
        self.assertRegex(
            combined,
            r"\d+\.\d+",
            msg="pip-audit --version did not return a recognisable version string.",
        )

    def test_pip_audit_meets_minimum_version(self):
        """pip-audit version must be >= 2.7.3."""
        result = subprocess.run(
            [sys.executable, "-m", "pip_audit", "--version"],
            capture_output=True,
            text=True,
        )
        combined = result.stdout + result.stderr
        version = _parse_version(combined)
        self.assertGreaterEqual(
            version,
            PIP_AUDIT_MIN_VERSION,
            msg=(
                f"pip-audit {version} is below the required minimum "
                f"{PIP_AUDIT_MIN_VERSION}. Upgrade pip-audit to >= 2.7.3."
            ),
        )


class TestWorkflowFileExists(unittest.TestCase):
    """Verify the GitHub Actions workflow directory and security workflow exist."""

    def test_workflows_directory_exists(self):
        self.assertTrue(
            WORKFLOWS_DIR.exists(),
            msg=f"Expected .github/workflows/ directory at {WORKFLOWS_DIR}",
        )

    def test_security_workflow_file_exists(self):
        wf = _find_workflow_file()
        self.assertIsNotNone(
            wf,
            msg=(
                "No workflow file containing a 'security' job was found in "
                f"{WORKFLOWS_DIR}. Expected a .yml/.yaml file with a 'security' job."
            ),
        )


class TestWorkflowStructure(unittest.TestCase):
    """Verify the security job in the workflow has the required steps."""

    @classmethod
    def setUpClass(cls):
        cls.wf_path = _find_workflow_file()
        if cls.wf_path is None:
            cls.wf = None
        else:
            cls.wf = _load_workflow(cls.wf_path)

    def _get_security_job(self):
        if self.wf is None:
            self.skipTest("No workflow file with a security job found.")
        jobs = self.wf.get("jobs", {})
        # Accept job keys like 'security', 'security-scan', 'security_scan'
        for key, job in jobs.items():
            if "security" in key.lower():
                return job
        self.fail(
            f"No job with 'security' in its key found in {self.wf_path}. "
            f"Available jobs: {list(jobs.keys())}"
        )

    def test_workflow_triggers_on_push(self):
        """Workflow must trigger on push events."""
        if self.wf is None:
            self.skipTest("No workflow file found.")
        triggers = self.wf.get("on", self.wf.get(True, {}))
        if isinstance(triggers, dict):
            self.assertIn(
                "push",
                triggers,
                msg="Workflow must include 'push' as a trigger.",
            )
        elif isinstance(triggers, list):
            self.assertIn(
                "push",
                triggers,
                msg="Workflow must include 'push' as a trigger.",
            )

    def test_workflow_triggers_on_pull_request(self):
        """Workflow must trigger on pull_request events."""
        if self.wf is None:
            self.skipTest("No workflow file found.")
        triggers = self.wf.get("on", self.wf.get(True, {}))
        if isinstance(triggers, dict):
            self.assertIn(
                "pull_request",
                triggers,
                msg="Workflow must include 'pull_request' as a trigger.",
            )
        elif isinstance(triggers, list):
            self.assertIn(
                "pull_request",
                triggers,
                msg="Workflow must include 'pull_request' as a trigger.",
            )

    def test_security_job_has_checkout_step(self):
        """Security job must include a checkout step."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        uses_values = [s.get("uses", "") for s in steps]
        checkout_present = any("actions/checkout" in u for u in uses_values)
        self.assertTrue(
            checkout_present,
            msg="Security job must include an 'actions/checkout' step.",
        )

    def test_security_job_has_python_setup_step(self):
        """Security job must include a Python setup step."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        uses_values = [s.get("uses", "") for s in steps]
        python_setup_present = any(
            "actions/setup-python" in u for u in uses_values
        )
        self.assertTrue(
            python_setup_present,
            msg="Security job must include an 'actions/setup-python' step.",
        )

    def test_security_job_has_bandit_step(self):
        """Security job must include a step that runs bandit."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        run_commands = [s.get("run", "") for s in steps]
        bandit_present = any("bandit" in cmd for cmd in run_commands)
        self.assertTrue(
            bandit_present,
            msg="Security job must include a step that runs 'bandit'.",
        )

    def test_security_job_bandit_uses_recursive_flag(self):
        """bandit step must use the -r (recursive) flag."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        for step in steps:
            run = step.get("run", "")
            if "bandit" in run:
                self.assertRegex(
                    run,
                    r"bandit\s.*-r",
                    msg="bandit invocation must include the -r (recursive) flag.",
                )
                return
        self.fail("No bandit run step found in security job.")

    def test_security_job_bandit_uses_config_file(self):
        """bandit step must reference a config file via -c flag."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        for step in steps:
            run = step.get("run", "")
            if "bandit" in run:
                self.assertRegex(
                    run,
                    r"-c\s+\S+",
                    msg=(
                        "bandit invocation must specify a config file with -c "
                        "(e.g., -c .bandit or -c pyproject.toml)."
                    ),
                )
                return
        self.fail("No bandit run step found in security job.")

    def test_security_job_bandit_outputs_json_report(self):
        """bandit step must produce a JSON report file."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        for step in steps:
            run = step.get("run", "")
            if "bandit" in run:
                self.assertRegex(
                    run,
                    r"--format\s+json|--format=json|-f\s+json",
                    msg="bandit invocation must output JSON format (--format json).",
                )
                self.assertRegex(
                    run,
                    r"-o\s+\S+\.json|--output\s+\S+\.json",
                    msg="bandit invocation must write output to a .json file (-o <file>).",
                )
                return
        self.fail("No bandit run step found in security job.")

    def test_security_job_has_pip_audit_step(self):
        """Security job must include a step that runs pip-audit."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        run_commands = [s.get("run", "") for s in steps]
        pip_audit_present = any("pip-audit" in cmd or "pip_audit" in cmd for cmd in run_commands)
        self.assertTrue(
            pip_audit_present,
            msg="Security job must include a step that runs 'pip-audit'.",
        )

    def test_security_job_pip_audit_outputs_json_report(self):
        """pip-audit step must produce a JSON report file."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        for step in steps:
            run = step.get("run", "")
            if "pip-audit" in run or "pip_audit" in run:
                self.assertRegex(
                    run,
                    r"--format\s+json|--format=json",
                    msg="pip-audit invocation must output JSON format (--format json).",
                )
                self.assertRegex(
                    run,
                    r"--output\s+\S+\.json|--output=\S+\.json",
                    msg="pip-audit invocation must write output to a .json file (--output <file>).",
                )
                return
        self.fail("No pip-audit run step found in security job.")

    def test_security_job_pip_audit_specifies_requirements(self):
        """pip-audit step must reference a requirements/dependency manifest."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        for step in steps:
            run = step.get("run", "")
            if "pip-audit" in run or "pip_audit" in run:
                has_req = (
                    "--requirement" in run
                    or "-r " in run
                    or "pyproject.toml" in run
                    or "setup.cfg" in run
                )
                self.assertTrue(
                    has_req,
                    msg=(
                        "pip-audit invocation must specify a dependency manifest "
                        "(e.g., --requirement requirements.txt)."
                    ),
                )
                return
        self.fail("No pip-audit run step found in security job.")

    def test_security_job_uploads_bandit_artifact(self):
        """Security job must upload the bandit report as a workflow artifact."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        uses_values = [s.get("uses", "") for s in steps]
        upload_present = any("actions/upload-artifact" in u for u in uses_values)
        self.assertTrue(
            upload_present,
            msg="Security job must include at least one 'actions/upload-artifact' step.",
        )
        # Check that bandit report is referenced in an upload step
        bandit_report_uploaded = False
        for step in steps:
            if "actions/upload-artifact" in step.get("uses", ""):
                with_block = step.get("with", {})
                path_val = str(with_block.get("path", ""))
                if "bandit" in path_val:
                    bandit_report_uploaded = True
                    break
        self.assertTrue(
            bandit_report_uploaded,
            msg=(
                "Security job must upload the bandit report artifact "
                "(upload-artifact step with a path containing 'bandit')."
            ),
        )

    def test_security_job_uploads_pip_audit_artifact(self):
        """Security job must upload the pip-audit report as a workflow artifact."""
        job = self._get_security_job()
        steps = job.get("steps", [])
        pip_audit_report_uploaded = False
        for step in steps:
            if "actions/upload-artifact" in step.get("uses", ""):
                with_block = step.get("with", {})
                path_val = str(with_block.get("path", ""))
                if "pip-audit" in path_val or "pip_audit" in path_val:
                    pip_audit_report_uploaded = True
                    break
        self.assertTrue(
            pip_audit_report_uploaded,
            msg=(
                "Security job must upload the pip-audit report artifact "
                "(upload-artifact step with a path containing 'pip-audit' or 'pip_audit')."
            ),
        )

    def test_security_job_runs_on_ubuntu(self):
        """Security job must run on an ubuntu runner."""
        job = self._get_security_job()
        runs_on = job.get("runs-on", "")
        self.assertIn(
            "ubuntu",
            str(runs_on).lower(),
            msg=f"Security job 'runs-on' must be an ubuntu runner, got: {runs_on}",
        )


class TestBanditConfiguration(unittest.TestCase):
    """Verify bandit configuration file exists and is correctly structured."""

    def _find_bandit_config(self):
        """Return path to .bandit file or None."""
        bandit_file = REPO_ROOT / ".bandit"
        if bandit_file.exists():
            return bandit_file
        return None

    def _find_bandit_in_pyproject(self):
        """Return True if pyproject.toml contains [tool.bandit] section."""
        pyproject = REPO_ROOT / "pyproject.toml"
        if not pyproject.exists():
            return False
        content = pyproject.read_text(encoding="utf-8")
        return "[tool.bandit]" in content

    def test_bandit_config_exists(self):
        """A bandit configuration must exist as .bandit or [tool.bandit] in pyproject.toml."""
        has_bandit_file = self._find_bandit_config() is not None
        has_pyproject_section = self._find_bandit_in_pyproject()
        self.assertTrue(
            has_bandit_file or has_pyproject_section,
            msg=(
                "No bandit configuration found. Expected either a '.bandit' file "
                "in the repo root or a '[tool.bandit]' section in pyproject.toml."
            ),
        )

    def test_bandit_config_specifies_targets(self):
        """Bandit config must specify target directories."""
        bandit_file = self._find_bandit_config()
        if bandit_file:
            content = bandit_file.read_text(encoding="utf-8")
            self.assertRegex(
                content,
                r"targets",
                msg=".bandit config must specify 'targets' (directories to scan).",
            )
        else:
            pyproject = REPO_ROOT / "pyproject.toml"
            if pyproject.exists():
                content = pyproject.read_text(encoding="utf-8")
                self.assertRegex(
                    content,
                    r"\[tool\.bandit\].*?targets",
                    msg="[tool.bandit] in pyproject.toml must specify 'targets'.",
                )
            else:
                self.skipTest("No bandit config file found to inspect.")


class TestDevDependenciesIncludeSecurityTools(unittest.TestCase):
    """Verify dev/CI dependencies pin bandit and pip-audit."""

    def _get_dev_requirements_content(self):
        dev_req = _find_dev_requirements_file()
        if dev_req is None:
            return None, None
        return dev_req, dev_req.read_text(encoding="utf-8")

    def test_dev_requirements_file_exists(self):
        """A dev/CI requirements file or pyproject.toml must exist."""
        dev_req = _find_dev_requirements_file()
        self.assertIsNotNone(
            dev_req,
            msg=(
                "No dev requirements file found. Expected one of: "
                "requirements-dev.txt, requirements_dev.txt, requirements-ci.txt, "
                "requirements-test.txt, or pyproject.toml."
            ),
        )

    def test_bandit_pinned_in_dev_requirements(self):
        """bandit must be listed in dev/CI dependencies."""
        dev_req, content = self._get_dev_requirements_content()
        if content is None:
            self.skipTest("No dev requirements file found.")
        self.assertRegex(
            content,
            r"bandit[>=<!\s]",
            msg=(
                f"bandit is not listed in {dev_req}. "
                "Add 'bandit>=1.7.9' to dev/CI dependencies."
            ),
        )

    def test_pip_audit_pinned_in_dev_requirements(self):
        """pip-audit must be listed in dev/CI dependencies."""
        dev_req, content = self._get_dev_requirements_content()
        if content is None:
            self.skipTest("No dev requirements file found.")
        self.assertRegex(
            content,
            r"pip.audit[>=<!\s]",
            msg=(
                f"pip-audit is not listed in {dev_req}. "
                "Add 'pip-audit>=2.7.3' to dev/CI dependencies."
            ),
        )

    def test_bandit_version_constraint_meets_minimum(self):
        """bandit version constraint in dev requirements must be >= 1.7.9."""
        dev_req, content = self._get_dev_requirements_content()
        if content is None:
            self.skipTest("No dev requirements file found.")
        match = re.search(r"bandit[>=<!\s]+(\d+\.\d+[\.\d]*)", content)
        if match is None:
            self.skipTest("bandit version constraint not parseable; skipping version check.")
        version = _parse_version(match.group(1))
        self.assertGreaterEqual(
            version,
            BANDIT_MIN_VERSION,
            msg=(
                f"bandit version constraint {match.group(1)} in {dev_req} "
                f"is below the required minimum {BANDIT_MIN_VERSION}."
            ),
        )

    def test_pip_audit_version_constraint_meets_minimum(self):
        """pip-audit version constraint in dev requirements must be >= 2.7.3."""
        dev_req, content = self._get_dev_requirements_content()
        if content is None:
            self.skipTest("No dev requirements file found.")
        match = re.search(r"pip.audit[>=<!\s]+(\d+\.\d+[\.\d]*)", content)
        if match is None:
            self.skipTest("pip-audit version constraint not parseable; skipping version check.")
        version = _parse_version(match.group(1))
        self.assertGreaterEqual(
            version,
            PIP_AUDIT_MIN_VERSION,
            msg=(
                f"pip-audit version constraint {match.group(1)} in {dev_req} "
                f"is below the required minimum {PIP_AUDIT_MIN_VERSION}."
            ),
        )


class TestBanditCanScanCode(unittest.TestCase):
    """Verify bandit can execute a scan and produce valid JSON output."""

    def test_bandit_produces_valid_json_output(self):
        """bandit --format json must produce parseable JSON on a trivial target."""
        import tempfile

        # Write a minimal safe Python file to scan
        safe_code = "x = 1 + 1\nprint(x)\n"
        with tempfile.NamedTemporaryFile(
            suffix=".py", mode="w", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(safe_code)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "bandit",
                    "-r",
                    tmp_path,
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
            )
            # bandit exits 0 (no issues) or 1 (issues found); both are valid runs
            self.assertIn(
                result.returncode,
                (0, 1),
                msg=f"bandit exited with unexpected code {result.returncode}. stderr: {result.stderr}",
            )
            output = result.stdout.strip()
            self.assertTrue(
                len(output) > 0,
                msg="bandit produced no stdout output when --format json was specified.",
            )
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError as exc:
                self.fail(f"bandit JSON output is not valid JSON: {exc}\nOutput: {output[:500]}")
            self.assertIn(
                "results",
                parsed,
                msg="bandit JSON output must contain a 'results' key.",
            )
            self.assertIn(
                "metrics",
                parsed,
                msg="bandit JSON output must contain a 'metrics' key.",
            )
        finally:
            os.unlink(tmp_path)


class TestPipAuditCanRun(unittest.TestCase):
    """Verify pip-audit can execute and produce valid JSON output."""

    def test_pip_audit_produces_valid_json_output(self):
        """pip-audit --format json must produce parseable JSON."""
        import tempfile

        # Write a minimal requirements file with a known-safe package
        req_content = "pip>=23.0\n"
        with tempfile.NamedTemporaryFile(
            suffix=".txt", mode="w", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(req_content)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip_audit",
                    "--requirement",
                    tmp_path,
                    "--format",
                    "json",
                    "--no-deps",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
            # pip-audit exits 0 (no vulns) or 1 (vulns found); both are valid runs
            self.assertIn(
                result.returncode,
                (0, 1),
                msg=(
                    f"pip-audit exited with unexpected code {result.returncode}. "
                    f"stderr: {result.stderr[:500]}"
                ),
            )
            output = result.stdout.strip()
            self.assertTrue(
                len(output) > 0,
                msg="pip-audit produced no stdout output when --format json was specified.",
            )
            try:
                parsed = json.loads(output)
            except json.JSONDecodeError as exc:
                self.fail(
                    f"pip-audit JSON output is not valid JSON: {exc}\nOutput: {output[:500]}"
                )
            # pip-audit JSON output is a list of dependency audit results
            self.assertIsInstance(
                parsed,
                (list, dict),
                msg="pip-audit JSON output must be a JSON array or object.",
            )
        finally:
            os.unlink(tmp_path)


class TestNoLegacySafetyToolPresent(unittest.TestCase):
    """Verify that the old 'safety' tool is not being used as the sole dep scanner
    (pip-audit is the designated replacement in this upgrade)."""

    def test_workflow_does_not_rely_solely_on_safety(self):
        """Workflow security job must use pip-audit, not only the legacy 'safety' tool."""
        wf_path = _find_workflow_file()
        if wf_path is None:
            self.skipTest("No security workflow file found.")
        content = wf_path.read_text(encoding="utf-8")
        has_pip_audit = "pip-audit" in content or "pip_audit" in content
        self.assertTrue(
            has_pip_audit,
            msg=(
                f"Workflow {wf_path.name} does not invoke pip-audit. "
                "The upgrade requires pip-audit to replace or supplement legacy safety checks."
            ),
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)