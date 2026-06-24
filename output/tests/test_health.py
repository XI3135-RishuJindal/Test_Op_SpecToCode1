"""
test_health.py — Test suite for the ACCTHLTH health check program.

Acceptance criteria (from spec):
  - Health endpoint returns result code '00'
  - Status field is 'UP'
  - Service name is populated
  - Version is populated
  - Timestamp is populated
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from conftest import compile_program, run_cobol

# ── Constants ─────────────────────────────────────────────────────────────────
HEALTH_SOURCE = (
    Path(__file__).parent.parent / "src" / "adapters" / "primary" / "ACCTHLTH.cbl"
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def health_bin(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Compile ACCTHLTH for this module."""
    return compile_program("ACCTHLTH", HEALTH_SOURCE)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestHealthCheckCompilation:
    """Verify the health check program compiles without errors."""

    def test_source_file_exists(self) -> None:
        """ACCTHLTH.cbl must exist in the primary adapters directory."""
        assert HEALTH_SOURCE.exists(), (
            f"Health check source not found: {HEALTH_SOURCE}"
        )

    def test_compiles_successfully(self, health_bin: Path) -> None:
        """GnuCOBOL must compile ACCTHLTH without errors."""
        assert health_bin.exists(), "Compiled binary not produced"
        assert health_bin.is_file(), "Binary path is not a file"


class TestHealthCheckBehavior:
    """Verify runtime behaviour of the health check program."""

    def test_exits_with_zero(self, health_bin: Path) -> None:
        """ACCTHLTH must exit with return code 0 (success)."""
        result = run_cobol(health_bin)
        assert result.returncode == 0, (
            f"Expected exit 0, got {result.returncode}.\nstderr: {result.stderr}"
        )

    def test_no_runtime_errors(self, health_bin: Path) -> None:
        """ACCTHLTH must not produce runtime error output."""
        result = run_cobol(health_bin)
        stderr_lower = result.stderr.lower()
        assert "abend" not in stderr_lower, "Runtime ABEND detected"
        assert "error" not in stderr_lower, f"Runtime error: {result.stderr}"

    def test_produces_output(self, health_bin: Path) -> None:
        """ACCTHLTH must write at least one line to stdout."""
        result = run_cobol(health_bin)
        assert result.stdout.strip(), "Health check produced no output"

    def test_status_is_up(self, health_bin: Path) -> None:
        """Health response must contain 'UP' status."""
        result = run_cobol(health_bin)
        assert "UP" in result.stdout, (
            f"Expected 'UP' in output, got:\n{result.stdout}"
        )

    def test_result_code_is_00(self, health_bin: Path) -> None:
        """Health response must contain result code '00'."""
        result = run_cobol(health_bin)
        assert "00" in result.stdout, (
            f"Expected result code '00' in output, got:\n{result.stdout}"
        )

    def test_service_name_present(self, health_bin: Path) -> None:
        """Health response must include the service name."""
        result = run_cobol(health_bin)
        assert "ACCOUNT" in result.stdout.upper(), (
            f"Service name not found in output:\n{result.stdout}"
        )

    def test_version_present(self, health_bin: Path) -> None:
        """Health response must include a version string."""
        result = run_cobol(health_bin)
        # Version follows semver pattern x.y.z
        import re
        assert re.search(r"\d+\.\d+\.\d+", result.stdout), (
            f"Version string not found in output:\n{result.stdout}"
        )


class TestHealthCheckIdempotency:
    """Health check must be safe to call multiple times."""

    def test_multiple_invocations_consistent(self, health_bin: Path) -> None:
        """Repeated calls must all return 'UP' and code '00'."""
        for i in range(3):
            result = run_cobol(health_bin)
            assert result.returncode == 0, f"Invocation {i+1} failed"
            assert "UP" in result.stdout, f"Invocation {i+1}: status not UP"
            assert "00" in result.stdout, f"Invocation {i+1}: result code not 00"
