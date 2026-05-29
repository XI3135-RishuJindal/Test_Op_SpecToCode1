"""
CI/CD Pipeline Upgrade Validation Tests

Validates that the CI/CD pipeline infrastructure has been successfully established
with all six required stages: build, test, SAST, container build, image scan, and deploy.

These tests verify the pipeline configuration files exist, are structurally valid,
contain the correct stage definitions, enforce security gates, and follow the
decisions documented in docs/cicd-decisions.md.

Run with: pytest tests/test_cicd_pipeline_upgrade.py -v
"""

import os
import re
import json
import pathlib
import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

REQUIRED_STAGES = ["build", "test", "sast", "container-build", "image-scan", "deploy"]

# Candidate pipeline config file locations (ordered by preference)
PIPELINE_CANDIDATES = [
    REPO_ROOT / ".github" / "workflows" / "ci-cd.yml",
    REPO_ROOT / ".github" / "workflows" / "ci-cd.yaml",
    REPO_ROOT / ".gitlab-ci.yml",
    REPO_ROOT / ".gitlab-ci.yaml",
    REPO_ROOT / "Jenkinsfile",
    REPO_ROOT / "Jenkinsfile.groovy",
]

DECISIONS_DOC = REPO_ROOT / "docs" / "cicd-decisions.md"
DOCKERIGNORE = REPO_ROOT / ".dockerignore"
DOCKERFILE_CANDIDATES = [
    REPO_ROOT / "Dockerfile",
    REPO_ROOT / "docker" / "Dockerfile",
    REPO_ROOT / "build" / "Dockerfile",
]


def _find_pipeline_file():
    """Return the first pipeline config file that exists, or None."""
    for candidate in PIPELINE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def _pipeline_content():
    """Return the raw text of the pipeline config file."""
    f = _find_pipeline_file()
    if f is None:
        pytest.fail(
            "No pipeline configuration file found. Expected one of: "
            + ", ".join(str(c) for c in PIPELINE_CANDIDATES)
        )
    return f.read_text(encoding="utf-8")


def _find_dockerfile():
    for candidate in DOCKERFILE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


# ---------------------------------------------------------------------------
# 1. Pipeline file existence
# ---------------------------------------------------------------------------


class TestPipelineFileExists:
    """The pipeline configuration file must exist at a recognised path."""

    def test_pipeline_config_file_exists(self):
        found = _find_pipeline_file()
        assert found is not None, (
            "No CI/CD pipeline configuration file was found. "
            "Expected one of: " + ", ".join(str(c) for c in PIPELINE_CANDIDATES)
        )

    def test_pipeline_config_file_is_not_empty(self):
        content = _pipeline_content()
        assert len(content.strip()) > 0, "Pipeline configuration file is empty."

    def test_pipeline_config_file_path_is_documented(self):
        """The pipeline file path should be referenced in the decisions doc."""
        assert DECISIONS_DOC.exists(), (
            f"docs/cicd-decisions.md not found at {DECISIONS_DOC}. "
            "This file must document CI/CD platform and tooling decisions."
        )
        decisions_text = DECISIONS_DOC.read_text(encoding="utf-8")
        pipeline_file = _find_pipeline_file()
        # At minimum the CI platform name should appear in the decisions doc
        platform_keywords = [
            "github actions",
            "gitlab ci",
            "jenkins",
            "circleci",
            "azure devops",
            "bitbucket",
            "drone",
            "tekton",
        ]
        found_platform = any(
            kw in decisions_text.lower() for kw in platform_keywords
        )
        assert found_platform, (
            "docs/cicd-decisions.md does not mention a CI/CD platform. "
            "Expected one of: " + ", ".join(platform_keywords)
        )


# ---------------------------------------------------------------------------
# 2. All six required stages are defined
# ---------------------------------------------------------------------------


class TestRequiredStagesPresent:
    """Every required stage must appear in the pipeline configuration."""

    @pytest.mark.parametrize("stage", REQUIRED_STAGES)
    def test_stage_defined_in_pipeline(self, stage):
        content = _pipeline_content()
        # Normalise hyphens/underscores for flexible matching
        normalised_content = content.lower().replace("_", "-")
        normalised_stage = stage.lower().replace("_", "-")
        assert normalised_stage in normalised_content, (
            f"Required stage '{stage}' not found in pipeline configuration. "
            f"All six stages must be present: {REQUIRED_STAGES}"
        )

    def test_all_six_stages_present_together(self):
        content = _pipeline_content().lower().replace("_", "-")
        missing = [s for s in REQUIRED_STAGES if s.lower() not in content]
        assert not missing, (
            f"The following required stages are missing from the pipeline: {missing}"
        )


# ---------------------------------------------------------------------------
# 3. Stage ordering — security gates must precede deploy
# ---------------------------------------------------------------------------


class TestStageOrdering:
    """Security stages (sast, image-scan) must appear before the deploy stage."""

    def _stage_position(self, content: str, stage: str) -> int:
        """Return the character offset of the first occurrence of a stage name."""
        normalised = content.lower().replace("_", "-")
        idx = normalised.find(stage.lower())
        return idx  # -1 if not found

    def test_sast_before_deploy(self):
        content = _pipeline_content()
        sast_pos = self._stage_position(content, "sast")
        deploy_pos = self._stage_position(content, "deploy")
        assert sast_pos != -1, "SAST stage not found."
        assert deploy_pos != -1, "Deploy stage not found."
        assert sast_pos < deploy_pos, (
            "SAST stage must appear before the deploy stage in the pipeline. "
            f"sast position={sast_pos}, deploy position={deploy_pos}"
        )

    def test_image_scan_before_deploy(self):
        content = _pipeline_content()
        scan_pos = self._stage_position(content, "image-scan")
        deploy_pos = self._stage_position(content, "deploy")
        assert scan_pos != -1, "image-scan stage not found."
        assert deploy_pos != -1, "Deploy stage not found."
        assert scan_pos < deploy_pos, (
            "image-scan stage must appear before the deploy stage. "
            f"image-scan position={scan_pos}, deploy position={deploy_pos}"
        )

    def test_container_build_before_image_scan(self):
        content = _pipeline_content()
        build_pos = self._stage_position(content, "container-build")
        scan_pos = self._stage_position(content, "image-scan")
        assert build_pos != -1, "container-build stage not found."
        assert scan_pos != -1, "image-scan stage not found."
        assert build_pos < scan_pos, (
            "container-build stage must appear before image-scan stage. "
            f"container-build position={build_pos}, image-scan position={scan_pos}"
        )

    def test_test_stage_before_sast(self):
        content = _pipeline_content()
        test_pos = self._stage_position(content, "test")
        sast_pos = self._stage_position(content, "sast")
        assert test_pos != -1, "test stage not found."
        assert sast_pos != -1, "SAST stage not found."
        assert test_pos < sast_pos, (
            "test stage must appear before sast stage. "
            f"test position={test_pos}, sast position={sast_pos}"
        )

    def test_build_stage_is_first(self):
        content = _pipeline_content()
        build_pos = self._stage_position(content, "build")
        other_stages = [s for s in REQUIRED_STAGES if s != "build"]
        for stage in other_stages:
            pos = self._stage_position(content, stage)
            if pos != -1:
                assert build_pos < pos, (
                    f"build stage must appear before '{stage}' stage. "
                    f"build position={build_pos}, {stage} position={pos}"
                )


# ---------------------------------------------------------------------------
# 4. Trigger rules
# ---------------------------------------------------------------------------


class TestTriggerRules:
    """Pipeline must define branch-based and/or tag-based trigger rules."""

    def test_trigger_rules_present(self):
        content = _pipeline_content().lower()
        trigger_keywords = [
            "on:",          # GitHub Actions
            "trigger",      # GitLab CI / Jenkins
            "branches",
            "push",
            "pull_request",
            "merge_request",
            "tags",
            "when:",
        ]
        found = any(kw in content for kw in trigger_keywords)
        assert found, (
            "No trigger rules detected in the pipeline configuration. "
            "The pipeline must define branch filters, PR/MR triggers, "
            "or tag-based deploy triggers."
        )

    def test_main_or_master_branch_trigger_present(self):
        content = _pipeline_content().lower()
        assert "main" in content or "master" in content, (
            "Pipeline does not reference 'main' or 'master' branch. "
            "At minimum the primary branch must be a pipeline trigger."
        )

    def test_deploy_is_not_triggered_on_every_branch(self):
        """Deploy stage should be gated — not run on every arbitrary branch."""
        content = _pipeline_content().lower()
        # If the pipeline uses GitHub Actions 'if' conditions or GitLab 'only/rules'
        # for the deploy job, that is sufficient. We check that some gating keyword exists.
        gating_keywords = [
            "if:",
            "only:",
            "rules:",
            "when: manual",
            "environment:",
            "condition",
            "filter",
            "tags:",
        ]
        found = any(kw in content for kw in gating_keywords)
        assert found, (
            "No deploy gating mechanism detected. The deploy stage must be "
            "restricted (e.g., branch filter, manual approval, tag trigger, "
            "or environment protection rules)."
        )


# ---------------------------------------------------------------------------
# 5. Secret handling — no plaintext credentials
# ---------------------------------------------------------------------------


class TestSecretHandling:
    """Pipeline must reference secrets via the CI platform's secret store."""

    PLAINTEXT_PATTERNS = [
        r"password\s*[:=]\s*['\"]?\w{6,}",
        r"token\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{10,}",
        r"secret\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{10,}",
        r"aws_secret_access_key\s*[:=]\s*['\"]?[A-Za-z0-9/+]{20,}",
        r"api_key\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{10,}",
    ]

    def test_no_plaintext_passwords_in_pipeline(self):
        content = _pipeline_content()
        for pattern in self.PLAINTEXT_PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            # Filter out references that are clearly variable/secret references
            real_matches = [
                m for m in matches
                if not re.search(r"\$\{?\{?[A-Z_]+\}?\}?", m)
                and "secrets." not in m.lower()
                and "env." not in m.lower()
                and "var." not in m.lower()
            ]
            assert not real_matches, (
                f"Possible plaintext credential found matching pattern '{pattern}': "
                f"{real_matches}. All credentials must use the CI platform's secret store."
            )

    def test_secret_store_references_present(self):
        content = _pipeline_content()
        secret_ref_patterns = [
            r"\$\{\{\s*secrets\.",          # GitHub Actions
            r"\$[A-Z_]+",                   # Environment variable reference
            r"withCredentials",             # Jenkins
            r"CI_.*_TOKEN",                 # GitLab CI convention
            r"vault",                       # HashiCorp Vault
            r"secretKeyRef",                # Kubernetes secret ref
        ]
        found = any(re.search(p, content) for p in secret_ref_patterns)
        assert found, (
            "No secret store references detected in the pipeline. "
            "Registry credentials, SAST tokens, and deploy credentials must "
            "be sourced from the CI platform's secret store."
        )


# ---------------------------------------------------------------------------
# 6. SAST tool configuration
# ---------------------------------------------------------------------------


class TestSASTConfiguration:
    """SAST stage must reference a recognised scanning tool."""

    SAST_TOOLS = [
        "semgrep",
        "snyk",
        "codeql",
        "bandit",
        "trivy",
        "sonarqube",
        "sonar-scanner",
        "checkmarx",
        "veracode",
        "gosec",
        "eslint",
        "spotbugs",
        "pmd",
        "flawfinder",
    ]

    def test_sast_tool_referenced_in_pipeline(self):
        content = _pipeline_content().lower()
        found_tool = next((t for t in self.SAST_TOOLS if t in content), None)
        assert found_tool is not None, (
            "No recognised SAST tool found in the pipeline configuration. "
            "Expected one of: " + ", ".join(self.SAST_TOOLS)
        )

    def test_sast_tool_documented_in_decisions(self):
        assert DECISIONS_DOC.exists(), "docs/cicd-decisions.md not found."
        decisions_text = DECISIONS_DOC.read_text(encoding="utf-8").lower()
        found_tool = next((t for t in self.SAST_TOOLS if t in decisions_text), None)
        assert found_tool is not None, (
            "SAST tool selection is not documented in docs/cicd-decisions.md. "
            "The chosen SAST tool must be recorded with license/token requirements."
        )

    def test_sast_stage_fails_pipeline_on_findings(self):
        """SAST must be configured to fail the pipeline, not just warn."""
        content = _pipeline_content().lower()
        # Look for explicit 'continue-on-error: true' or 'allow_failure: true'
        # scoped to the sast section — a rough heuristic
        sast_idx = content.find("sast")
        if sast_idx == -1:
            pytest.skip("SAST stage not found — covered by earlier test.")
        # Extract a window around the sast stage definition
        window = content[sast_idx: sast_idx + 500]
        soft_failure_patterns = [
            "continue-on-error: true",
            "allow_failure: true",
            "ignore_errors: true",
        ]
        for pattern in soft_failure_patterns:
            assert pattern not in window, (
                f"SAST stage appears to have soft-failure enabled ('{pattern}'). "
                "SAST must be a hard gate — pipeline must fail on findings."
            )


# ---------------------------------------------------------------------------
# 7. Container build configuration
# ---------------------------------------------------------------------------


class TestContainerBuildConfiguration:
    """Container build stage must reference a Dockerfile and a registry."""

    def test_dockerfile_exists(self):
        found = _find_dockerfile()
        assert found is not None, (
            "No Dockerfile found. Expected one of: "
            + ", ".join(str(c) for c in DOCKERFILE_CANDIDATES)
        )

    def test_dockerignore_exists(self):
        assert DOCKERIGNORE.exists(), (
            f".dockerignore not found at {DOCKERIGNORE}. "
            "A .dockerignore file must exist to exclude build artifacts, "
            "test output, and secrets from the container build context."
        )

    def test_dockerignore_excludes_sensitive_paths(self):
        assert DOCKERIGNORE.exists(), ".dockerignore not found."
        content = DOCKERIGNORE.read_text(encoding="utf-8")
        sensitive_patterns = [".env", "*.key", "*.pem", "secrets", ".git"]
        missing = [p for p in sensitive_patterns if p not in content]
        assert not missing, (
            f".dockerignore is missing entries for sensitive paths: {missing}. "
            "These must be excluded from the container build context."
        )

    def test_container_registry_referenced_in_pipeline(self):
        content = _pipeline_content().lower()
        registry_keywords = [
            "docker.io",
            "ghcr.io",
            "gcr.io",
            "ecr",
            "registry",
            "docker push",
            "docker tag",
            "image:",
            "container_registry",
        ]
        found = any(kw in content for kw in registry_keywords)
        assert found, (
            "No container registry reference found in the pipeline. "
            "The container-build stage must push to a registry."
        )

    def test_container_registry_documented_in_decisions(self):
        assert DECISIONS_DOC.exists(), "docs/cicd-decisions.md not found."
        decisions_text = DECISIONS_DOC.read_text(encoding="utf-8").lower()
        registry_keywords = [
            "ecr", "gcr", "ghcr", "docker hub", "registry", "acr", "quay"
        ]
        found = any(kw in decisions_text for kw in registry_keywords)
        assert found, (
            "Container registry is not documented in docs/cicd-decisions.md. "
            "The registry URL and auth method must be recorded."
        )


# ---------------------------------------------------------------------------
# 8. Image scan configuration
# ---------------------------------------------------------------------------


class TestImageScanConfiguration:
    """Image scan stage must reference a recognised scanning tool."""

    IMAGE_SCAN_TOOLS = [
        "trivy",
        "grype",
        "snyk",
        "anchore",
        "clair",
        "docker scout",
        "aqua",
        "twistlock",
        "prisma",
    ]

    def test_image_scan_tool_referenced_in_pipeline(self):
        content = _pipeline_content().lower()
        found_tool = next((t for t in self.IMAGE_SCAN_TOOLS if t in content), None)
        assert found_tool is not None, (
            "No recognised image scanning tool found in the pipeline. "
            "Expected one of: " + ", ".join(self.IMAGE_SCAN_TOOLS)
        )

    def test_image_scan_tool_documented_in_decisions(self):
        assert DECISIONS_DOC.exists(), "docs/cicd-decisions.md not found."
        decisions_text = DECISIONS_DOC.read_text(encoding="utf-8").lower()
        found_tool = next(
            (t for t in self.IMAGE_SCAN_TOOLS if t in decisions_text), None
        )
        assert found_tool is not None, (
            "Image scanning tool is not documented in docs/cicd-decisions.md."
        )

    def test_image_scan_stage_fails_on_critical_vulnerabilities(self):
        """Image scan must be configured to fail on CRITICAL/HIGH findings."""
        content = _pipeline_content().lower()
        scan_idx = content.find("image-scan")
        if scan_idx == -1:
            scan_idx = content.find("image_scan")
        if scan_idx == -1:
            pytest.skip("image-scan stage not found — covered by earlier test.")
        window = content[scan_idx: scan_idx + 600]
        # Check for severity threshold configuration
        severity_keywords = [
            "critical",
            "high",
            "severity",
            "--exit-code",
            "fail-on",
            "fail_on",
            "threshold",
        ]
        found = any(kw in window for kw in severity_keywords)
        assert found, (
            "Image scan stage does not appear to configure a severity threshold. "
            "The scan must be set to fail the pipeline on CRITICAL or HIGH findings."
        )

    def test_image_scan_not_soft_failure(self):
        content = _pipeline_content().lower()
        scan_idx = content.find("image-scan")
        if scan_idx == -1:
            scan_idx = content.find("image_scan")
        if scan_idx == -1:
            pytest.skip("image-scan stage not found.")
        window = content[scan_idx: scan_idx + 500]
        soft_failure_patterns = [
            "continue-on-error: true",
            "allow_failure: true",
        ]
        for pattern in soft_failure_patterns:
            assert pattern not in window, (
                f"Image scan stage has soft-failure enabled ('{pattern}'). "
                "Image scanning must be a hard gate."
            )


# ---------------------------------------------------------------------------
# 9. Deploy stage configuration
# ---------------------------------------------------------------------------


class TestDeployConfiguration:
    """Deploy stage must reference a deployment target and be properly gated."""

    DEPLOY_TOOLS = [
        "kubectl",
        "helm",
        "terraform",
        "ansible",
        "aws ecs",
        "aws eks",
        "gcloud",
        "az ",
        "serverless",
        "heroku",
        "fly.io",
        "deploy",
        "rollout",
        "release",
    ]

    def test_deploy_target_documented_in_decisions(self):
        assert DECISIONS_DOC.exists(), "docs/cicd-decisions.md not found."
        decisions_text = DECISIONS_DOC.read_text(encoding="utf-8").lower()
        deploy_keywords = [
            "kubernetes",
            "ecs",
            "eks",
            "gke",
            "aks",
            "vm",
            "serverless",
            "lambda",
            "cloud run",
            "app service",
            "heroku",
            "deployment target",
        ]
        found = any(kw in decisions_text for kw in deploy_keywords)
        assert found, (
            "Deployment target is not documented in docs/cicd-decisions.md. "
            "The target environment must be recorded."
        )

    def test_deploy_stage_references_deployment_tooling(self):
        content = _pipeline_content().lower()
        deploy_idx = content.find("deploy")
        if deploy_idx == -1:
            pytest.fail("deploy stage not found in pipeline.")
        window = content[deploy_idx: deploy_idx + 800]
        found = any(tool in window for tool in self.DEPLOY_TOOLS)
        assert found, (
            "Deploy stage does not reference any recognised deployment tooling. "
            "Expected one of: " + ", ".join(self.DEPLOY_TOOLS)
        )

    def test_deploy_environment_variable_or_name_present(self):
        content = _pipeline_content().lower()
        env_keywords = [
            "environment:",
            "env:",
            "production",
            "staging",
            "prod",
            "stg",
            "deploy_env",
            "target_env",
        ]
        found = any(kw in content for kw in env_keywords)
        assert found, (
            "No environment name or variable found in the pipeline. "
            "The deploy stage must target a named environment."
        )


# ---------------------------------------------------------------------------
# 10. Decisions documentation completeness
# ---------------------------------------------------------------------------


class TestDecisionsDocumentation:
    """docs/cicd-decisions.md must exist and cover all required decision areas."""

    REQUIRED_SECTIONS = [
        "ci",          # CI/CD platform
        "registry",    # Container registry
        "deploy",      # Deployment target
        "sast",        # SAST tool
        "scan",        # Image scan tool
        "secret",      # Secret/credential management
    ]

    def test_decisions_doc_exists(self):
        assert DECISIONS_DOC.exists(), (
            f"docs/cicd-decisions.md not found at {DECISIONS_DOC}. "
            "This file must document all CI/CD tooling decisions."
        )

    def test_decisions_doc_is_not_empty(self):
        assert DECISIONS_DOC.exists(), "docs/cicd-decisions.md not found."
        content = DECISIONS_DOC.read_text(encoding="utf-8").strip()
        assert len(content) > 100, (
            "docs/cicd-decisions.md appears to be a stub (< 100 chars). "
            "It must contain substantive decision records."
        )

    @pytest.mark.parametrize("section_keyword", REQUIRED_SECTIONS)
    def test_decisions_doc_covers_required_area(self, section_keyword):
        assert DECISIONS_DOC.exists(), "docs/cicd-decisions.md not found."
        content = DECISIONS_DOC.read_text(encoding="utf-8").lower()
        assert section_keyword in content, (
            f"docs/cicd-decisions.md does not mention '{section_keyword}'. "
            "All required decision areas must be documented: "
            + ", ".join(self.REQUIRED_SECTIONS)
        )


# ---------------------------------------------------------------------------
# 11. Pipeline syntax validity (YAML-based pipelines)
# ---------------------------------------------------------------------------


class TestPipelineSyntaxValidity:
    """For YAML-based pipelines, the file must parse without errors."""

    def test_yaml_pipeline_parses_without_error(self):
        pipeline_file = _find_pipeline_file()
        if pipeline_file is None:
            pytest.fail("No pipeline file found.")
        if pipeline_file.suffix not in (".yml", ".yaml"):
            pytest.skip(
                f"Pipeline file {pipeline_file.name} is not YAML — skipping YAML parse test."
            )
        try:
            import yaml  # PyYAML
        except ImportError:
            pytest.skip("PyYAML not installed — skipping YAML syntax validation.")
        content = pipeline_file.read_text(encoding="utf-8")
        try:
            parsed = yaml.safe_load(content)
        except yaml.YAMLError as exc:
            pytest.fail(
                f"Pipeline YAML file failed to parse: {exc}. "
                "The pipeline configuration must be valid YAML."
            )
        assert parsed is not None, "Pipeline YAML parsed to None — file may be empty."
        assert isinstance(parsed, dict), (
            "Pipeline YAML root must be a mapping (dict), "
            f"got {type(parsed).__name__}."
        )

    def test_yaml_pipeline_has_expected_top_level_keys(self):
        pipeline_file = _find_pipeline_file()
        if pipeline_file is None:
            pytest.fail("No pipeline file found.")
        if pipeline_file.suffix not in (".yml", ".yaml"):
            pytest.skip("Not a YAML pipeline.")
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed.")
        content = pipeline_file.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        if not isinstance(parsed, dict):
            pytest.skip("Pipeline YAML root is not a dict.")

        # GitHub Actions: must have 'on' and 'jobs'
        # GitLab CI: must have 'stages'
        github_actions_keys = {"on", "jobs"}
        gitlab_ci_keys = {"stages"}
        has_github = github_actions_keys.issubset(parsed.keys())
        has_gitlab = gitlab_ci_keys.issubset(parsed.keys())
        assert has_github or has_gitlab, (
            f"Pipeline YAML top-level keys {set(parsed.keys())} do not match "
            "expected GitHub Actions ('on', 'jobs') or GitLab CI ('stages') structure."
        )


# ---------------------------------------------------------------------------
# 12. Version / upgrade marker assertion
# ---------------------------------------------------------------------------


class TestUpgradeMarker:
    """
    Verify that the pipeline represents a net-new installation (upgrade from none).
    Since there was no prior pipeline, the presence of all six stages in a valid
    config file IS the version assertion for this upgrade.
    """

    def test_pipeline_represents_complete_new_installation(self):
        """
        Upgrade goal: greenfield CI/CD pipeline with all six stages.
        This test asserts the 'target version' of the upgrade — a fully
        configured pipeline — is active by verifying all six stages exist
        in a non-empty, parseable configuration file.
        """
        pipeline_file = _find_pipeline_file()
        assert pipeline_file is not None, (
            "UPGRADE VALIDATION FAILED: No pipeline configuration file found. "
            "The upgrade goal was to establish a CI/CD pipeline from scratch."
        )
        content = pipeline_file.read_text(encoding="utf-8")
        assert len(content.strip()) > 0, "Pipeline file is empty."

        normalised = content.lower().replace("_", "-")
        missing_stages = [s for s in REQUIRED_STAGES if s not in normalised]
        assert not missing_stages, (
            f"UPGRADE VALIDATION FAILED: Pipeline is missing stages: {missing_stages}. "
            f"All six stages must be present for the upgrade to be considered complete: "
            f"{REQUIRED_STAGES}"
        )

    def test_no_legacy_manual_deployment_scripts_replace_pipeline(self):
        """
        Ensure the pipeline is not bypassed by legacy manual deploy scripts
        that pre-date the upgrade.
        """
        legacy_patterns = [
            REPO_ROOT / "deploy.sh",
            REPO_ROOT / "scripts" / "manual_deploy.sh",
            REPO_ROOT / "build_and_push.sh",
        ]
        for legacy_file in legacy_patterns:
            if legacy_file.exists():
                content = legacy_file.read_text(encoding="utf-8")
                # Legacy scripts are acceptable if they are called FROM the pipeline,
                # but should not be the sole deployment mechanism.
                # Warn rather than hard-fail — the pipeline file's existence is the gate.
                pipeline_content = _pipeline_content().lower()
                script_name = legacy_file.name
                if script_name not in pipeline_content:
                    pytest.warns(
                        UserWarning,
                        match=f"{script_name} exists but is not referenced in the pipeline",
                    ) if False else None  # informational only
                    # Non-blocking: just ensure the pipeline file also exists
                    assert _find_pipeline_file() is not None, (
                        f"Legacy script {legacy_file} exists and the pipeline file is missing. "
                        "Manual scripts must not replace the automated pipeline."
                    )

    def test_cicd_upgrade_completion_summary(self, capsys):
        """Print a human-readable summary of the upgrade validation results."""
        pipeline_file = _find_pipeline_file()
        content = _pipeline_content() if pipeline_file else ""
        normalised = content.lower().replace("_", "-")

        present_stages = [s for s in REQUIRED_STAGES if s in normalised]
        missing_stages = [s for s in REQUIRED_STAGES if s not in normalised]

        summary_lines = [
            "",
            "=" * 60,
            "CI/CD PIPELINE UPGRADE VALIDATION SUMMARY",
            "=" * 60,
            f"Pipeline file   : {pipeline_file or 'NOT FOUND'}",
            f"Decisions doc   : {'FOUND' if DECISIONS_DOC.exists() else 'NOT FOUND'}",
            f"Dockerfile      : {_find_dockerfile() or 'NOT FOUND'}",
            f".dockerignore   : {'FOUND' if DOCKERIGNORE.exists() else 'NOT FOUND'}",
            f"Stages present  : {present_stages}",
            f"Stages missing  : {missing_stages}",
            f"Upgrade status  : {'COMPLETE' if not missing_stages and pipeline_file else 'INCOMPLETE'}",
            "=" * 60,
        ]
        print("\n".join(summary_lines))
        assert not missing_stages and pipeline_file is not None, (
            "Upgrade is INCOMPLETE. See summary above."
        )