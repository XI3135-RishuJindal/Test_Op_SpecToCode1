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
- **Unknown runtime/language/build tool** means a full parallel-run or big-bang approach carries unacceptable architectural risk until the codebase is better understood.
- The strangler-fig pattern allows the monolith to remain in production while candidate services are identified, extracted, and validated one at a time.
- Each extracted service can be independently rolled back without affecting the remaining monolith.

> **TODO:** Once the language, runtime, and build toolchain are confirmed, revisit whether a feature-flag-gated extraction pattern should be layered on top of the strangler-fig approach.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Discovery & Domain Mapping** — Audit the monolith codebase, identify bounded contexts, map data ownership, and produce a decomposition candidate register. | Access to full source repository and production traffic data | TODO (person-days — derive from confirmed moderate estimate once tech analysis is complete) |
| 2 | **Dependency & Coupling Analysis** — Identify tight coupling, shared database tables, synchronous call chains, and cross-domain transactions that would block extraction. | Phase 1 output (candidate register) | TODO |
| 3 | **Decomposition Design** — Define service boundaries, inter-service communication contracts (sync/async), and data ownership per candidate service. | Phase 2 output; architecture review sign-off | TODO |
| 4 | **Pilot Extraction (1 service)** — Extract the lowest-risk, highest-value bounded context as a proof-of-concept microservice. Validate operational model. | Phase 3 design docs; infrastructure readiness | TODO |
| 5 | **Incremental Extraction (remaining candidates)** — Extract remaining approved candidates in priority order, one at a time, using the pattern validated in Phase 4. | Phase 4 pilot retrospective | TODO |
| 6 | **Monolith Decommission Planning** — Document residual monolith scope, plan final decommission or retention as a "core" service. | All extractions complete and stable | TODO |

> **TODO:** Populate effort estimates (person-days) once the moderate upgrade option details and codebase size metrics are confirmed.

---

## Component Changes

### General Structural Changes (applicable to all extracted services)

Because the language, runtime, and specific class/method names are not available in the provided context, the following describes the *structural pattern* of changes required. All items marked **TODO** must be resolved during Phase 1.

---

### Monolith Core

| Concern | Change Required |
|---------|----------------|
| Entry points / controllers | TODO — identify and annotate which route handlers or controllers belong to each bounded context |
| Shared domain models | TODO — identify models that span multiple bounded contexts; these are extraction blockers |
| Shared utility/helper classes | TODO — classify as: (a) copy-per-service, (b) promoted to shared library, or (c) remain in monolith |
| Database access layer | TODO — identify per-context data access objects/repositories; shared tables must be resolved before extraction |
| Internal API calls | TODO — map all in-process method calls that cross bounded context boundaries; these become candidate inter-service contracts |

---

### Per Extracted Service (template — repeat for each candidate)

- **New repository / module:** Each extracted service gets its own deployable unit.
- **API contract:** Define and version the external interface (REST, gRPC, or message-based — TODO: confirm based on tech stack).
- **Data store:** Each service owns its own schema/database; shared tables must be split or replicated with an agreed ownership model.
- **Authentication/authorization:** TODO — determine whether the monolith holds a shared auth context that must be replicated or federated.
- **Configuration:** TODO — identify config keys currently shared in monolith config files that must be split per service.

---

### Inter-Service Communication Layer

- **Synchronous calls:** TODO — confirm HTTP/REST or gRPC preference.
- **Asynchronous events:** TODO — confirm whether a message broker (e.g., Kafka, RabbitMQ, SQS) is available or needs to be introduced.
- **Service discovery:** TODO — confirm whether infrastructure provides service discovery (e.g., Kubernetes DNS, Consul).

---

## Dependency Upgrade Plan

N/A — not applicable to this task.

> The tech analysis provides no framework versions or top upgrade targets. Dependency upgrades are not in scope for a decomposition evaluation. If specific service extraction work in Phase 4–5 requires dependency changes, a separate dependency upgrade plan should be authored at that time.

---

## Infrastructure Changes

> All items below are marked TODO because the tech analysis does not specify the current infrastructure stack.

| Concern | Required Change | Status |
|---------|----------------|--------|
| Container strategy | Determine whether each extracted service will be containerized (Docker or equivalent) | TODO |
| Orchestration | Confirm whether Kubernetes, ECS, or another orchestrator is in use or planned | TODO |
| Service mesh | Evaluate need for a service mesh (e.g., Istio, Linkerd) for observability and traffic management between services | TODO |
| API Gateway | Determine whether an API gateway is needed to route external traffic to extracted services while the monolith still handles other routes (core strangler-fig infrastructure) | TODO |
| CI/CD pipelines | Each extracted service will require its own build and deploy pipeline; confirm current CI/CD tooling | TODO |
| Observability | Distributed tracing, centralized logging, and metrics aggregation become critical once services are split; confirm tooling (e.g., OpenTelemetry, Jaeger, Prometheus) | TODO |
| Secrets management | TODO — confirm how secrets/config are currently managed and how they will be distributed per service |
| IaC | TODO — confirm whether Terraform, Pulumi, CloudFormation, or equivalent is in use |

---

## Rollback Strategy

Because the strangler-fig pattern is used, each phase is independently reversible.

### Phase 1 — Discovery & Domain Mapping
- **Rollback:** No production changes are made in this phase. Discard or archive the candidate register. No action required.

### Phase 2 — Dependency & Coupling Analysis
- **Rollback:** No production changes are made. Discard analysis artifacts. No action required.

### Phase 3 — Decomposition Design
- **Rollback:** No production changes are made. Revert design documents in version control. No action required.

### Phase 4 — Pilot Extraction
- **Rollback trigger:** Service instability, data inconsistency, or unacceptable latency regression.
- **Steps:**
  1. Re-route all traffic for the extracted bounded context back to the monolith via the API gateway or load balancer configuration change (single config update, no code change required if strangler-fig routing is in place).
  2. Halt writes to the extracted service's data store; confirm monolith data store is the authoritative source.
  3. Decommission the pilot service deployment.
  4. Archive the pilot service repository (do not delete — preserve for re-extraction).
  5. Document the rollback reason and update the decomposition candidate register.

### Phase 5 — Incremental Extraction (per service)
- **Rollback trigger:** Same as Phase 4, applied per individual service.
- **Steps:** Identical to Phase 4 rollback, applied only to the specific service being rolled back. All other extracted services remain unaffected.

### Phase 6 — Monolith Decommission Planning
- **Rollback:** If decommission is initiated and issues arise, re-enable the monolith deployment from the last known good artifact. TODO — confirm artifact retention policy.

---

## Testing Strategy

> Specific tools are marked TODO where the tech stack is unknown. The strategy below defines the required *layers* and *gates* regardless of tooling.

### Test Pyramid

| Layer | Scope | Tooling | Coverage Target | CI Gate |
|-------|-------|---------|----------------|---------|
| **Unit** | Individual service business logic in isolation | TODO (confirm language-appropriate framework) | ≥ 80% line coverage per extracted service | Block merge on failure |
| **Integration** | Service-to-service contracts; database interactions | TODO (e.g., contract testing via Pact, or equivalent) | All inter-service API contracts covered | Block merge on failure |
| **Regression** | End-to-end flows that span the monolith and extracted services | TODO (confirm E2E framework) | All critical user journeys covered | Block deployment to staging on failure |
| **Performance** | Latency and throughput comparison: monolith baseline vs. extracted service | TODO (e.g., k6, Gatling, JMeter) | Extracted service P99 latency ≤ monolith baseline + 10% | Block promotion to production on regression |

### Additional Testing Requirements

- **Contract testing:** Before any service extraction goes to production, a consumer-driven contract test suite must exist for every inter-service interface introduced. This is the primary guard against integration regressions in a distributed system.
- **Data consistency tests:** For any bounded context where data is split from a shared database, automated tests must verify that no data is lost or duplicated during and after extraction.
- **Chaos/resilience testing:** TODO — evaluate once infrastructure is confirmed. Recommended before Phase 5 begins at scale.
- **Monolith regression suite:** The existing monolith test suite (TODO — confirm it exists and its coverage level) must continue to pass throughout all phases to confirm the strangler-fig routing does not break remaining monolith functionality.

---

## Timeline

> Effort values are marked TODO because the moderate upgrade option person-days estimate was not provided in the input context. Populate this table once the tech analysis and option details are confirmed.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Decomposition candidate register published | Phase 1 — Discovery | TODO | TODO |
| Coupling analysis report published | Phase 2 — Coupling Analysis | TODO | TODO |
| Service boundary design approved | Phase 3 — Design | TODO | TODO |
| Architecture review sign-off | Phase 3 — Design | TODO | TODO |
| Pilot service live in production | Phase 4 — Pilot Extraction | TODO | TODO |
| Pilot retrospective complete | Phase 4 — Pilot Extraction | TODO | TODO |
| All approved candidates extracted | Phase 5 — Incremental Extraction | TODO | TODO |
| Monolith decommission plan published | Phase 6 — Decommission Planning | TODO | TODO |

---

## Open TODOs Summary

The following blockers must be resolved before Phase 1 can begin:

1. **Confirm language, runtime, and build tool** — required to select appropriate tooling for all phases.
2. **Confirm moderate option person-days estimate** — required to populate all effort and timeline fields.
3. **Confirm current infrastructure** (container, orchestration, CI/CD, observability) — required to populate Infrastructure Changes section.
4. **Confirm existence and coverage of current monolith test suite** — required to establish regression baseline.
5. **Confirm inter-service communication preferences** (sync vs. async, protocol) — required to finalize Phase 3 design.
6. **Confirm data store architecture** (shared DB, schema-per-service, etc.) — required to assess extraction complexity.