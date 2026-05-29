# TASKS: Monolith Decomposition Opportunity Evaluation

> **Goal:** Evaluate and document decomposition opportunities from the existing monolith into microservices.
> **Upgrade Option:** Moderate
> **Note:** Technology stack details were not provided in the tech analysis. Tasks below are scoped strictly to discovery, evaluation, and documentation activities. No code migration tasks are included, as no specific components, frameworks, or files were identified.

---

## Prerequisites

- [ ] [XS] Confirm access to the monolith's source repository and ensure read permissions are granted to all evaluators involved in the decomposition analysis
- [ ] [XS] Confirm access to any existing architecture diagrams, API contracts, database schemas, and runbooks relevant to the monolith
- [ ] [XS] Identify and schedule availability of domain experts, team leads, and stakeholders who have working knowledge of the monolith's bounded contexts
- [ ] [XS] Establish a shared documentation workspace (e.g., Confluence space, GitHub Wiki, or equivalent) where all decomposition findings will be recorded

---

## Phase 1 — Preparation

- [ ] [M] Inventory all top-level modules, packages, and logical groupings within the monolith codebase and record findings in a `decomposition/01-module-inventory.md` document
- [ ] [M] Map all inbound and outbound integration points (APIs, message queues, scheduled jobs, shared databases, file I/O) and record in `decomposition/02-integration-map.md`
- [ ] [S] Identify and document all shared libraries, utilities, and cross-cutting concerns (e.g., logging, auth, config) that are consumed across multiple modules in `decomposition/03-shared-concerns.md`
- [ ] [S] Capture the current deployment topology (single deployable unit, database layout, infrastructure dependencies) in `decomposition/04-deployment-topology.md`
- [ ] [S] Document the existing test coverage posture (unit, integration, end-to-end) as a baseline reference in `decomposition/05-test-coverage-baseline.md`

---

## Phase 2 — Core Upgrade

> **Note:** This phase covers the core analytical work — identifying and evaluating decomposition candidates. No code changes are in scope for this task.

- [ ] [L] Conduct domain-driven design (DDD) event-storming or context-mapping sessions with domain experts to identify candidate bounded contexts and record outputs in `decomposition/06-bounded-contexts.md`
- [ ] [M] Analyze inter-module coupling and dependency frequency across identified modules; document high-coupling hotspots and low-coupling natural seams in `decomposition/07-coupling-analysis.md`
- [ ] [M] Evaluate each candidate bounded context against decomposition criteria (team ownership, independent deployability, data isolation feasibility, change frequency) and score in `decomposition/08-candidate-scoring.md`
- [ ] [M] Identify data ownership boundaries and shared-database anti-patterns; document which modules share tables or schemas and the effort required to separate them in `decomposition/09-data-boundary-analysis.md`
- [ ] [S] Assess operational complexity trade-offs (network latency, distributed transactions, observability overhead) for the top-ranked decomposition candidates in `decomposition/10-operational-tradeoffs.md`
- [ ] [M] Produce a prioritized decomposition roadmap listing candidates in recommended extraction order, with rationale, in `decomposition/11-decomposition-roadmap.md`

---

## Phase 3 — Testing & Validation

- [ ] [S] Review the test coverage baseline (`decomposition/05-test-coverage-baseline.md`) against each candidate service boundary to identify gaps that would need to be closed before any future extraction begins; record findings in `decomposition/12-test-gap-analysis.md`
- [ ] [S] Validate the bounded context map (`decomposition/06-bounded-contexts.md`) and candidate scoring (`decomposition/08-candidate-scoring.md`) in a structured review session with domain experts and record sign-off or revision notes

---

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task. No code changes, pipeline modifications, or infrastructure updates are in scope for an evaluation and documentation effort.

---

## Phase 5 — Documentation & Rollout

- [ ] [M] Consolidate all decomposition artifacts into a single executive summary document (`decomposition/00-executive-summary.md`) covering findings, recommended candidates, risks, and proposed next steps
- [ ] [S] Conduct a stakeholder review walkthrough of `decomposition/00-executive-summary.md` and `decomposition/11-decomposition-roadmap.md`; capture feedback and open questions in a tracked issues list
- [ ] [S] Incorporate stakeholder feedback and publish the final decomposition documentation set to the shared workspace, marking the evaluation milestone as complete
- [ ] [XS] Create follow-on GitHub Issues or backlog items for each top-priority decomposition candidate identified in `decomposition/11-decomposition-roadmap.md` to seed the next phase of work

---

> **Scope boundary:** All tasks above are limited to evaluation and documentation. Actual service extraction, refactoring, infrastructure provisioning, and CI/CD changes are out of scope until a follow-on modernization task is initiated with a concrete tech stack analysis.