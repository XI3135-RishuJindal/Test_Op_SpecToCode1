# TASKS: Monolith Decomposition Opportunity Evaluation

> **Goal:** Evaluate and document decomposition opportunities from the existing monolith into microservices.
> **Upgrade Option:** Moderate
> **Note:** Technology stack details were not provided in the tech analysis. Tasks below are scoped strictly to discovery, evaluation, and documentation activities. No code migration tasks are included, as no specific components, frameworks, or files were identified.

---

## Prerequisites

- [ ] [XS] Confirm access to the monolith's source repository and ensure read permissions are granted to all evaluators
- [ ] [XS] Confirm access to any existing architecture diagrams, API contracts, or domain documentation in the project wiki or shared drive
- [ ] [XS] Identify and schedule availability of domain experts, product owners, and current maintainers for interview sessions
- [ ] [XS] Establish a shared documentation workspace (e.g., Confluence space, GitHub Wiki, or shared folder) where evaluation outputs will be stored

---

## Phase 1 — Preparation

- [ ] [M] Inventory all top-level modules, packages, and logical groupings in the monolith codebase and record findings in `decomposition/01-module-inventory.md`
- [ ] [M] Map all inbound and outbound integrations (APIs, message queues, databases, third-party services) and document in `decomposition/02-integration-map.md`
- [ ] [S] Identify and document all shared libraries, utilities, and cross-cutting concerns (logging, auth, config) in `decomposition/03-shared-concerns.md`
- [ ] [S] Collect and document existing non-functional requirements (SLAs, latency targets, throughput, availability) in `decomposition/04-nfr-baseline.md`
- [ ] [S] Document the current deployment model (single deployable unit, deployment frequency, rollback process) in `decomposition/05-deployment-baseline.md`

---

## Phase 2 — Core Upgrade

> **Note:** No specific frameworks, runtime, or build tool were identified in the tech analysis. The "core" work for this task is the decomposition analysis itself.

- [ ] [L] Conduct domain-driven design (DDD) event-storming or domain mapping sessions with stakeholders and record bounded context candidates in `decomposition/06-bounded-contexts.md`
- [ ] [L] Analyze module coupling and cohesion across identified boundaries — document afferent/efferent coupling scores and hotspots in `decomposition/07-coupling-analysis.md`
- [ ] [M] Identify data ownership boundaries — map which modules own which data entities and flag shared data conflicts in `decomposition/08-data-ownership-map.md`
- [ ] [M] Evaluate each bounded context candidate against decomposition criteria (independent deployability, team ownership, change frequency, scalability need) and score in `decomposition/09-candidate-scoring.md`
- [ ] [M] Identify and document decomposition anti-patterns present in the codebase (e.g., distributed monolith risks, chatty service boundaries, shared mutable state) in `decomposition/10-antipattern-risks.md`
- [ ] [S] Prioritize decomposition candidates into a ranked shortlist (High / Medium / Low) based on scoring in `decomposition/09-candidate-scoring.md` and record in `decomposition/11-priority-shortlist.md`

---

## Phase 3 — Testing & Validation

- [ ] [M] Review existing test coverage for each decomposition candidate boundary — document gaps that would need to be closed before extraction in `decomposition/12-test-coverage-gaps.md`
- [ ] [S] Validate bounded context boundaries with domain experts in a structured review session and record sign-off or revision notes in `decomposition/06-bounded-contexts.md`
- [ ] [S] Peer-review the coupling analysis and data ownership map with at least two engineers not involved in the original analysis and record review outcomes in `decomposition/13-peer-review-notes.md`

---

## Phase 4 — CI/CD & Infrastructure

N/A — not applicable to this task. No code extraction or deployment changes are in scope for an evaluation and documentation effort.

---

## Phase 5 — Documentation & Rollout

- [ ] [L] Author the final decomposition opportunities report consolidating all phase outputs, including executive summary, candidate services, risks, and recommended sequencing in `decomposition/14-decomposition-report.md`
- [ ] [M] Create a proposed migration roadmap with phased extraction sequence, dependency order, and effort estimates in `decomposition/15-migration-roadmap.md`
- [ ] [S] Document decision log capturing key architectural decisions and trade-offs considered during evaluation in `decomposition/16-decision-log.md` (ADR format recommended)
- [ ] [S] Present findings to stakeholders and engineering leadership — capture feedback and open questions in `decomposition/17-stakeholder-review-notes.md`
- [ ] [XS] Archive all working documents and link the final report from the project README or central wiki landing page

---

> **Assumptions & Caveats:**
> - All file paths above (`decomposition/`) are suggested conventions — adjust to match your actual repository or documentation structure.
> - Task sizing assumes a small team (2–3 engineers + 1 architect). Adjust sizes if the monolith is very large or stakeholder availability is limited.
> - No implementation, refactoring, or infrastructure tasks are included, as the stated goal is evaluation and documentation only.