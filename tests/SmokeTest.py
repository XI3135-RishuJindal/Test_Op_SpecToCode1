import os
import re
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Dict, Tuple, Optional


class UpgradeValidationTests(unittest.TestCase):
    """
    Upgrade validation tests.

    NOTE: This repository's upgrade context did not specify the target runtime/framework
    name nor the exact target version. These tests are written to be runnable and to
    enforce that the pipeline supplies the exact target version via environment variables.

    Required env vars for strict validation:
      - UPGRADE_TARGET_RUNTIME: e.g., "python"
      - UPGRADE_TARGET_VERSION: e.g., "3.12.4"
    Optional env vars:
      - UPGRADE_DEPRECATED_API_REGEX: regex for deprecated API usage to assert absent
      - UPGRADE_NEW_CONFIG_KEYS: comma-separated keys that must load from config
      - UPGRADE_CONFIG_PATH: path to config file to parse (default: auto-detect)
    """

    @staticmethod
    def _run(cmd, cwd: Optional[Path] = None) -> Tuple[int, str]:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return p.returncode, p.stdout

    @staticmethod
    def _repo_root() -> Path:
        # Best-effort: walk up until we find a VCS marker or stop.
        here = Path(__file__).resolve()
        for p in [here] + list(here.parents):
            if (p / ".git").exists() or (p / "pyproject.toml").exists() or (p / "package.json").exists():
                return p
        return here.parent

    def _require_env(self, key: str) -> str:
        v = os.environ.get(key, "").strip()
        self.assertTrue(v, f"Missing required environment variable: {key}")
        return v

    def test_000_target_runtime_and_version_are_exact(self):
        target_runtime = self._require_env("UPGRADE_TARGET_RUNTIME").lower()
        target_version = self._require_env("UPGRADE_TARGET_VERSION")

        if target_runtime == "python":
            active = sys.version.split()[0]
            self.assertEqual(
                active,
                target_version,
                f"Active Python runtime version mismatch. Expected EXACT {target_version}, got {active}.",
            )
        else:
            self.fail(
                f"Unsupported/unknown runtime '{target_runtime}'. "
                f"Provide a supported runtime or extend tests. "
                f"Target version was '{target_version}'."
            )

    def test_010_critical_application_path_starts_and_responds(self):
        """
        Critical path validation for a typical Python app: ensure module import + CLI start works.

        This tries, in order:
          1) If APP_MODULE env var is set: import it.
          2) If an executable script path is set via APP_START_CMD: run it and expect exit 0.
          3) Else: attempt to run 'python -m <package>' if APP_PACKAGE env var is set.

        These are intentionally strict upgrade-validation hooks; the pipeline should set one.
        """
        app_module = os.environ.get("APP_MODULE", "").strip()
        app_start_cmd = os.environ.get("APP_START_CMD", "").strip()
        app_package = os.environ.get("APP_PACKAGE", "").strip()

        if app_module:
            try:
                __import__(app_module)
            except Exception as e:
                self.fail(f"Failed to import critical application module '{app_module}' after upgrade: {e!r}")
            return

        if app_start_cmd:
            cmd = app_start_cmd.split()
            rc, out = self._run(cmd, cwd=self._repo_root())
            self.assertEqual(rc, 0, f"Critical application start command failed: {app_start_cmd}\n{out}")
            return

        if app_package:
            rc, out = self._run([sys.executable, "-m", app_package], cwd=self._repo_root())
            self.assertEqual(rc, 0, f"Critical application package start failed: python -m {app_package}\n{out}")
            return

        self.fail(
            "No critical application path configured. Set one of: APP_MODULE, APP_START_CMD, APP_PACKAGE."
        )

    def test_020_deprecated_apis_replaced_no_longer_present(self):
        """
        Assert deprecated APIs removed from the codebase.

        The upgrade context did not specify which APIs were deprecated/replaced, so this test
        is parameterized by UPGRADE_DEPRECATED_API_REGEX (required for this check to be meaningful).
        """
        pattern = os.environ.get("UPGRADE_DEPRECATED_API_REGEX", "").strip()
        self.assertTrue(
            pattern,
            "Missing UPGRADE_DEPRECATED_API_REGEX. Provide a regex matching deprecated API symbols/paths "
            "that should no longer appear after upgrade.",
        )
        rx = re.compile(pattern)

        root = self._repo_root()

        # Search common source file extensions without adding dependencies.
        exts = {
            ".py",
            ".pyi",
            ".txt",
            ".md",
            ".rst",
            ".toml",
            ".yaml",
            ".yml",
            ".json",
            ".ini",
            ".cfg",
            ".env",
            ".sh",
            ".bat",
            ".ps1",
        }
        ignore_dirs = {".git", ".venv", "venv", "node_modules", "dist", "build", ".tox", ".pytest_cache", "__pycache__"}
        offenders = []

        for path in root.rglob("*"):
            if path.is_dir():
                continue
            if any(part in ignore_dirs for part in path.parts):
                continue
            if path.suffix.lower() not in exts:
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if rx.search(content):
                offenders.append(str(path.relative_to(root)))

        self.assertFalse(
            offenders,
            f"Deprecated API usage still present (pattern: {pattern}). Offending files:\n- "
            + "\n- ".join(sorted(offenders)),
        )

    def test_030_new_configuration_keys_load_without_errors(self):
        """
        Validate new configuration keys introduced by the upgrade can be loaded.

        Since config system/framework isn't specified, this test does a conservative parse of
        common config files and asserts keys are present in at least one detected config.

        Provide:
          - UPGRADE_NEW_CONFIG_KEYS: comma-separated list of keys (required)
          - UPGRADE_CONFIG_PATH: explicit config file path (optional)
        """
        keys_raw = os.environ.get("UPGRADE_NEW_CONFIG_KEYS", "").strip()
        self.assertTrue(
            keys_raw,
            "Missing UPGRADE_NEW_CONFIG_KEYS. Provide comma-separated new config keys that must load.",
        )
        required_keys = [k.strip() for k in keys_raw.split(",") if k.strip()]
        self.assertTrue(required_keys, "UPGRADE_NEW_CONFIG_KEYS did not contain any keys.")

        root = self._repo_root()
        cfg_path_env = os.environ.get("UPGRADE_CONFIG_PATH", "").strip()

        candidate_paths = []
        if cfg_path_env:
            candidate_paths.append((root / cfg_path_env).resolve())
        else:
            # Auto-detect common config files
            for name in [
                "pyproject.toml",
                "config.toml",
                "config.yaml",
                "config.yml",
                "appsettings.json",
                "settings.json",
                ".env",
                ".env.local",
                "setup.cfg",
                "tox.ini",
            ]:
                p = root / name
                if p.exists() and p.is_file():
                    candidate_paths.append(p.resolve())

        self.assertTrue(
            candidate_paths,
            "Could not find any config files to validate. Set UPGRADE_CONFIG_PATH or add a recognizable config.",
        )

        parsed_any = False
        found_keys = set()

        for p in candidate_paths:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            parsed = self._parse_config_best_effort(p, text)
            if parsed is None:
                continue
            parsed_any = True

            # Support dotted keys as nested dict paths (best-effort)
            for key in required_keys:
                if self._has_key(parsed, key):
                    found_keys.add(key)

        self.assertTrue(parsed_any, "Failed to parse any config file (best-effort parsers did not apply).")
        missing = [k for k in required_keys if k not in found_keys]
        self.assertFalse(
            missing,
            "New configuration keys missing or failed to load from config: " + ", ".join(missing),
        )

    @staticmethod
    def _parse_config_best_effort(path: Path, text: str) -> Optional[Dict]:
        suffix = path.suffix.lower()
        name = path.name.lower()

        if suffix == ".json":
            import json

            try:
                return json.loads(text) if text.strip() else {}
            except Exception:
                return None

        if suffix in {".yml", ".yaml"}:
            # No external deps allowed; minimal YAML subset: key: value, nesting via indentation (2+ spaces).
            return UpgradeValidationTests._parse_minimal_yaml(text)

        if suffix == ".toml" or name == "pyproject.toml":
            # Python 3.11+ has tomllib; fallback to None if not available.
            try:
                import tomllib  # type: ignore
            except Exception:
                return None
            try:
                return tomllib.loads(text) if text.strip() else {}
            except Exception:
                return None

        if name in {".env", ".env.local"}:
            return UpgradeValidationTests._parse_dotenv(text)

        if suffix in {".ini", ".cfg"} or name in {"setup.cfg", "tox.ini"}:
            import configparser

            cp = configparser.ConfigParser()
            try:
                cp.read_string(text)
            except Exception:
                return None
            d = {"DEFAULT": dict(cp.defaults())}
            for section in cp.sections():
                d[section] = dict(cp.items(section))
            return d

        return None

    @staticmethod
    def _parse_dotenv(text: str) -> Dict:
        d: Dict[str, str] = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            d[k.strip()] = v.strip().strip("'").strip('"')
        return d

    @staticmethod
    def _parse_minimal_yaml(text: str) -> Optional[Dict]:
        # Minimal YAML parser for simple mappings; returns None if structure seems incompatible.
        root: Dict = {}
        stack = [(0, root)]
        for raw in text.splitlines():
            if not raw.strip() or raw.lstrip().startswith("#"):
                continue
            if "\t" in raw:
                return None
            indent = len(raw) - len(raw.lstrip(" "))
            line = raw.strip()
            if ":" not in line:
                return None
            key, rest = line.split(":", 1)
            key = key.strip()
            value = rest.strip()
            # Determine current container based on indentation
            while stack and indent < stack[-1][0]:
                stack.pop()
            if not stack:
                return None
            cur = stack[-1][1]
            if value == "":
                nxt: Dict = {}
                cur[key] = nxt
                stack.append((indent + 2, nxt))
            else:
                # scalar
                cur[key] = value.strip("'").strip('"')
        return root

    @staticmethod
    def _has_key(obj: object, dotted_key: str) -> bool:
        # Supports dotted lookup into nested dicts; also supports case-insensitive match for INI-style keys.
        parts = dotted_key.split(".")
        cur = obj
        for part in parts:
            if isinstance(cur, dict):
                if part in cur:
                    cur = cur[part]
                    continue
                # case-insensitive fallback
                lower_map = {str(k).lower(): k for k in cur.keys()}
                if part.lower() in lower_map:
                    cur = cur[lower_map[part.lower()]]
                    continue
                return False
            return False
        return True


if __name__ == "__main__":
    unittest.main()