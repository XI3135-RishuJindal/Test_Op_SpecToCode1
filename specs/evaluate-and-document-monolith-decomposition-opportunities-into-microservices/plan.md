# PLAN: Monolith Decomposition into Microservices

> **Status:** Draft
> **Spec reference:** spec.md
> **Option selected:** moderate

---

## Overview

**Migration Strategy: Strangler-Fig**

Given the task is to *evaluate and document* decomposition opportunities — and that the upgrade urgency is rated **medium** with a moderate effort option selected — a strangler-fig pattern is the appropriate strategy. This approach allows individual bounded contexts to be extracted incrementally from the monolith without requiring a high-risk big-bang rewrite.

Key justifications:
- **Medium urgency** means there is no forcing function to decompose everything at once; incremental extraction reduces blast radius.
- **Unknown runtime/language/build tooling** means a full parallel-run or big-bang approach carries unacceptable unknowns at this stage.
- The first phase is explicitly an *evaluation and documentation* phase, producing the decomposition map before any code changes are committed.
- Strangler-fig allows the monolith to remain the system of record while candidate services are carved out behind routing or facade layers, enabling independent rollback per extracted service.

> **TODO:** Once the tech stack (language, runtime, build tool, frameworks) is confirmed, revisit whether a feature-flag-gated extraction or parallel-run is more appropriate for specific high-risk components.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Discovery & Domain Mapping** — Identify bounded contexts, data ownership boundaries, and inter-module coupling via static analysis and team interviews. Produce a decomposition candidate register. | Access to codebase, architecture diagrams, team SMEs | TODO (derive from confirmed person-days once stack is known) |
| 2 | **Decomposition Blueprint** — For each candidate service: define API contracts, data ownership, synchronous vs. asynchronous communication patterns, and dependency graph. Document in ADRs. | Phase 1 output | TODO |
| 3 | **Pilot Extraction (1–2 services)** — Extract the lowest-coupling, highest-value candidate service(s) using strangler-fig. Establish shared infrastructure patterns (service template, CI pipeline, observability). | Phase 2 blueprint, infrastructure readiness | TODO |
| 4 | **Incremental Extraction** — Extract remaining prioritized services per the blueprint, one bounded context at a time. Decommission monolith modules as services reach production parity. | Phase 3 patterns established | TODO |
| 5 | **Monolith Decommission & Validation** — Validate full traffic has migrated, remove dead monolith code paths, finalize documentation. | Phase 4 complete | TODO |

> **TODO:** Populate effort estimates (person-days) once the moderate upgrade option's specific estimates are provided and the tech stack is confirmed.

---

## Component Changes

> **TODO:** Specific class names, method names, and file paths cannot be identified because the language, runtime, and codebase context have not been provided. The structure below defines what must be documented per component once the codebase is analyzed.

### Per-Component Template (to be completed in Phase 1–2)

For each decomposition candidate identified during discovery, document:

| Field | Detail |
|-------|--------|
| **Component / Bounded Context** | Name of the domain area (e.g., `OrderManagement`, `UserAuth`, `Billing`) |
| **Affected Files** | TODO — list source files, modules, packages |
| **Structural Change** | Extract to standalone service; replace in-process calls with API/event calls |
| **APIs Modified** | TODO — internal method calls become HTTP REST / gRPC / message queue contracts |
| **Data Store Change** | TODO — identify shared database tables to be split or replicated |
| **Strangler Facade** | A routing layer or API gateway rule that redirects traffic from monolith to new service |
| **Coupling Risk** | TODO — identify circular dependencies or shared mutable state |

### Known Structural Concerns (to be validated in Phase 1)

- **Shared database anti-pattern:** Monoliths commonly share a single database schema across domains. Each extracted service must own its data — identify tables requiring ownership transfer or event-driven synchronization.
- **Synchronous call chains:** Deep in-process call stacks must be mapped before extraction to avoid distributed deadlocks.
- **Shared libraries / utilities:** Cross-cutting concerns (logging, auth, validation) must be promoted to shared libraries or platform services, not duplicated.

---

## Dependency Upgrade Plan

N/A — not applicable to this task.

> The task is decomposition evaluation and planning. No specific dependency versions have been provided in the tech analysis (language, runtime, build tool, and frameworks are all listed as unknown). Dependency upgrade planning will be addressed per-service once the pilot extraction phase begins.
>
> **TODO:** Populate this table after Phase 1 discovery confirms the tech stack and per-service dependency requirements.

---

## Infrastructure Changes

> **TODO:** No infrastructure context has been provided. The following items must be investigated and confirmed during Phase 1–2.

| Infrastructure Concern | Status | Notes |
|------------------------|--------|-------|
| Container runtime (Docker base images) | TODO | Confirm whether monolith is containerized; define base image standards for extracted services |
| Orchestration (Kubernetes / other) | TODO | Confirm orchestration platform; define namespace and resource quota strategy per service |
| Service mesh / inter-service networking | TODO | Evaluate need for service mesh (e.g., Istio, Linkerd) for mTLS, traffic management, and observability |
| API Gateway / ingress routing | TODO | Required for strangler-fig routing; confirm existing gateway or plan introduction |
| CI/CD pipeline per service | TODO | Each extracted service needs an independent pipeline; confirm current CI/CD tooling |
| Secrets management | TODO | Confirm vault/secrets strategy for per-service credentials |
| Observability stack (logs, metrics, traces) | TODO | Distributed tracing (e.g., OpenTelemetry) is critical for microservices; confirm existing tooling |
| IaC (Terraform / Helm / other) | TODO | Confirm IaC tooling for per-service infrastructure provisioning |

---

## Rollback Strategy

Each phase is independently reversible under the strangler-fig pattern.

### Phase 1 — Discovery & Domain Mapping
- **Rollback:** No code changes made. Discard or archive the decomposition candidate register. No system impact.

### Phase 2 — Decomposition Blueprint
- **Rollback:** No code changes made. ADRs are documentation artifacts. No system impact.

### Phase 3 — Pilot Extraction
- **Rollback steps:**
  1. Revert the strangler-fig routing rule (API gateway / proxy config) to direct 100% of traffic back to the monolith code path.
  2. Stop and decommission the pilot microservice deployment.
  3. Verify monolith is handling all traffic via smoke tests and monitoring.
  4. If a separate data store was introduced, confirm the monolith's data store is current (no data was written exclusively to the new service's store without sync).
  5. Archive the extracted service code in a branch; do not delete.

### Phase 4 — Incremental Extraction
- **Rollback steps (per service):**
  1. Each service extraction is independently reversible using the same routing-revert mechanism as Phase 3.
  2. Maintain the monolith code path for each extracted domain until the service has been in production for a defined stability window (TODO: define SLA threshold).
  3. Do not delete monolith code paths until Phase 5 sign-off.

### Phase 5 — Monolith Decommission
- **Rollback steps:**
  1. This phase is the highest-risk for rollback. Do not proceed until all services have passed the stability window.
  2. If a critical failure occurs post-decommission, restore the monolith from the last known good deployment artifact (container image tag or build artifact — TODO: confirm artifact retention policy).
  3. Re-enable monolith routing at the gateway layer.
  4. Conduct a blameless post-mortem before re-attempting decommission.

---

## Testing Strategy

> **TODO:** Specific test frameworks and tooling cannot be specified without knowing the language and runtime. The strategy below defines the required layers and gates; tooling must be confirmed in Phase 1.

### Test Pyramid

| Layer | Scope | Target Coverage | CI Gate |
|-------|-------|-----------------|---------|
| **Unit** | Individual service business logic, domain models | TODO (recommend ≥80% line coverage per service) | Block merge on failure |
| **Integration** | Service ↔ database, service ↔ message broker, service ↔ dependent APIs | Key happy paths + failure modes | Block merge on failure |
| **Contract** | API contracts between services (consumer-driven contract tests) | All inter-service interfaces | Block merge on failure; TODO: evaluate Pact or equivalent |
| **End-to-End / Regression** | Critical user journeys spanning multiple services | Top 10 business-critical flows | Block release on failure |
| **Performance / Load** | Latency and throughput per extracted service under expected load | TODO: define SLOs per service | Block release if SLO breached |
| **Chaos / Resilience** | Failure injection (service unavailability, network partition) | Key dependency failure scenarios | TODO: evaluate Chaos Monkey / Gremlin / Toxiproxy |

### Key Testing Concerns for Decomposition

- **Contract testing is mandatory** for microservices. Without it, interface drift between services will cause silent production failures. Establish contract tests before any service goes to production.
- **Data migration testing:** Any schema split or data ownership transfer must be tested with production-representative data volumes.
- **Observability validation:** Distributed traces must be verified end-to-end in staging before each service extraction goes live.

---

## Timeline

> **TODO:** Specific dates and person-day allocations cannot be derived because the moderate upgrade option's effort estimates were not provided and the tech stack is unknown. The table below defines milestones; owners and dates must be assigned once Phase 1 is scoped.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|----------------------|-------|
| Codebase access and tooling confirmed | 1 | TODO | TODO |
| Bounded context map complete | 1 | TODO | TODO |
| Decomposition candidate register published | 1 | TODO | TODO |
| API contract drafts complete for all candidates | 2 | TODO | TODO |
| ADRs approved for pilot service(s) | 2 | TODO | TODO |
| Infrastructure baseline confirmed (CI, gateway, observability) | 2–3 | TODO | TODO |
| Pilot service(s) live in production (strangler-fig) | 3 | TODO | TODO |
| Pilot stability window passed; monolith path retired for pilot | 3 | TODO | TODO |
| All prioritized services extracted and stable | 4 | TODO | TODO |
| Monolith decommissioned | 5 | TODO | TODO |

---

## Open TODOs Summary

| # | Item | Blocking Phase |
|---|------|---------------|
| 1 | Confirm language, runtime, build tool, and frameworks | 1 |
| 2 | Confirm moderate option person-days estimate for effort allocation | 1 |
| 3 | Identify specific files, classes, and modules from codebase | 1 |
| 4 | Confirm container/orchestration infrastructure | 2 |
| 5 | Confirm CI/CD tooling and pipeline structure | 2 |
| 6 | Confirm observability stack and tracing capability | 2 |
| 7 | Define per-service SLOs for performance gates | 2 |
| 8 | Select contract testing framework | 2 |
| 9 | Define artifact retention policy for rollback | 2 |
| 10 | Assign milestone owners and target dates | 1 |