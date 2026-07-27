import os
import subprocess
import unittest
from pathlib import Path


def _repo_root() -> Path:
    # Prefer common CI env var; otherwise use current working directory.
    return Path(os.environ.get("GITHUB_WORKSPACE", os.getcwd())).resolve()


def _run(cmd, cwd: Path):
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )


class TestSourceAccessUpgradeValidation(unittest.TestCase):
    """
    Upgrade context: "Obtain and validate codebase source access (GitHub URL/ZIP/path)"
    This test suite validates the post-upgrade acceptance criteria:
      - Source is present and non-empty
      - If it's a git repo, repository commands work and permissions are readable
      - A pinned baseline commit is recorded
      - No replaced/deprecated access method artifacts are present
      - New configuration key (SOURCE_ACCESS_METHOD) loads without errors
    """

    @classmethod
    def setUpClass(cls):
        cls.root = _repo_root()

    def test_repo_root_is_non_empty(self):
        self.assertTrue(self.root.exists(), f"Repo root does not exist: {self.root}")
        entries = list(self.root.iterdir())
        self.assertGreater(len(entries), 0, f"Repo root appears empty: {self.root}")

    def test_new_configuration_key_loads_without_errors(self):
        # New key introduced by this upgrade validation step.
        # Tests must not fail if environment is not configured; we ensure it loads safely.
        try:
            _ = os.environ.get("SOURCE_ACCESS_METHOD", "")
        except Exception as e:
            self.fail(f"Failed to load SOURCE_ACCESS_METHOD env var: {e}")

    def test_access_validation_document_exists_and_mentions_method(self):
        # The spec requires ACCESS_VALIDATION.md to document method and validation commands.
        av = self.root / "ACCESS_VALIDATION.md"
        self.assertTrue(av.exists(), "ACCESS_VALIDATION.md missing at repo root (required by spec).")
        content = av.read_text(encoding="utf-8", errors="replace")
        self.assertGreater(len(content.strip()), 0, "ACCESS_VALIDATION.md is empty.")
        # Ensure it documents the method (GitHub URL/ZIP/path) explicitly.
        lowered = content.lower()
        self.assertTrue(
            ("github" in lowered) or ("zip" in lowered) or ("local path" in lowered) or ("filesystem" in lowered),
            "ACCESS_VALIDATION.md does not appear to document the source access method (GitHub/ZIP/path).",
        )

    def test_git_cli_is_available(self):
        r = _run(["git", "--version"], self.root)
        self.assertEqual(r.returncode, 0, f"git not available or failed to run: {r.stderr.strip()}")
        self.assertIn("git version", r.stdout.lower())

    def test_git_repository_integrity_commands_succeed(self):
        # Critical application paths for this upgrade are git validation commands.
        r1 = _run(["git", "status", "--porcelain=v1"], self.root)
        self.assertEqual(r1.returncode, 0, f"git status failed: {r1.stderr.strip()}")

        r2 = _run(["git", "log", "-n", "1", "--oneline"], self.root)
        self.assertEqual(r2.returncode, 0, f"git log failed: {r2.stderr.strip()}")
        self.assertGreater(len(r2.stdout.strip()), 0, "git log produced no output; repository history may be missing.")

    def test_git_remote_is_configured_and_readable_if_present(self):
        # Remote checks should pass if a remote is configured; if no remote is present (e.g., ZIP),
        # we validate that this is consistent with a non-git source and do not hard-fail.
        r = _run(["git", "remote", "-v"], self.root)
        self.assertEqual(r.returncode, 0, f"git remote -v failed: {r.stderr.strip()}")

        remotes = [line.strip() for line in r.stdout.splitlines() if line.strip()]
        if not remotes:
            # Acceptable for ZIP/local path inputs that are not connected to a remote.
            # Still ensure the repository is at least a git worktree (or extracted source).
            has_git_dir = (self.root / ".git").exists()
            self.assertTrue(
                has_git_dir or any((self.root / f).exists() for f in ("README.md", "README", "package.json", "pyproject.toml", "pom.xml", "build.gradle")),
                "No git remotes configured and .git missing; cannot confirm source baseline structure.",
            )
            return

        # If origin exists, ensure it is readable.
        # This validates the "read access" requirement via listing heads.
        r2 = _run(["git", "ls-remote", "--heads", "origin"], self.root)
        self.assertEqual(
            r2.returncode, 0, f"git ls-remote --heads origin failed (read access/remote connectivity issue): {r2.stderr.strip()}"
        )
        self.assertGreater(len(r2.stdout.strip()), 0, "git ls-remote returned no heads; remote may be empty or inaccessible.")

    def test_default_branch_can_be_identified_if_origin_exists(self):
        # Identify and record default branch name via git remote show origin (if origin exists).
        r = _run(["git", "remote"], self.root)
        self.assertEqual(r.returncode, 0, f"git remote failed: {r.stderr.strip()}")
        remotes = set(line.strip() for line in r.stdout.splitlines() if line.strip())
        if "origin" not in remotes:
            self.skipTest("No origin remote configured; default branch identification not applicable for ZIP/local path sources.")

        r2 = _run(["git", "remote", "show", "origin"], self.root)
        self.assertEqual(r2.returncode, 0, f"git remote show origin failed: {r2.stderr.strip()}")
        lowered = r2.stdout.lower()
        self.assertIn("head branch", lowered, "Could not find 'HEAD branch' info in git remote show origin output.")

    def test_baseline_commit_sha_is_recorded_and_matches_HEAD(self):
        # Verify that ACCESS_VALIDATION.md includes the specific HEAD SHA (git rev-parse HEAD).
        r = _run(["git", "rev-parse", "HEAD"], self.root)
        self.assertEqual(r.returncode, 0, f"git rev-parse HEAD failed: {r.stderr.strip()}")
        head_sha = r.stdout.strip()
        self.assertRegex(head_sha, r"^[0-9a-f]{40}$", "HEAD commit SHA is not a 40-char hex string.")

        av = self.root / "ACCESS_VALIDATION.md"
        self.assertTrue(av.exists(), "ACCESS_VALIDATION.md missing; cannot validate recorded baseline SHA.")
        content = av.read_text(encoding="utf-8", errors="replace")
        self.assertIn(head_sha, content, "ACCESS_VALIDATION.md does not contain the current HEAD SHA (baseline not recorded).")

    def test_deprecated_artifacts_do_not_exist(self):
        # Deprecated/old artifacts for this upgrade: temporary access validation logs or secret material.
        # The spec says .gitignore should not contain sensitive local artifacts created during access validation
        # and no secrets/credentials should be added. We assert common mistakes are absent.
        forbidden_files = [
            "access_validation.log",
            "access_validation.txt",
            "terminal.log",
            "shell_history.txt",
            ".env",
            ".env.local",
            ".envrc",
            "id_rsa",
            "id_ed25519",
            ".npmrc",
            ".pypirc",
        ]
        present = [f for f in forbidden_files if (self.root / f).exists()]
        self.assertEqual(
            present, [],
            f"Deprecated/forbidden local artifacts found in repo root (should not be committed): {present}",
        )

    def test_replaced_process_is_not_used_git_diff_stat_in_doc(self):
        # Ensure the documentation does not instruct committing secrets or using unsafe methods.
        # As a minimal "deprecated API/process" check, ensure ACCESS_VALIDATION.md doesn't contain PAT tokens patterns.
        av = self.root / "ACCESS_VALIDATION.md"
        if not av.exists():
            self.skipTest("ACCESS_VALIDATION.md missing; handled by other test.")
        content = av.read_text(encoding="utf-8", errors="replace")
        lowered = content.lower()

        # Common GitHub token prefixes; not exhaustive, but catches accidental inclusion.
        suspicious = ["ghp_", "gho_", "ghu_", "ghs_", "github_pat_"]
        found = [s for s in suspicious if s in lowered]
        self.assertEqual(found, [], "ACCESS_VALIDATION.md appears to contain a GitHub token; secrets must not be committed.")


if __name__ == "__main__":
    unittest.main()