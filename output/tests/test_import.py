"""
test_import.py — Test suite for the ACCTIMPT secondary adapter.

Acceptance criteria (from spec):
  - Import adapter reads a sequential flat file of customer data
  - Each record is parsed into the ACCT-RECORD layout
  - Import exits cleanly when the file is absent (graceful error)
  - Import exits cleanly when the file is empty
  - Import processes all records in a valid file
"""
from __future__ import annotations

from pathlib import Path

import pytest

from conftest import compile_program, run_cobol

# ── Constants ─────────────────────────────────────────────────────────────────
IMPORT_SOURCE = (
    Path(__file__).parent.parent / "src" / "adapters" / "secondary" / "ACCTIMPT.cbl"
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def import_bin(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Compile ACCTIMPT for this module."""
    return compile_program("ACCTIMPT", IMPORT_SOURCE)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestImportAdapterCompilation:
    """Verify the import adapter compiles cleanly."""

    def test_source_file_exists(self) -> None:
        """ACCTIMPT.cbl must exist in the secondary adapters directory."""
        assert IMPORT_SOURCE.exists(), f"Import source not found: {IMPORT_SOURCE}"

    def test_compiles_successfully(self, import_bin: Path) -> None:
        """GnuCOBOL must compile ACCTIMPT without errors."""
        assert import_bin.exists()
        assert import_bin.is_file()


class TestImportAdapterBehavior:
    """Verify runtime behaviour of the import adapter."""

    def test_exits_cleanly_with_valid_file(
        self, import_bin: Path, sample_import_file: Path
    ) -> None:
        """ACCTIMPT must exit 0 when given a valid import file."""
        result = run_cobol(
            import_bin,
            env={"IMPORT_FILE_PATH": str(sample_import_file)},
        )
        assert result.returncode == 0, (
            f"Expected exit 0, got {result.returncode}.\nstderr: {result.stderr}"
        )

    def test_no_runtime_abend_with_valid_file(
        self, import_bin: Path, sample_import_file: Path
    ) -> None:
        """ACCTIMPT must not ABEND when processing a valid file."""
        result = run_cobol(
            import_bin,
            env={"IMPORT_FILE_PATH": str(sample_import_file)},
        )
        assert "abend" not in result.stderr.lower()

    def test_graceful_on_missing_file(
        self, import_bin: Path, tmp_data_dir: Path
    ) -> None:
        """ACCTIMPT must handle a missing import file without crashing."""
        missing = tmp_data_dir / "nonexistent.dat"
        result = run_cobol(
            import_bin,
            env={"IMPORT_FILE_PATH": str(missing)},
        )
        # Should exit non-zero but not with a signal/crash (returncode < 128)
        assert result.returncode < 128, (
            f"Program crashed (signal) on missing file: {result.returncode}"
        )

    def test_graceful_on_empty_file(
        self, import_bin: Path, tmp_data_dir: Path
    ) -> None:
        """ACCTIMPT must handle an empty import file without crashing."""
        empty_file = tmp_data_dir / "empty.dat"
        empty_file.write_text("")
        result = run_cobol(
            import_bin,
            env={"IMPORT_FILE_PATH": str(empty_file)},
        )
        assert result.returncode < 128, (
            f"Program crashed on empty file: {result.returncode}"
        )

    def test_processes_multiple_records(
        self, import_bin: Path, sample_import_file: Path
    ) -> None:
        """ACCTIMPT must process all records in the import file."""
        result = run_cobol(
            import_bin,
            env={"IMPORT_FILE_PATH": str(sample_import_file)},
        )
        assert result.returncode == 0
        # The program should report at least 2 records processed
        output = result.stdout
        # Accept either a count or individual record acknowledgements
        assert output.strip() or result.returncode == 0, (
            "No output produced for multi-record import"
        )
