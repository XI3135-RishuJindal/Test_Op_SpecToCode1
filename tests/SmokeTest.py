import os
import re
import subprocess
import sys
import unittest
from pathlib import Path


class TestCVERemediationUpgradeValidation(unittest.TestCase):
    """
    Upgrade validation tests for conservative patch/minor dependency bumps.

    These tests intentionally verify:
    - the active runtime is at the exact target version (provided via env)
    - critical application paths (basic execution/import) work under the new version
    - deprecated/removed APIs (provided via env patterns) do not appear in the repo
    - new configuration keys (provided via env) can be loaded without errors
    """

    @classmethod
    def setUpClass(cls):
        cls.repo_root = Path(__file__).resolve().parents[1]

    def _run(self, args, cwd=None, env=None, timeout=60):
        proc = subprocess.run(
            args,
            cwd=str(cwd or self.repo_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
        )
        return proc

    def test_active_runtime_version_matches_target_exactly(self):
        """
        REQUIRED:
        - Checks active runtime version against the exact target version.

        The target must be explicitly provided by CI via UPGRADE_TARGET_RUNTIME_VERSION,
        because the upgrade context did not specify language/runtime in this prompt.
        """
        target = os.environ.get("UPGRADE_TARGET_RUNTIME_VERSION", "").strip()
        self.assertTrue(
            target,
            "UPGRADE_TARGET_RUNTIME_VERSION must be set to the EXACT target runtime version (e.g., '3.12.4').",
        )

        # This test file is written in Python, so we assert the active Python runtime version.
        active = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        self.assertEqual(
            active,
            target,
            f"Active runtime version '{active}' does not match target '{target}'.",
        )

    def test_critical_application_paths_execute(self):
        """
        REQUIRED:
        - Validates critical application paths work correctly with the new version.

        Because no app/framework entrypoints were provided, we validate:
        - repository can run a minimal Python command
        - if a common app entrypoint exists (app.py/main.py), it at least imports/executes --help safely
        """
        proc = self._run([sys.executable, "-c", "import sys; print(sys.version)"])
        self.assertEqual(proc.returncode, 0, f"Python command failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")

        # Try common entrypoints without assuming specific frameworks.
        candidates = [
            self.repo_root / "app.py",
            self.repo_root / "main.py",
            self.repo_root / "src" / "app.py",
            self.repo_root / "src" / "main.py",
        ]
        entrypoints = [p for p in candidates if p.exists() and p.is_file()]

        # If we find an entrypoint, ensure it can at least be invoked with --help
        # (a typical "critical path" that should not crash due to dependency bumps).
        for ep in entrypoints:
            proc = self._run([sys.executable, str(ep), "--help"], timeout=60)
            self.assertEqual(
                proc.returncode,
                0,
                f"Entrypoint {ep} failed under upgraded dependencies.\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}",
            )

    def test_deprecated_apis_replaced_do_not_appear_in_repo(self):
        """
        REQUIRED:
        - Verifies deprecated APIs replaced in this upgrade no longer appear.

        Because the upgrade context did not specify which APIs were deprecated,
        CI must provide one or more regex patterns via:
          UPGRADE_DEPRECATED_API_REGEX (newline-separated or '||' separated)

        Example:
          export UPGRADE_DEPRECATED_API_REGEX="\\bimp\\b||from\\s+collections\\s+import\\s+MutableMapping"
        """
        patterns_raw = os.environ.get("UPGRADE_DEPRECATED_API_REGEX", "").strip()
        self.assertTrue(
            patterns_raw,
            "UPGRADE_DEPRECATED_API_REGEX must be set to regex pattern(s) for deprecated APIs replaced in this upgrade.",
        )

        # Support newline-separated and/or '||' separated patterns.
        parts = []
        for line in patterns_raw.splitlines():
            line = line.strip()
            if not line:
                continue
            parts.extend([p.strip() for p in line.split("||") if p.strip()])

        self.assertTrue(parts, "No usable patterns found in UPGRADE_DEPRECATED_API_REGEX.")

        # Only scan source-like files; avoid scanning bulky or irrelevant artifacts.
        include_ext = {
            ".py",
            ".pyi",
            ".txt",
            ".md",
            ".rst",
            ".toml",
            ".ini",
            ".cfg",
            ".yml",
            ".yaml",
            ".json",
            ".env",
            ".sh",
            ".bat",
            ".ps1",
        }
        exclude_dirs = {
            ".git",
            ".hg",
            ".svn",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            ".tox",
            "venv",
            ".venv",
            "env",
            ".env",
            "node_modules",
            "dist",
            "build",
            "target",
            ".gradle",
            ".idea",
            ".vscode",
        }

        compiled = [re.compile(p) for p in parts]
        hits = []

        for path in self.repo_root.rglob("*"):
            if any(part in exclude_dirs for part in path.parts):
                continue
            if not path.is_file():
                continue
            if path.suffix not in include_ext:
                continue
            # Keep files reasonably small to avoid scanning huge lockfiles/artifacts.
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            for rx in compiled:
                m = rx.search(content)
                if m:
                    # capture a small context snippet
                    start = max(0, m.start() - 40)
                    end = min(len(content), m.end() + 40)
                    snippet = content[start:end].replace("\n", "\\n")
                    hits.append(f"{path.relative_to(self.repo_root)}: /{rx.pattern}/ ...{snippet}...")
        self.assertFalse(
            hits,
            "Deprecated API patterns were found in repository sources after upgrade:\n" + "\n".join(hits),
        )

    def test_new_configuration_keys_load_without_errors(self):
        """
        REQUIRED:
        - Ensures new configuration keys introduced by the upgrade load without errors.

        Because the specific framework/config system is unknown, CI provides:
          UPGRADE_NEW_CONFIG_KEYS: comma-separated keys to validate
          UPGRADE_CONFIG_FILE: optional path to config file (default: none)
          UPGRADE_CONFIG_FORMAT: optional (json|dotenv). If omitted, inferred from file extension.

        Behavior:
        - If CONFIG_FILE is provided and is .json, parse and ensure keys exist.
        - If CONFIG_FILE is provided and is .env, parse dotenv and ensure keys exist.
        - If no CONFIG_FILE is provided, ensure keys exist in the process environment.
        """
        keys_raw = os.environ.get("UPGRADE_NEW_CONFIG_KEYS", "").strip()
        self.assertTrue(
            keys_raw,
            "UPGRADE_NEW_CONFIG_KEYS must be set to the new config keys introduced by the upgrade (comma-separated).",
        )
        keys = [k.strip() for k in keys_raw.split(",") if k.strip()]
        self.assertTrue(keys, "No usable keys found in UPGRADE_NEW_CONFIG_KEYS.")

        cfg_file_raw = os.environ.get("UPGRADE_CONFIG_FILE", "").strip()
        cfg_format = os.environ.get("UPGRADE_CONFIG_FORMAT", "").strip().lower()

        if cfg_file_raw:
            cfg_path = (self.repo_root / cfg_file_raw).resolve()
            self.assertTrue(cfg_path.exists(), f"UPGRADE_CONFIG_FILE points to missing file: {cfg_path}")
            self.assertTrue(cfg_path.is_file(), f"UPGRADE_CONFIG_FILE is not a file: {cfg_path}")

            if not cfg_format:
                if cfg_path.suffix.lower() == ".json":
                    cfg_format = "json"
                elif cfg_path.suffix.lower() == ".env":
                    cfg_format = "dotenv"

            self.assertIn(cfg_format, {"json", "dotenv"}, f"Unsupported/unknown config format: '{cfg_format}'")

            if cfg_format == "json":
                import json

                try:
                    data = json.loads(cfg_path.read_text(encoding="utf-8"))
                except Exception as e:
                    self.fail(f"Failed to parse JSON config '{cfg_path}': {e}")

                missing = [k for k in keys if k not in data]
                self.assertFalse(
                    missing,
                    f"New configuration keys missing from JSON config '{cfg_path}': {missing}",
                )

            elif cfg_format == "dotenv":
                try:
                    text = cfg_path.read_text(encoding="utf-8", errors="strict")
                except Exception as e:
                    self.fail(f"Failed to read dotenv config '{cfg_path}': {e}")

                env_map = {}
                for line in text.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.lower().startswith("export "):
                        line = line[7:].lstrip()
                    if "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env_map[k.strip()] = v.strip().strip("'").strip('"')

                missing = [k for k in keys if k not in env_map]
                self.assertFalse(
                    missing,
                    f"New configuration keys missing from dotenv config '{cfg_path}': {missing}",
                )
        else:
            missing = [k for k in keys if k not in os.environ]
            self.assertFalse(
                missing,
                "New configuration keys must be present in environment when UPGRADE_CONFIG_FILE is not set. Missing: "
                + ", ".join(missing),
            )


if __name__ == "__main__":
    unittest.main()