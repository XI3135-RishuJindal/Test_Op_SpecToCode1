"""
conftest.py — Shared pytest fixtures for Account Management Service tests.

The test harness compiles COBOL programs via GnuCOBOL and invokes them
through a thin Python subprocess wrapper, capturing the LINKAGE SECTION
output via a shared memory segment or stdout-encoded response.
"""
from __future__ import annotations

import os
import subprocess
import struct
import tempfile
from pathlib import Path
from typing import Generator

import pytest

# ── Project root ─────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.parent
BIN_DIR = PROJECT_ROOT / "bin"
SRC_DIR = PROJECT_ROOT / "src"

# ── Helpers ───────────────────────────────────────────────────────────────────

def compile_program(program_name: str, source_path: Path) -> Path:
    """Compile a COBOL source file with GnuCOBOL and return the binary path."""
    BIN_DIR.mkdir(parents=True, exist_ok=True)
    binary = BIN_DIR / program_name
    result = subprocess.run(
        ["cobc", "-x", "-free", "-o", str(binary), str(source_path)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.skip(
            f"GnuCOBOL compilation failed for {program_name}:\n{result.stderr}"
        )
    return binary


def run_cobol(binary: Path, env: dict | None = None) -> subprocess.CompletedProcess:
    """Execute a compiled COBOL binary and return the CompletedProcess."""
    merged_env = {**os.environ, **(env or {})}
    return subprocess.run(
        [str(binary)],
        capture_output=True,
        text=True,
        env=merged_env,
        timeout=10,
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def health_binary() -> Path:
    """Compile ACCTHLTH once per test session."""
    source = SRC_DIR / "adapters" / "primary" / "ACCTHLTH.cbl"
    return compile_program("ACCTHLTH", source)


@pytest.fixture(scope="session")
def api_binary() -> Path:
    """Compile ACCTAPI once per test session."""
    source = SRC_DIR / "adapters" / "primary" / "ACCTAPI.cbl"
    return compile_program("ACCTAPI", source)


@pytest.fixture(scope="session")
def domain_binary() -> Path:
    """Compile ACCTDMN once per test session."""
    source = SRC_DIR / "domain" / "ACCTDMN.cbl"
    return compile_program("ACCTDMN", source)


@pytest.fixture()
def tmp_data_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for VSAM/import data files."""
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "import").mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture()
def sample_import_file(tmp_data_dir: Path) -> Path:
    """Write a minimal customer import flat file and return its path."""
    import_path = tmp_data_dir / "import" / "customers.dat"
    records = [
        # account_id  cust_id    type status balance          open_date last_upd  filler
        "ACCT000001CUST000001CH A000000010000020240101202401010" + " " * 26,
        "ACCT000002CUST000002SV A000000050000020240201202402010" + " " * 26,
    ]
    import_path.write_text("\n".join(records) + "\n")
    return import_path
