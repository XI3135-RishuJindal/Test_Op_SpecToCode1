import os
import sys
import unittest
import platform
import subprocess
import re
from typing import Optional, Tuple


def _env(name: str) -> Optional[str]:
    v = os.environ.get(name)
    return v.strip() if isinstance(v, str) and v.strip() else None


def _run(cmd, cwd: Optional[str] = None) -> Tuple[int, str]:
    p = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=isinstance(cmd, str),
        env=os.environ.copy(),
    )
    return p.returncode, (p.stdout or "").strip()


def _parse_semver(s: str) -> Tuple[int, int, int, str]:
    """
    Parse versions like:
      3.12.4
      v18.20.3
      21.6.2+build
      1.2.3-rc.1
    Returns (major, minor, patch, suffix)
    """
    s = s.strip()
    if s.startswith("v"):
        s = s[1:]
    # take first occurrence of x.y.z
    m = re.search(r"(\d+)\.(\d+)\.(\d+)(.*)$", s)
    if not m:
        raise ValueError(f"Unable to parse semantic version from: {s!r}")
    return int(m.group(1)), int(m.group(2)), int(m.group(3)), (m.group(4) or "").strip()


def _detect_runtime_and_version() -> Tuple[str, str]:
    """
    Best-effort runtime detection with no extra deps.
    Supports common runtimes: python, node, java, dotnet, go, ruby, php.
    Priority: explicit UPGRADE_RUNTIME env, then detect based on availability.
    """
    forced = _env("UPGRADE_RUNTIME")
    if forced:
        rt = forced.lower()
        if rt == "python":
            return "python", platform.python_version()
        if rt == "node":
            rc, out = _run(["node", "--version"])
            if rc != 0:
                raise AssertionError(f"UPGRADE_RUNTIME=node but node not available: {out}")
            return "node", out.splitlines()[0].strip()
        if rt == "java":
            rc, out = _run(["java", "-version"])
            if rc != 0:
                raise AssertionError(f"UPGRADE_RUNTIME=java but java not available: {out}")
            # java -version prints to stderr; we redirected to stdout
            first = out.splitlines()[0].strip()
            return "java", first
        if rt == "dotnet":
            rc, out = _run(["dotnet", "--version"])
            if rc != 0:
                raise AssertionError(f"UPGRADE_RUNTIME=dotnet but dotnet not available: {out}")
            return "dotnet", out.splitlines()[0].strip()
        if rt == "go":
            rc, out = _run(["go", "version"])
            if rc != 0:
                raise AssertionError(f"UPGRADE_RUNTIME=go but go not available: {out}")
            return "go", out.splitlines()[0].strip()
        if rt == "ruby":
            rc, out = _run(["ruby", "--version"])
            if rc != 0:
                raise AssertionError(f"UPGRADE_RUNTIME=ruby but ruby not available: {out}")
            return "ruby", out.splitlines()[0].strip()
        if rt == "php":
            rc, out = _run(["php", "--version"])
            if rc != 0:
                raise AssertionError(f"UPGRADE_RUNTIME=php but php not available: {out}")
            return "php", out.splitlines()[0].strip()
        raise AssertionError(f"Unsupported UPGRADE_RUNTIME={forced!r}")

    # auto-detect: python is always present for this test file
    return "python", platform.python_version()


def _repo_root() -> str:
    rc, out = _run(["git", "rev-parse", "--show-toplevel"])
    if rc == 0 and out:
        return out.strip()
    return os.getcwd()


class UpgradeValidationTests(unittest.TestCase):
    """
    Upgrade validation tests intended for dependency patch/minor upgrades.

    This suite is designed to be runnable without repo-specific dependencies,
    but requires upgrade context to be supplied via environment variables
    so it can assert the EXACT target version and verify upgrade-specific behavior.

    Required environment variables:
      - UPGRADE_TARGET_VERSION: exact semantic version (x.y.z) expected to be active.
        (For non-semver runtimes/frameworks, provide the exact version string and set UPGRADE_EXACT_MATCH=1.)
    Optional:
      - UPGRADE_RUNTIME: python|node|java|dotnet|go|ruby|php (forces runtime detection)
      - UPGRADE_EXACT_MATCH: "1" to require string-equality match rather than semver comparison
      - UPGRADE_CRITICAL_PATH_CMD: a command to execute as a critical application path
      - UPGRADE_NEW_CONFIG_KEYS: comma-separated config keys expected to load
      - UPGRADE_CONFIG_FILE: path to a config file to validate (best-effort parsing)
      - UPGRADE_DEPRECATED_TOKEN: a string that must not appear in the codebase (deprecated API)
      - UPGRADE_DEPRECATED_GREP: regex (python re) that must not match any tracked source file
      - UPGRADE_REPLACEMENT_TOKEN: a string that must appear at least once (replacement usage)
      - UPGRADE_LOCKFILE: lockfile path (e.g., package-lock.json, poetry.lock, Gemfile.lock)
      - UPGRADE_EXPECTED_PACKAGE_VERSIONS: comma-separated "name@x.y.z" pairs to verify in lockfiles (best-effort)
    """

    @classmethod
    def setUpClass(cls):
        cls.repo = _repo_root()
        cls.runtime, cls.runtime_version = _detect_runtime_and_version()

    def test_active_runtime_exact_target_version(self):
        target = _env("UPGRADE_TARGET_VERSION")
        self.assertTrue(
            target,
            "UPGRADE_TARGET_VERSION must be set to the EXACT target version for upgrade validation.",
        )

        exact_match = _env("UPGRADE_EXACT_MATCH") == "1"
        active = self.runtime_version.strip()

        if exact_match:
            self.assertEqual(
                active,
                target,
                f"Active {self.runtime} version must match EXACT target. active={active!r} target={target!r}",
            )
            return

        # semver compare for common cases where active may include prefix/suffix
        a = _parse_semver(active)
        t = _parse_semver(target)

        self.assertEqual(
            a[:3],
            t[:3],
            f"Active {self.runtime} version must match EXACT target semver. active={active!r} target={target!r}",
        )

    def test_critical_application_path_executes_successfully(self):
        """
        Critical path should be provided by the upgrade context since repo/framework is unknown.
        This is not a generic smoke test: it asserts an upgrade-specific critical path command
        still works under the upgraded runtime/dependencies.
        """
        cmd = _env("UPGRADE_CRITICAL_PATH_CMD")
        self.assertTrue(
            cmd,
            "UPGRADE_CRITICAL_PATH_CMD must be set to a real critical application path command "
            "(e.g., 'python -m yourapp --version', 'node dist/server.js --healthcheck', "
            "'./gradlew test -x ...', 'dotnet test', etc.).",
        )

        rc, out = _run(cmd, cwd=self.repo)
        self.assertEqual(
            rc,
            0,
            f"Critical application path command failed under upgraded environment.\n"
            f"cmd={cmd!r}\nexit={rc}\noutput:\n{out}\n",
        )

    def test_deprecated_apis_removed_or_replaced(self):
        """
        Verifies deprecated APIs that were replaced in this upgrade no longer appear,
        and optionally verifies their replacements appear.
        """
        deprecated_token = _env("UPGRADE_DEPRECATED_TOKEN")
        deprecated_grep = _env("UPGRADE_DEPRECATED_GREP")
        replacement_token = _env("UPGRADE_REPLACEMENT_TOKEN")

        self.assertTrue(
            deprecated_token or deprecated_grep,
            "Set UPGRADE_DEPRECATED_TOKEN (literal string) and/or UPGRADE_DEPRECATED_GREP (regex) "
            "to verify deprecated APIs removed in this upgrade.",
        )

        # Enumerate tracked files via git to avoid scanning build outputs/vendor directories.
        rc, files_out = _run(["git", "ls-files"], cwd=self.repo)
        self.assertEqual(rc, 0, f"Unable to list repo files via git: {files_out}")
        files = [f for f in files_out.splitlines() if f.strip()]

        # only scan plausible text/source files
        scan_exts = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".java",
            ".kt",
            ".kts",
            ".cs",
            ".go",
            ".rb",
            ".php",
            ".scala",
            ".gradle",
            ".xml",
            ".yml",
            ".yaml",
            ".json",
            ".toml",
            ".ini",
            ".cfg",
            ".properties",
            ".md",
            ".txt",
        }

        dep_regex = re.compile(deprecated_grep) if deprecated_grep else None
        found_deprecated = []
        found_replacement = 0

        for rel in files:
            _, ext = os.path.splitext(rel)
            if ext and ext.lower() not in scan_exts:
                continue
            path = os.path.join(self.repo, rel)
            try:
                with open(path, "rb") as fh:
                    data = fh.read()
                # skip likely binary
                if b"\x00" in data:
                    continue
                text = data.decode("utf-8", errors="replace")
            except OSError:
                continue

            if deprecated_token and deprecated_token in text:
                found_deprecated.append(rel)

            if dep_regex and dep_regex.search(text):
                found_deprecated.append(rel)

            if replacement_token and replacement_token in text:
                found_replacement += 1

        self.assertEqual(
            found_deprecated,
            [],
            "Deprecated API usage still present after upgrade. "
            f"Matches found in files: {sorted(set(found_deprecated))}",
        )

        if replacement_token:
            self.assertGreater(
                found_replacement,
                0,
                "Replacement API token was not found anywhere; expected at least one usage "
                f"of {replacement_token!r} to confirm migration.",
            )

    def test_new_configuration_keys_load_without_errors(self):
        """
        Verifies new configuration keys introduced by the upgrade can be loaded/recognized.
        Since framework is unknown, this test supports two strategies:
          1) Verify keys exist in a provided config file (UPGRADE_CONFIG_FILE).
          2) Verify app can start/load config via UPGRADE_CRITICAL_PATH_CMD and that the keys are present in env.

        To avoid false positives, require explicit UPGRADE_NEW_CONFIG_KEYS.
        """
        keys_csv = _env("UPGRADE_NEW_CONFIG_KEYS")
        self.assertTrue(
            keys_csv,
            "UPGRADE_NEW_CONFIG_KEYS must be set (comma-separated) to validate new config keys introduced by upgrade.",
        )
        keys = [k.strip() for k in keys_csv.split(",") if k.strip()]
        self.assertTrue(keys, "UPGRADE_NEW_CONFIG_KEYS did not contain any keys.")

        cfg_file = _env("UPGRADE_CONFIG_FILE")
        if cfg_file:
            cfg_path = cfg_file if os.path.isabs(cfg_file) else os.path.join(self.repo, cfg_file)
            self.assertTrue(os.path.exists(cfg_path), f"UPGRADE_CONFIG_FILE does not exist: {cfg_path}")
            with open(cfg_path, "rb") as fh:
                data = fh.read()
            self.assertNotIn(b"\x00", data, "Config file appears to be binary.")
            text = data.decode("utf-8", errors="replace")

            missing = [k for k in keys if k not in text]
            self.assertEqual(
                missing,
                [],
                f"New config keys missing from config file {cfg_file!r}: {missing}",
            )
        else:
            # No config file provided; require env vars to exist as a proxy for loadable keys.
            missing_env = [k for k in keys if _env(k) is None]
            self.assertEqual(
                missing_env,
                [],
                "No UPGRADE_CONFIG_FILE provided; expected new config keys to be supplied via environment "
                f"variables. Missing: {missing_env}",
            )

        # Additionally ensure critical path doesn't error when these keys are present.
        cmd = _env("UPGRADE_CRITICAL_PATH_CMD")
        self.assertTrue(
            cmd,
            "UPGRADE_CRITICAL_PATH_CMD must be set so we can verify new config keys don't cause load errors.",
        )
        rc, out = _run(cmd, cwd=self.repo)
        self.assertEqual(
            rc,
            0,
            "Application failed to run with new configuration keys after upgrade.\n"
            f"cmd={cmd!r}\nexit={rc}\noutput:\n{out}\n",
        )

    def test_upgraded_dependencies_reflected_in_lockfile_when_provided(self):
        """
        Upgrade-specific validation that expected patched versions are present.
        Best-effort parsing across common lockfile types; requires explicit expectations.

        Env:
          - UPGRADE_LOCKFILE: path to lockfile
          - UPGRADE_EXPECTED_PACKAGE_VERSIONS: "name@x.y.z,name2@a.b.c"
        """
        lockfile = _env("UPGRADE_LOCKFILE")
        expected = _env("UPGRADE_EXPECTED_PACKAGE_VERSIONS")
        if not lockfile or not expected:
            self.skipTest(
                "Set UPGRADE_LOCKFILE and UPGRADE_EXPECTED_PACKAGE_VERSIONS to verify patched dependency versions."
            )

        lock_path = lockfile if os.path.isabs(lockfile) else os.path.join(self.repo, lockfile)
        self.assertTrue(os.path.exists(lock_path), f"Lockfile not found: {lock_path}")

        with open(lock_path, "rb") as fh:
            data = fh.read()
        self.assertNotIn(b"\x00", data, "Lockfile appears to be binary.")
        text = data.decode("utf-8", errors="replace")

        pairs = []
        for item in expected.split(","):
            item = item.strip()
            if not item:
                continue
            if "@" not in item:
                self.fail(
                    f"Invalid entry in UPGRADE_EXPECTED_PACKAGE_VERSIONS: {item!r}. Expected format 'name@x.y.z'."
                )
            name, ver = item.rsplit("@", 1)
            name = name.strip()
            ver = ver.strip()
            if not name or not ver:
                self.fail(f"Invalid entry in UPGRADE_EXPECTED_PACKAGE_VERSIONS: {item!r}.")
            pairs.append((name, ver))

        missing = []
        for name, ver in pairs:
            # best-effort patterns across lockfile formats
            patterns = [
                rf'"{re.escape(name)}"\s*:\s*{{[^}}]*"version"\s*:\s*"{re.escape(ver)}"',  # package-lock v2/v3
                rf'"{re.escape(name)}@[^"]*"\s*:\s*{{[^}}]*"version"\s*:\s*"{re.escape(ver)}"',  # yarn lock v2+ json-ish
                rf'^{re.escape(name)}\s+\({re.escape(ver)}\)',  # pnpm-lock style (rare)
                rf'^{re.escape(name)}\s+\({re.escape(ver)}',  # bundler (Gemfile.lock) sometimes: "    name (ver)"
                rf'^\s*{re.escape(name)}\s*\({re.escape(ver)}\)',  # Gemfile.lock
                rf'^{re.escape(name)}=={re.escape(ver)}$',  # requirements freeze
                rf'{re.escape(name)}\s*==\s*{re.escape(ver)}',  # requirements.txt
                rf'{re.escape(name)}\s*{re.escape(ver)}',  # fallback
            ]
            if not any(re.search(p, text, flags=re.MULTILINE) for p in patterns):
                missing.append(f"{name}@{ver}")

        self.assertEqual(
            missing,
            [],
            f"Expected patched dependency versions not found in {lockfile!r}: {missing}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)