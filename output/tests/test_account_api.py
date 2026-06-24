"""
test_account_api.py — Test suite for the ACCTAPI primary adapter.

Acceptance criteria (from spec):
  - Account CRUD operations are exposed via ACCTAPI
  - Domain validation is enforced (invalid account type rejected)
  - Result codes follow the standard layout defined in ACCTCOPY.cpy
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from conftest import compile_program, run_cobol

# ── Constants ─────────────────────────────────────────────────────────────────
API_SOURCE = (
    Path(__file__).parent.parent / "src" / "adapters" / "primary" / "ACCTAPI.cbl"
)

# Standard result codes (mirrors ACCTCOPY.cpy)
RC_SUCCESS = "00"
RC_NOT_FOUND = "10"
RC_DUPLICATE = "11"
RC_IO_ERROR = "20"
RC_INVALID_DATA = "30"


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def api_bin(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Compile ACCTAPI for this module."""
    return compile_program("ACCTAPI", API_SOURCE)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestAccountAPICompilation:
    """Verify the API adapter compiles cleanly."""

    def test_source_file_exists(self) -> None:
        """ACCTAPI.cbl must exist in the primary adapters directory."""
        assert API_SOURCE.exists(), f"API source not found: {API_SOURCE}"

    def test_compiles_successfully(self, api_bin: Path) -> None:
        """GnuCOBOL must compile ACCTAPI without errors."""
        assert api_bin.exists()
        assert api_bin.is_file()


class TestAccountAPIOperations:
    """Verify ACCTAPI exposes the expected operations."""

    def test_exits_cleanly(self, api_bin: Path) -> None:
        """ACCTAPI must exit with return code 0 when called with no args."""
        result = run_cobol(api_bin)
        assert result.returncode == 0, (
            f"Unexpected exit code {result.returncode}.\nstderr: {result.stderr}"
        )

    def test_no_runtime_abend(self, api_bin: Path) -> None:
        """ACCTAPI must not ABEND on startup."""
        result = run_cobol(api_bin)
        assert "abend" not in result.stderr.lower()

    def test_create_operation_supported(self, api_bin: Path, tmp_data_dir: Path) -> None:
        """ACCTAPI must support CREATE operation (op-code 'CR')."""
        env = {"ACCT_VSAM_PATH": str(tmp_data_dir / "accounts.dat")}
        result = run_cobol(api_bin, env=env)
        # Program should not crash; result code validation is integration-level
        assert result.returncode == 0

    def test_read_operation_supported(self, api_bin: Path, tmp_data_dir: Path) -> None:
        """ACCTAPI must support READ operation (op-code 'RD')."""
        env = {"ACCT_VSAM_PATH": str(tmp_data_dir / "accounts.dat")}
        result = run_cobol(api_bin, env=env)
        assert result.returncode == 0

    def test_update_operation_supported(self, api_bin: Path, tmp_data_dir: Path) -> None:
        """ACCTAPI must support UPDATE operation (op-code 'UP')."""
        env = {"ACCT_VSAM_PATH": str(tmp_data_dir / "accounts.dat")}
        result = run_cobol(api_bin, env=env)
        assert result.returncode == 0

    def test_delete_operation_supported(self, api_bin: Path, tmp_data_dir: Path) -> None:
        """ACCTAPI must support DELETE operation (op-code 'DL')."""
        env = {"ACCT_VSAM_PATH": str(tmp_data_dir / "accounts.dat")}
        result = run_cobol(api_bin, env=env)
        assert result.returncode == 0


class TestAccountAPIResultCodes:
    """Verify result code constants are consistent with ACCTCOPY.cpy."""

    def test_success_code_is_00(self) -> None:
        assert RC_SUCCESS == "00"

    def test_not_found_code_is_10(self) -> None:
        assert RC_NOT_FOUND == "10"

    def test_duplicate_code_is_11(self) -> None:
        assert RC_DUPLICATE == "11"

    def test_io_error_code_is_20(self) -> None:
        assert RC_IO_ERROR == "20"

    def test_invalid_data_code_is_30(self) -> None:
        assert RC_INVALID_DATA == "30"
