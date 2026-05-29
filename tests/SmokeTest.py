"""
Upgrade Validation Tests: Monolith Decomposition Opportunity Evaluation

These tests verify that the decomposition evaluation process has been completed
successfully by asserting the existence, structure, and content of all required
documentation artifacts produced during the evaluation.

Run with: python -m pytest tests/test_decomposition_upgrade_validation.py -v
"""

import os
import re
import pytest

DOCS_BASE = os.path.join("docs", "decomposition")

REQUIRED_ARTIFACTS = [
    "module-inventory.md",
    "dependency-map.md",
    "data-model-analysis.md",
    "runtime-coupling.md",
    "external-integrations.md",
    "scoring-rubric.md",
    "candidate-scores.md",
    "bounded-contexts.md",
    "interface-contracts.md",
    "decomposition-recommendations.md",
    "migration-risks.md",
    "adr",
]

MINIMUM_CANDIDATE_COUNT = 1
MINIMUM_BOUNDED_CONTEXT_COUNT = 1
MINIMUM_ADR_COUNT = 1

REQUIRED_SCORING_RUBRIC_CRITERIA = [
    "autonomy",
    "change frequency",
    "team ownership",
    "data isolation",
]

REQUIRED_RECOMMENDATION_SECTIONS = [
    "candidate",
    "rationale",
    "interface",
    "risk",
]

REQUIRED_INTERFACE_CONTRACT_FIELDS = [
    "endpoint",
    "contract",
    "schema",
]

REQUIRED_ADR_SECTIONS = [
    "status",
    "context",
    "decision",
    "consequences",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def artifact_path(*parts):
    return os.path.join(DOCS_BASE, *parts)


def read_artifact(*parts):
    path = artifact_path(*parts)
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def count_markdown_headings(content, level=2):
    """Return the number of headings at the given ATX heading level."""
    pattern = r"^#{" + str(level) + r"}\s+\S"
    return len(re.findall(pattern, content, re.MULTILINE))


def list_files_in(directory, extension=".md"):
    if not os.path.isdir(directory):
        return []
    return [
        f for f in os.listdir(directory)
        if f.endswith(extension)
    ]


# ---------------------------------------------------------------------------
# Phase 0 — Artifact existence (upgrade completion gate)
# ---------------------------------------------------------------------------

class TestArtifactExistence:
    """All required documentation artifacts must exist on disk."""

    @pytest.mark.parametrize("artifact", [
        "module-inventory.md",
        "dependency-map.md",
        "data-model-analysis.md",
        "runtime-coupling.md",
        "external-integrations.md",
        "scoring-rubric.md",
        "candidate-scores.md",
        "bounded-contexts.md",
        "interface-contracts.md",
        "decomposition-recommendations.md",
        "migration-risks.md",
    ])
    def test_required_markdown_artifact_exists(self, artifact):
        path = artifact_path(artifact)
        assert os.path.isfile(path), (
            f"Required decomposition artifact is missing: {path}\n"
            f"This file must be produced as part of the evaluation upgrade."
        )

    def test_adr_directory_exists(self):
        path = artifact_path("adr")
        assert os.path.isdir(path), (
            f"ADR directory is missing: {path}\n"
            "At least one Architecture Decision Record must be produced."
        )

    def test_at_least_one_adr_file_exists(self):
        adr_dir = artifact_path("adr")
        adrs = list_files_in(adr_dir, extension=".md")
        assert len(adrs) >= MINIMUM_ADR_COUNT, (
            f"Expected at least {MINIMUM_ADR_COUNT} ADR file(s) in {adr_dir}, "
            f"found {len(adrs)}."
        )

    def test_artifacts_are_non_empty(self):
        for artifact in [
            "module-inventory.md",
            "dependency-map.md",
            "scoring-rubric.md",
            "candidate-scores.md",
            "decomposition-recommendations.md",
        ]:
            path = artifact_path(artifact)
            if not os.path.isfile(path):
                pytest.skip(f"{path} does not exist — covered by existence test")
            size = os.path.getsize(path)
            assert size > 0, f"Artifact is empty (0 bytes): {path}"


# ---------------------------------------------------------------------------
# Phase 1 — Module inventory structure
# ---------------------------------------------------------------------------

class TestModuleInventory:
    """module-inventory.md must enumerate at least one module."""

    def test_module_inventory_has_content(self):
        content = read_artifact("module-inventory.md")
        assert len(content.strip()) > 50, (
            "module-inventory.md appears to contain only placeholder text."
        )

    def test_module_inventory_lists_modules(self):
        content = read_artifact("module-inventory.md")
        # Expect at least one list item or table row describing a module
        has_list_item = bool(re.search(r"^\s*[-*]\s+\S", content, re.MULTILINE))
        has_table_row = bool(re.search(r"^\|.+\|", content, re.MULTILINE))
        has_heading_entry = count_markdown_headings(content, level=3) >= 1
        assert has_list_item or has_table_row or has_heading_entry, (
            "module-inventory.md does not appear to list any modules. "
            "Expected at least one list item, table row, or level-3 heading."
        )

    def test_module_inventory_no_todo_placeholders_in_module_names(self):
        content = read_artifact("module-inventory.md")
        # The document may contain TODO notes but module names themselves
        # should not be entirely TODO
        todo_only_lines = re.findall(
            r"^\s*[-*]\s+TODO\s*$", content, re.MULTILINE | re.IGNORECASE
        )
        assert len(todo_only_lines) == 0, (
            f"module-inventory.md contains {len(todo_only_lines)} unresolved "
            "TODO-only list entries. All modules must be named."
        )


# ---------------------------------------------------------------------------
# Phase 1 — Dependency map
# ---------------------------------------------------------------------------

class TestDependencyMap:
    """dependency-map.md must document inter-module relationships."""

    def test_dependency_map_references_multiple_modules(self):
        content = read_artifact("dependency-map.md")
        # Expect arrows, table rows, or list items indicating relationships
        relationship_indicators = re.findall(
            r"(->|→|depends on|calls|imports|uses)", content, re.IGNORECASE
        )
        assert len(relationship_indicators) >= 1, (
            "dependency-map.md does not appear to document any inter-module "
            "dependencies. Expected at least one relationship indicator "
            "(e.g., '->', '→', 'depends on', 'calls', 'imports')."
        )

    def test_dependency_map_has_meaningful_length(self):
        content = read_artifact("dependency-map.md")
        word_count = len(content.split())
        assert word_count >= 30, (
            f"dependency-map.md has only {word_count} words. "
            "Expected a substantive dependency analysis."
        )


# ---------------------------------------------------------------------------
# Phase 1 — Scoring rubric
# ---------------------------------------------------------------------------

class TestScoringRubric:
    """scoring-rubric.md must define the agreed evaluation criteria."""

    @pytest.mark.parametrize("criterion", REQUIRED_SCORING_RUBRIC_CRITERIA)
    def test_scoring_rubric_contains_criterion(self, criterion):
        content = read_artifact("scoring-rubric.md")
        assert criterion.lower() in content.lower(), (
            f"scoring-rubric.md does not mention the required criterion: "
            f"'{criterion}'. All four baseline criteria must be documented."
        )

    def test_scoring_rubric_defines_scale(self):
        content = read_artifact("scoring-rubric.md")
        # Expect some numeric scale definition (e.g., 1-5, 0-3, High/Med/Low)
        has_numeric_scale = bool(re.search(r"\b[1-9]\s*[-–]\s*[1-9]\b", content))
        has_qualitative_scale = bool(
            re.search(r"\b(high|medium|low)\b", content, re.IGNORECASE)
        )
        assert has_numeric_scale or has_qualitative_scale, (
            "scoring-rubric.md does not appear to define a scoring scale. "
            "Expected a numeric range (e.g., 1-5) or qualitative levels "
            "(High/Medium/Low)."
        )


# ---------------------------------------------------------------------------
# Phase 2 — Candidate scores
# ---------------------------------------------------------------------------

class TestCandidateScores:
    """candidate-scores.md must record scored decomposition candidates."""

    def test_candidate_scores_has_minimum_candidates(self):
        content = read_artifact("candidate-scores.md")
        # Count table rows (excluding header/separator) or list items
        table_data_rows = re.findall(
            r"^\|(?!\s*[-:]+\s*\|).+\|", content, re.MULTILINE
        )
        list_items = re.findall(r"^\s*[-*]\s+\S", content, re.MULTILINE)
        h3_entries = count_markdown_headings(content, level=3)
        total = max(len(table_data_rows), len(list_items), h3_entries)
        assert total >= MINIMUM_CANDIDATE_COUNT, (
            f"candidate-scores.md must document at least "
            f"{MINIMUM_CANDIDATE_COUNT} scored candidate(s). Found {total}."
        )

    def test_candidate_scores_references_rubric_criteria(self):
        content = read_artifact("candidate-scores.md")
        matched = [
            c for c in REQUIRED_SCORING_RUBRIC_CRITERIA
            if c.lower() in content.lower()
        ]
        assert len(matched) >= 2, (
            "candidate-scores.md should reference at least 2 of the rubric "
            f"criteria. Found: {matched}. "
            f"Expected criteria: {REQUIRED_SCORING_RUBRIC_CRITERIA}"
        )


# ---------------------------------------------------------------------------
# Phase 2 — Bounded contexts
# ---------------------------------------------------------------------------

class TestBoundedContexts:
    """bounded-contexts.md must identify distinct bounded contexts."""

    def test_bounded_contexts_minimum_count(self):
        content = read_artifact("bounded-contexts.md")
        h2_count = count_markdown_headings(content, level=2)
        h3_count = count_markdown_headings(content, level=3)
        list_items = len(re.findall(r"^\s*[-*]\s+\S", content, re.MULTILINE))
        total = max(h2_count, h3_count, list_items)
        assert total >= MINIMUM_BOUNDED_CONTEXT_COUNT, (
            f"bounded-contexts.md must identify at least "
            f"{MINIMUM_BOUNDED_CONTEXT_COUNT} bounded context(s). "
            f"Found approximately {total} entries."
        )

    def test_bounded_contexts_describes_ownership_or_responsibility(self):
        content = read_artifact("bounded-contexts.md")
        ownership_terms = re.findall(
            r"\b(owner|team|responsible|domain|context|boundary)\b",
            content, re.IGNORECASE
        )
        assert len(ownership_terms) >= 2, (
            "bounded-contexts.md does not appear to describe ownership or "
            "domain responsibility. Expected terms like 'owner', 'team', "
            "'domain', 'boundary', or 'context'."
        )


# ---------------------------------------------------------------------------
# Phase 2 — Interface contracts
# ---------------------------------------------------------------------------

class TestInterfaceContracts:
    """interface-contracts.md must define service boundary contracts."""

    def test_interface_contracts_has_content(self):
        content = read_artifact("interface-contracts.md")
        assert len(content.strip()) > 100, (
            "interface-contracts.md appears to be a stub. "
            "Expected substantive interface contract definitions."
        )

    @pytest.mark.parametrize("field", REQUIRED_INTERFACE_CONTRACT_FIELDS)
    def test_interface_contracts_mentions_field(self, field):
        content = read_artifact("interface-contracts.md")
        assert field.lower() in content.lower(), (
            f"interface-contracts.md does not mention '{field}'. "
            "Interface contracts must address endpoints, contracts, and schemas."
        )

    def test_interface_contracts_references_at_least_one_service(self):
        content = read_artifact("interface-contracts.md")
        # Expect at least one service/API name defined as a heading or bold term
        service_definitions = re.findall(
            r"(#{2,4}\s+\S|^\*\*[^*]+\*\*)", content, re.MULTILINE
        )
        assert len(service_definitions) >= 1, (
            "interface-contracts.md does not appear to define any named "
            "service contracts. Expected at least one named service section."
        )


# ---------------------------------------------------------------------------
# Phase 2 — Decomposition recommendations
# ---------------------------------------------------------------------------

class TestDecompositionRecommendations:
    """decomposition-recommendations.md is the primary upgrade output artifact."""

    @pytest.mark.parametrize("section_keyword", REQUIRED_RECOMMENDATION_SECTIONS)
    def test_recommendations_contains_required_section(self, section_keyword):
        content = read_artifact("decomposition-recommendations.md")
        assert section_keyword.lower() in content.lower(), (
            f"decomposition-recommendations.md does not contain a section or "
            f"discussion of '{section_keyword}'. All four areas (candidate, "
            "rationale, interface, risk) must be addressed."
        )

    def test_recommendations_references_at_least_one_named_candidate(self):
        content = read_artifact("decomposition-recommendations.md")
        # Must reference at least one named service or module candidate
        named_candidates = re.findall(
            r"#{2,4}\s+(.+)", content, re.MULTILINE
        )
        assert len(named_candidates) >= MINIMUM_CANDIDATE_COUNT, (
            "decomposition-recommendations.md must name at least one "
            f"decomposition candidate as a heading. Found: {named_candidates}"
        )

    def test_recommendations_does_not_contain_unresolved_spec_todos(self):
        content = read_artifact("decomposition-recommendations.md")
        # The spec itself had TODO markers — the final recommendations must not
        unresolved = re.findall(
            r"\bTODO\b(?!\s*—\s*confirm)", content
        )
        assert len(unresolved) == 0, (
            f"decomposition-recommendations.md contains {len(unresolved)} "
            "unresolved TODO marker(s). All items must be resolved before "
            "the evaluation is considered complete."
        )

    def test_recommendations_has_substantive_length(self):
        content = read_artifact("decomposition-recommendations.md")
        word_count = len(content.split())
        assert word_count >= 200, (
            f"decomposition-recommendations.md has only {word_count} words. "
            "Expected a substantive recommendations document (>=200 words)."
        )


# ---------------------------------------------------------------------------
# Phase 2 — Migration risks
# ---------------------------------------------------------------------------

class TestMigrationRisks:
    """migration-risks.md must document identified risks and mitigations."""

    def test_migration_risks_identifies_risks(self):
        content = read_artifact("migration-risks.md")
        risk_indicators = re.findall(
            r"\b(risk|failure|rollback|data loss|downtime|regression|"
            r"compatibility|breaking change)\b",
            content, re.IGNORECASE
        )
        assert len(risk_indicators) >= 3, (
            "migration-risks.md does not appear to identify meaningful risks. "
            f"Found only {len(risk_indicators)} risk-related term(s). "
            "Expected at least 3."
        )

    def test_migration_risks_includes_mitigation_strategies(self):
        content = read_artifact("migration-risks.md")
        mitigation_indicators = re.findall(
            r"\b(mitigat|remediat|fallback|rollback|monitor|alert|"
            r"test|validate|canary|feature flag)\b",
            content, re.IGNORECASE
        )
        assert len(mitigation_indicators) >= 2, (
            "migration-risks.md does not appear to include mitigation "
            f"strategies. Found only {len(mitigation_indicators)} "
            "mitigation-related term(s). Expected at least 2."
        )


# ---------------------------------------------------------------------------
# Phase 3 — Architecture Decision Records
# ---------------------------------------------------------------------------

class TestArchitectureDecisionRecords:
    """ADR files must follow standard ADR structure."""

    def _get_adr_files(self):
        adr_dir = artifact_path("adr")
        if not os.path.isdir(adr_dir):
            return []
        return [
            os.path.join(adr_dir, f)
            for f in list_files_in(adr_dir, extension=".md")
        ]

    def test_adrs_exist(self):
        adrs = self._get_adr_files()
        assert len(adrs) >= MINIMUM_ADR_COUNT, (
            f"Expected at least {MINIMUM_ADR_COUNT} ADR file(s). "
            f"Found {len(adrs)}."
        )

    @pytest.mark.parametrize("section", REQUIRED_ADR_SECTIONS)
    def test_first_adr_contains_required_section(self, section):
        adrs = self._get_adr_files()
        if not adrs:
            pytest.skip("No ADR files found — covered by existence test")
        first_adr = sorted(adrs)[0]
        with open(first_adr, "r", encoding="utf-8") as fh:
            content = fh.read()
        assert section.lower() in content.lower(), (
            f"ADR file '{os.path.basename(first_adr)}' is missing the "
            f"required section: '{section}'. "
            "ADRs must contain: Status, Context, Decision, Consequences."
        )

    def test_adrs_have_accepted_or_proposed_status(self):
        adrs = self._get_adr_files()
        if not adrs:
            pytest.skip("No ADR files found — covered by existence test")
        for adr_path in adrs:
            with open(adr_path, "r", encoding="utf-8") as fh:
                content = fh.read()
            has_status = bool(
                re.search(
                    r"\b(accepted|proposed|superseded|deprecated|rejected)\b",
                    content, re.IGNORECASE
                )
            )
            assert has_status, (
                f"ADR '{os.path.basename(adr_path)}' does not declare a "
                "valid status. Expected one of: Accepted, Proposed, "
                "Superseded, Deprecated, Rejected."
            )


# ---------------------------------------------------------------------------
# Cross-artifact consistency checks
# ---------------------------------------------------------------------------

class TestCrossArtifactConsistency:
    """Verify that key artifacts reference each other consistently."""

    def test_recommendations_reference_bounded_contexts(self):
        recommendations = read_artifact("decomposition-recommendations.md")
        bounded_contexts = read_artifact("bounded-contexts.md")

        # Extract context names from bounded-contexts.md (level-2/3 headings)
        context_names = re.findall(
            r"^#{2,3}\s+(.+)", bounded_contexts, re.MULTILINE
        )
        if not context_names:
            pytest.skip(
                "No named bounded contexts found in bounded-contexts.md — "
                "cannot perform cross-reference check."
            )

        matched = [
            name.strip() for name in context_names
            if name.strip().lower() in recommendations.lower()
        ]
        assert len(matched) >= 1, (
            "decomposition-recommendations.md does not reference any of the "
            f"bounded contexts defined in bounded-contexts.md. "
            f"Contexts defined: {context_names}. "
            "Recommendations must be grounded in the identified contexts."
        )

    def test_candidate_scores_reference_module_inventory(self):
        scores = read_artifact("candidate-scores.md")
        inventory = read_artifact("module-inventory.md")

        # Extract module names from inventory (list items or headings)
        module_names = re.findall(
            r"^#{2,3}\s+(.+)|^\s*[-*]\s+([^\n:]+)", inventory, re.MULTILINE
        )
        flat_names = [
            (g1 or g2).strip()
            for g1, g2 in module_names
            if (g1 or g2).strip() and len((g1 or g2).strip()) > 3
        ]
        if not flat_names:
            pytest.skip(
                "No module names extracted from module-inventory.md — "
                "cannot perform cross-reference check."
            )

        matched = [
            name for name in flat_names
            if name.lower() in scores.lower()
        ]
        assert len(matched) >= 1, (
            "candidate-scores.md does not appear to reference any modules "
            "from module-inventory.md. Scores must be tied to inventoried "
            f"modules. Modules found in inventory: {flat_names[:10]}"
        )

    def test_interface_contracts_reference_recommendations(self):
        contracts = read_artifact("interface-contracts.md")
        recommendations = read_artifact("decomposition-recommendations.md")

        # Extract candidate names from recommendations
        candidate_names = re.findall(
            r"^#{2,3}\s+(.+)", recommendations, re.MULTILINE
        )
        if not candidate_names:
            pytest.skip(
                "No candidate names found in decomposition-recommendations.md"
            )

        matched = [
            name.strip() for name in candidate_names
            if name.strip().lower() in contracts.lower()
        ]
        assert len(matched) >= 1, (
            "interface-contracts.md does not reference any of the candidates "
            "named in decomposition-recommendations.md. Interface contracts "
            "must correspond to recommended decomposition candidates. "
            f"Candidates: {candidate_names}"
        )


# ---------------------------------------------------------------------------
# Upgrade completion gate — single summary assertion
# ---------------------------------------------------------------------------

class TestUpgradeCompletionGate:
    """
    Final gate: all required artifacts must exist and be non-empty.
    This is the canonical 'upgrade succeeded' check.
    """

    def test_all_required_artifacts_present_and_non_empty(self):
        missing = []
        empty = []

        for artifact in [
            "module-inventory.md",
            "dependency-map.md",
            "data-model-analysis.md",
            "runtime-coupling.md",
            "external-integrations.md",
            "scoring-rubric.md",
            "candidate-scores.md",
            "bounded-contexts.md",
            "interface-contracts.md",
            "decomposition-recommendations.md",
            "migration-risks.md",
        ]:
            path = artifact_path(artifact)
            if not os.path.isfile(path):
                missing.append(artifact)
            elif os.path.getsize(path) == 0:
                empty.append(artifact)

        adr_dir = artifact_path("adr")
        if not os.path.isdir(adr_dir) or len(list_files_in(adr_dir)) == 0:
            missing.append("adr/<at-least-one>.md")

        errors = []
        if missing:
            errors.append(f"Missing artifacts: {missing}")
        if empty:
            errors.append(f"Empty artifacts: {empty}")

        assert not errors, (
            "Monolith decomposition evaluation upgrade is INCOMPLETE.\n"
            + "\n".join(errors)
        )

    def test_decomposition_evaluation_version_marker_present(self):
        """
        The recommendations document must contain a version/date marker
        indicating when the evaluation was completed, serving as the
        'target version active' assertion for this documentation upgrade.
        """
        content = read_artifact("decomposition-recommendations.md")
        has_date = bool(
            re.search(
                r"\b(20\d{2}[-/]\d{2}[-/]\d{2}|"
                r"January|February|March|April|May|June|"
                r"July|August|September|October|November|December)\b",
                content
            )
        )
        has_version_marker = bool(
            re.search(r"\bv\d+\.\d+|\bversion\s+\d+|\brevision\s+\d+",
                      content, re.IGNORECASE)
        )
        assert has_date or has_version_marker, (
            "decomposition-recommendations.md does not contain a completion "
            "date or version marker. The evaluation document must be dated "
            "or versioned to confirm the upgrade was completed at a known "
            "point in time (e.g., '2024-06-15' or 'Version 1.0')."
        )