import os
import re
import json
import unittest
from pathlib import Path

TARGET_LANGUAGE_RUNTIME_VERSION = os.environ.get("TARGET_LANGUAGE_RUNTIME_VERSION", "").strip()
TARGET_ANALYZER_VERSION = os.environ.get("TARGET_ANALYZER_VERSION", "").strip()


def _repo_root() -> Path:
    # Resolve repo root as current working directory (typical in CI) or test file parent
    cwd = Path.cwd().resolve()
    if (cwd / ".git").exists() or (cwd / "docs").exists():
        return cwd
    return Path(__file__).resolve().parent


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _find_first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None


def _collect_manifests(root: Path):
    candidates = [
        root / "package.json",
        root / "package-lock.json",
        root / "yarn.lock",
        root / "pnpm-lock.yaml",
        root / "pom.xml",
        root / "build.gradle",
        root / "build.gradle.kts",
        root / "requirements.txt",
        root / "Pipfile.lock",
        root / "poetry.lock",
        root / "poetry.toml",
        root / "go.mod",
        root / "go.sum",
        root / "Cargo.toml",
        root / "Cargo.lock",
        root / "Gemfile",
        root / "Gemfile.lock",
    ]
    return [p for p in candidates if p.exists()]


def _detect_ecosystem(root: Path) -> str:
    if (root / "package.json").exists():
        return "node"
    if (root / "pom.xml").exists() or (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        return "java"
    if (root / "pyproject.toml").exists() or (root / "requirements.txt").exists() or (root / "poetry.lock").exists():
        return "python"
    if (root / "go.mod").exists():
        return "go"
    if (root / "Cargo.toml").exists():
        return "rust"
    if (root / "Gemfile").exists():
        return "ruby"
    return "unknown"


def _parse_node_engine_version(package_json_text: str):
    try:
        data = json.loads(package_json_text)
    except Exception:
        return None
    engines = data.get("engines") or {}
    node = engines.get("node")
    if not node:
        return None
    # Return as-is; could be semver range. We'll compare exact only if it looks exact.
    return str(node).strip()


def _is_exact_semver(s: str) -> bool:
    return bool(re.fullmatch(r"\d+\.\d+\.\d+", s))


def _normalize_v_prefix(v: str) -> str:
    return v[1:] if v.startswith("v") else v


class TestUpgradeBacklogArtifacts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = _repo_root()
        cls.docs_security = cls.root / "docs" / "security"

    def test_required_artifacts_exist(self):
        expected = [
            self.docs_security / "prioritized-upgrade-backlog.md",
            self.docs_security / "prioritization-criteria.md",
            self.docs_security / "README.md",
        ]
        for p in expected:
            self.assertTrue(p.exists(), f"Missing required artifact: {p}")

    def test_backlog_contains_required_fields(self):
        backlog_path = self.docs_security / "prioritized-upgrade-backlog.md"
        self.assertTrue(backlog_path.exists(), f"Missing required artifact: {backlog_path}")
        text = _read_text(backlog_path)

        # Minimum required fields from spec (allow flexible casing/formatting; enforce presence)
        required_markers = [
            "dependency",
            "ecosystem",
            "current",
            "target",
            "cve",
            "outdated",
            "upgrade type",
            "breaking",
            "rationale",
            "reference",
            "priority",
            "urgency",
            "manifest",
            "lockfile",
        ]
        lower = text.lower()
        missing = [m for m in required_markers if m not in lower]
        self.assertFalse(
            missing,
            "Backlog missing required field markers (ensure the document includes these fields/columns/sections): "
            + ", ".join(missing),
        )

        # Ensure there is at least one backlog item (heuristic: any markdown table row or list item after a header)
        has_table_row = bool(re.search(r"^\s*\|\s*[^|]+\s*\|\s*[^|]+\s*\|", text, flags=re.M))
        has_list_item = bool(re.search(r"^\s*[-*]\s+\S+", text, flags=re.M))
        self.assertTrue(has_table_row or has_list_item, "Backlog appears empty (no table rows or list items found).")

    def test_prioritization_criteria_non_empty_and_actionable(self):
        criteria_path = self.docs_security / "prioritization-criteria.md"
        self.assertTrue(criteria_path.exists(), f"Missing required artifact: {criteria_path}")
        text = _read_text(criteria_path).strip()
        self.assertGreater(len(text), 200, "Prioritization criteria seems too short to be actionable.")

        # Must mention CVE severity and at least one secondary decision rule per spec
        lower = text.lower()
        self.assertRegex(lower, r"\bcve\b", "Criteria must mention CVEs.")
        self.assertRegex(lower, r"\b(critical|high|severity)\b", "Criteria must include severity-based prioritization.")
        self.assertTrue(
            any(k in lower for k in ["direct", "transitive", "internet", "reachability", "exploitability", "fix availability"]),
            "Criteria should mention at least one additional rule (direct vs transitive, internet-facing, reachability, exploitability, or fix availability).",
        )

    def test_readme_describes_refresh_process(self):
        readme_path = self.docs_security / "README.md"
        self.assertTrue(readme_path.exists(), f"Missing required artifact: {readme_path}")
        text = _read_text(readme_path).lower()

        # Must explain how to refresh dependency/CVE artifacts
        self.assertTrue(
            any(k in text for k in ["refresh", "regenerate", "update", "re-run", "rerun"]),
            "README should explain how to refresh/regenerate the security backlog artifacts.",
        )
        self.assertTrue(
            any(k in text for k in ["dependabot", "dependency graph", "sbom", "code scanning", "advisory"]),
            "README should reference data sources/tools (Dependabot/Dependency Graph/SBOM/Code Scanning/advisories).",
        )

    def test_manifest_inventory_exists_or_is_not_applicable(self):
        # Spec indicates optional exports; accept absence only if repository has no recognizable manifests.
        manifests = _collect_manifests(self.root)
        inv = self.docs_security / "dependency-inventory.md"
        inv_json = self.docs_security / "dependency-inventory.json"

        if manifests:
            self.assertTrue(
                inv.exists() or inv_json.exists(),
                "Repository contains dependency manifests/lockfiles; expected docs/security/dependency-inventory.(md|json) to exist.",
            )

    def test_outdated_baseline_exists_or_is_not_applicable(self):
        manifests = _collect_manifests(self.root)
        baseline = self.docs_security / "outdated-baseline.md"
        if manifests:
            self.assertTrue(
                baseline.exists(),
                "Repository contains dependency manifests/lockfiles; expected docs/security/outdated-baseline.md to exist.",
            )

    def test_deprecated_ad_hoc_artifacts_not_used(self):
        # Deprecated/non-spec artifacts shouldn't replace the required ones.
        # Ensure backlog isn't mistakenly written into generic locations.
        forbidden = [
            self.root / "SECURITY_BACKLOG.md",
            self.root / "UPGRADE_BACKLOG.md",
            self.root / "dependency-backlog.md",
        ]
        for p in forbidden:
            self.assertFalse(
                p.exists(),
                f"Found deprecated/ad-hoc artifact {p}; expected canonical docs/security/* artifacts per spec.",
            )


class TestUpgradeRuntimeFrameworkVersion(unittest.TestCase):
    def test_target_runtime_version_is_asserted(self):
        """
        Upgrade validation requires asserting active runtime/framework version against the exact target.
        This repository context does not specify the language/runtime; therefore the test requires the
        pipeline to provide TARGET_LANGUAGE_RUNTIME_VERSION (e.g., 3.12.4, 20.11.1, 1.22.5).
        """
        self.assertTrue(
            TARGET_LANGUAGE_RUNTIME_VERSION,
            "TARGET_LANGUAGE_RUNTIME_VERSION must be set to the EXACT target runtime version for this upgrade.",
        )

    def test_active_runtime_version_matches_target_exactly(self):
        ecosystem = _detect_ecosystem(_repo_root())

        target = TARGET_LANGUAGE_RUNTIME_VERSION
        self.assertTrue(target, "TARGET_LANGUAGE_RUNTIME_VERSION must be set.")

        if ecosystem == "python":
            import sys

            active = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            self.assertEqual(
                active,
                target,
                f"Active Python version mismatch. Expected exact {target}, got {active}.",
            )
        elif ecosystem == "node":
            # Attempt to read node version from environment typically provided in CI, else skip with hard fail.
            # We enforce exact match; accept "vX.Y.Z" or "X.Y.Z".
            active = os.environ.get("NODE_VERSION") or os.environ.get("NODEJS_VERSION") or os.environ.get("NODE_RUNTIME_VERSION")
            self.assertTrue(
                active,
                "Node ecosystem detected but active version not provided. Set NODE_VERSION (or NODEJS_VERSION/NODE_RUNTIME_VERSION) to the active Node version.",
            )
            self.assertEqual(
                _normalize_v_prefix(active.strip()),
                _normalize_v_prefix(target.strip()),
                f"Active Node version mismatch. Expected exact {target}, got {active}.",
            )
        elif ecosystem == "java":
            active = os.environ.get("JAVA_VERSION") or os.environ.get("JDK_VERSION") or os.environ.get("JAVA_RUNTIME_VERSION")
            self.assertTrue(
                active,
                "Java ecosystem detected but active version not provided. Set JAVA_VERSION (or JDK_VERSION/JAVA_RUNTIME_VERSION) to the active Java version.",
            )
            self.assertEqual(
                active.strip(),
                target.strip(),
                f"Active Java version mismatch. Expected exact {target}, got {active}.",
            )
        elif ecosystem == "go":
            active = os.environ.get("GO_VERSION") or os.environ.get("GOLANG_VERSION") or os.environ.get("GO_RUNTIME_VERSION")
            self.assertTrue(
                active,
                "Go ecosystem detected but active version not provided. Set GO_VERSION (or GOLANG_VERSION/GO_RUNTIME_VERSION) to the active Go version.",
            )
            self.assertEqual(
                active.strip().lstrip("go"),
                target.strip().lstrip("go"),
                f"Active Go version mismatch. Expected exact {target}, got {active}.",
            )
        elif ecosystem == "rust":
            active = os.environ.get("RUST_VERSION") or os.environ.get("RUSTC_VERSION") or os.environ.get("RUST_RUNTIME_VERSION")
            self.assertTrue(
                active,
                "Rust ecosystem detected but active version not provided. Set RUST_VERSION (or RUSTC_VERSION/RUST_RUNTIME_VERSION) to the active Rust version.",
            )
            self.assertEqual(
                active.strip(),
                target.strip(),
                f"Active Rust version mismatch. Expected exact {target}, got {active}.",
            )
        elif ecosystem == "ruby":
            active = os.environ.get("RUBY_VERSION") or os.environ.get("RUBY_RUNTIME_VERSION")
            self.assertTrue(
                active,
                "Ruby ecosystem detected but active version not provided. Set RUBY_VERSION (or RUBY_RUNTIME_VERSION) to the active Ruby version.",
            )
            self.assertEqual(
                active.strip(),
                target.strip(),
                f"Active Ruby version mismatch. Expected exact {target}, got {active}.",
            )
        else:
            self.fail(
                "Unable to detect ecosystem to assert runtime version. Provide a recognized manifest (e.g., package.json, pyproject.toml, pom.xml, go.mod, Cargo.toml, Gemfile) "
                "or extend the test mapping."
            )

    def test_runtime_version_is_reflected_in_manifest_or_tooling_config_when_applicable(self):
        root = _repo_root()
        ecosystem = _detect_ecosystem(root)
        target = TARGET_LANGUAGE_RUNTIME_VERSION
        self.assertTrue(target, "TARGET_LANGUAGE_RUNTIME_VERSION must be set.")

        if ecosystem == "node":
            pkg = root / "package.json"
            self.assertTrue(pkg.exists(), "Node ecosystem detected but package.json not found.")
            engine = _parse_node_engine_version(_read_text(pkg))
            self.assertTrue(engine, "package.json must declare engines.node for reproducible runtime versioning.")
            # Enforce exact only if target is exact semver; otherwise allow range containing target is too complex without semver lib.
            if _is_exact_semver(target):
                self.assertIn(
                    target,
                    engine.replace(" ", ""),
                    f"package.json engines.node should include the exact target {target}. Found: {engine}",
                )

        elif ecosystem == "python":
            # Prefer pyproject.toml requires-python if present, else allow absence.
            pyproject = root / "pyproject.toml"
            if pyproject.exists() and _is_exact_semver(target):
                text = _read_text(pyproject)
                m = re.search(r"(?im)^\s*requires-python\s*=\s*['\"]([^'\"]+)['\"]\s*$", text)
                self.assertTrue(m, "pyproject.toml exists but does not declare requires-python.")
                requires = m.group(1).strip().replace(" ", "")
                self.assertIn(
                    target,
                    requires,
                    f"pyproject.toml requires-python should include the exact target {target}. Found: {requires}",
                )


class TestUpgradeNoDeprecatedAPIsAndNewConfig(unittest.TestCase):
    def test_deprecated_sources_not_present(self):
        """
        Upgrade requires ensuring replaced/deprecated APIs no longer appear.
        In this context, treat legacy ad-hoc security backlog outputs as deprecated in favor of docs/security/*.
        """
        root = _repo_root()
        deprecated_markers = [
            "npm audit --json > security-audit.json",
            "snyk test --json",
            "owasp dependency-check",
        ]
        # Scan only docs/security and root README-like docs; avoid heavy repo-wide scans.
        scan_paths = []
        for p in [root / "README.md", root / "docs", root / "docs" / "security"]:
            if p.exists():
                scan_paths.append(p)

        text_blobs = []
        for p in scan_paths:
            if p.is_file():
                text_blobs.append(_read_text(p))
            else:
                for f in p.rglob("*.md"):
                    try:
                        text_blobs.append(_read_text(f))
                    except Exception:
                        pass

        combined = "\n".join(text_blobs).lower()
        for marker in deprecated_markers:
            self.assertNotIn(
                marker.lower(),
                combined,
                f"Found deprecated/unsupported reference '{marker}' in documentation. Ensure the upgrade uses the standardized backlog artifacts and documented sources per spec.",
            )

    def test_new_configuration_keys_load(self):
        """
        New configuration keys introduced by this upgrade:
        - docs/security/* artifacts are canonical and must be discoverable.
        - Optionally, a tool config file may exist: docs/security/config.json
          If present, it must parse and contain required keys.
        """
        cfg = _repo_root() / "docs" / "security" / "config.json"
        if not cfg.exists():
            # No config file provided; validate canonical paths exist (acts as "config keys" for this upgrade deliverable).
            required = [
                _repo_root() / "docs" / "security" / "prioritized-upgrade-backlog.md",
                _repo_root() / "docs" / "security" / "prioritization-criteria.md",
                _repo_root() / "docs" / "security" / "README.md",
            ]
            for p in required:
                self.assertTrue(p.exists(), f"Missing required upgrade artifact: {p}")
            return

        data = json.loads(_read_text(cfg))
        # Enforce keys that make the deliverable refreshable/configurable without errors.
        for key in ["dataSources", "artifacts", "prioritization"]:
            self.assertIn(key, data, f"docs/security/config.json missing required key '{key}'")

        self.assertIsInstance(data["dataSources"], list, "config.json dataSources must be a list")
        self.assertIsInstance(data["artifacts"], dict, "config.json artifacts must be an object")
        self.assertIsInstance(data["prioritization"], dict, "config.json prioritization must be an object")


if __name__ == "__main__":
    unittest.main()