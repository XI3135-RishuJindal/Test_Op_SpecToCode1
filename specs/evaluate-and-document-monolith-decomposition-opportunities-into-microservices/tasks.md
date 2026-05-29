# TASKS: Monolith Decomposition Opportunity Evaluation

> **Goal:** Evaluate and document decomposition opportunities from the existing monolith into microservices.
> **Upgrade Option:** Moderate decomposition approach.
> **Note:** Tech stack details were not provided in the analysis. Tasks below are scoped strictly to the evaluation and documentation effort. No code migration or infrastructure changes are included.

---

## Prerequisites

- [ ] [XS] Confirm access to the monolith source repository and any existing architecture diagrams with the team lead
- [ ] [XS] Confirm access to production monitoring, logging, or APM tooling (e.g., dashboards, trace data) to support runtime analysis
- [ ] [XS] Identify and schedule availability of domain experts and service owners for interviews or workshops
- [ ] [XS] Set up a shared documentation space (e.g., Confluence space, GitHub Wiki, or `/docs/decomposition/` directory in the repo) for all evaluation artifacts

---

## Phase 1 — Preparation

- [ ] [S] Inventory all top-level modules, packages, and bounded namespaces in the monolith codebase and record findings in `docs/decomposition/module-inventory.md`
- [ ] [M] Map inter-module dependencies (imports, shared libraries, shared database tables, direct method calls) and produce a dependency graph artifact in `docs/decomposition/dependency-map.md`
- [ ] [S] Collect runtime traffic and usage data (request volumes, latency hotspots, error rates per functional area) from available monitoring tooling and record in `docs/decomposition/runtime-profile.md`
- [ ] [S] Document the current data model, identifying tables or schemas that are shared across multiple functional domains in `docs/decomposition/data-model-analysis.md`
- [ ] [XS] Define evaluation criteria (e.g., team ownership boundaries, change frequency, scalability needs, fault isolation value, data ownership clarity) in `docs/decomposition/evaluation-criteria.md`

---

## Phase 2 — Core Upgrade

> *This phase covers the core analytical work: identifying, assessing, and prioritizing decomposition candidates.*

- [ ] [M] Conduct domain-driven design (DDD) event-storming or context-mapping exercise with domain experts and record bounded context candidates in `docs/decomposition/bounded-contexts.md`
- [ ] [M] Evaluate each identified bounded context against the criteria defined in `docs/decomposition/evaluation-criteria.md` and score/rank candidates in `docs/decomposition/candidate-assessment.md`
- [ ] [M] Identify and document shared data coupling risks for each candidate, including tables with cross-domain writes, in `docs/decomposition/data-coupling-risks.md`
- [ ] [S] Identify synchronous vs. asynchronous communication patterns between candidate service boundaries and document recommended interaction styles in `docs/decomposition/communication-patterns.md`
- [ ] [S] Document the top 3–5 highest-priority decomposition candidates with rationale, estimated effort, and risk level in `docs/decomposition/priority-candidates.md`
- [ ] [M] Produce a recommended decomposition roadmap with sequencing rationale (e.g., strangler fig pattern, extract by team boundary) in `docs/decomposition/decomposition-roadmap.md`

---

## Phase 3 — Testing & Validation

- [ ] [S] Review the dependency map and bounded context findings with at least two domain experts or senior engineers and capture review feedback in `docs/decomposition/review-feedback.md`
- [ ] [S] Validate the data-coupling risk analysis against the actual database schema (or ORM models) and confirm or revise findings in `docs/decomposition/data-coupling-risks.md`
- [ ] [XS] Cross-check the priority candidates list against team ownership structure to confirm organizational alignment and note any gaps in `docs/decomposition/priority-candidates.md`

---

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task. This effort is an evaluation and documentation exercise; no pipeline, Docker, or infrastructure changes are in scope.

---

## Phase 5 — Documentation & Rollout

- [ ] [M] Compile all evaluation artifacts into a single executive summary document at `docs/decomposition/executive-summary.md`, including: scope, methodology, top candidates, roadmap, and risks
- [ ] [S] Present findings to engineering leadership and stakeholders; capture decisions and open questions in `docs/decomposition/stakeholder-review-notes.md`
- [ ] [XS] Create follow-on GitHub Issues or backlog tickets for each priority decomposition candidate, linking to the relevant sections of `docs/decomposition/priority-candidates.md`
- [ ] [XS] Schedule a 30-day checkpoint to review whether new runtime data or team changes affect the priority ranking documented in `docs/decomposition/decomposition-roadmap.md`

---

> **⚠️ Scope Notice:** Because the tech analysis did not provide language, runtime, build tool, or framework details, all tasks above are scoped exclusively to the evaluation and documentation effort. Once a specific decomposition candidate moves to implementation, a separate TASKS document should be generated with the full tech context of that service boundary.