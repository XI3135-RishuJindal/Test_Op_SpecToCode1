# PLAN: Monolith Decomposition into Microservices

> **Status:** Draft
> **Upgrade Option:** moderate
> **Urgency:** Medium

---

## Overview

**Migration Strategy: Strangler-Fig**

Given the medium urgency rating and the "moderate" effort option, a **strangler-fig pattern** is the recommended approach. Rather than a high-risk big-bang rewrite, bounded contexts are extracted incrementally from the monolith while the monolith continues to serve unextracted functionality. Each extracted service is placed behind a routing facade (API gateway or reverse proxy) that progressively redirects traffic as services become production-ready.

**Justification:**
- Medium urgency does not warrant the delivery risk of a big-bang decomposition.
- The strangler-fig pattern allows rollback at the individual service boundary rather than requiring full system rollback.
- Incremental extraction produces demonstrable value at each phase and limits blast radius of failures.
- Tech stack is currently unconfirmed (see TODOs below); strangler-fig tolerates discovery of unknowns mid-execution better than parallel-run or feature-flag strategies that require deep instrumentation upfront.

> **TODO:** Once the language, runtime, and build tool are confirmed via codebase audit, validate that the strangler-fig routing layer (API gateway / reverse proxy) is compatible with the existing entry points.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 0 | **Discovery & Domain Mapping** — Audit codebase, identify bounded contexts, map data ownership, document inter-module coupling, produce decomposition candidate register | Access to full source repository and production traffic data | TODO person-days (derive after codebase audit) |
| 1 | **Foundation** — Establish shared infrastructure: service mesh or API gateway skeleton, CI/CD pipeline templates, container base images, observability stack (logging, tracing, metrics), inter-service contract testing framework | Phase 0 complete; infrastructure platform confirmed | TODO person-days |
| 2 | **Extract First Candidate Service** — Select lowest-coupling bounded context from Phase 0 register; extract, deploy, and route traffic via strangler facade; validate parity with monolith behavior | Phase 1 complete | TODO person-days |
| 3 | **Extract Subsequent Services (Iterative)** — Repeat extraction pattern for each remaining candidate in priority order; decommission monolith modules as services reach stable production state | Phase 2 pattern validated | TODO person-days per service |
| 4 | **Monolith Decommission & Cleanup** — Remove strangler facade routing rules for fully migrated paths; retire monolith deployment; finalize documentation | All services extracted and validated | TODO person-days |

> **TODO:** Populate person-day estimates once the upgrade option detail and codebase size metrics are available.

---

## Component Changes

### Strangler-Fig Facade / API Gateway
- **What changes:** A new routing layer is introduced in front of the monolith. Initially it passes all traffic through to the monolith. As each service is extracted, routing rules are updated to direct relevant requests to the new service.
- **Files affected:** TODO — routing configuration files (e.g., `nginx.conf`, `gateway.yaml`, or equivalent) to be identified after infrastructure audit.
- **APIs modified:** No external API contract changes in early phases; internal routing is transparent to consumers.

### Bounded Context Extraction (per service)
- **What changes:** A self-contained module within the monolith is refactored into a standalone deployable service with its own data store, API surface, and deployment unit.
- **Files affected:** TODO — specific class/module/file names to be identified during Phase 0 domain mapping.
- **APIs modified:** Internal method calls between the extracted module and the remaining monolith are replaced with network calls (REST, gRPC, or message queue — TODO: confirm preferred IPC mechanism).

### Data Layer Decomposition
- **What changes:** Shared database tables owned by extracted bounded contexts are migrated to service-owned data stores. The monolith accesses this data via the new service's API rather than direct DB queries.
- **Files affected:** TODO — ORM models, repository classes, migration scripts (names unknown until codebase audit).
- **APIs modified:** TODO — data access layer interfaces.

### Observability Instrumentation
- **What changes:** Distributed tracing, structured logging, and health-check endpoints are added to each extracted service.
- **Files affected:** TODO — application bootstrap/entry-point files, middleware configuration.
- **APIs modified:** New `/health` and `/metrics` endpoints added per service.

> **TODO:** All specific class names, method names, and file paths are pending codebase audit in Phase 0.

---

## Dependency Upgrade Plan

N/A — not applicable to this task.

> **Note:** No specific framework or library versions were provided in the tech analysis. Dependency upgrade decisions for individual extracted services should be documented in per-service implementation plans produced during Phase 2 and Phase 3.

---

## Infrastructure Changes

> **TODO:** Language, runtime, build tool, and existing infrastructure platform are unconfirmed. The items below represent the expected infrastructure changes for a typical strangler-fig decomposition; each must be validated against actual context.

- **Container Images:** TODO — define base images per extracted service once runtime is confirmed.
- **Orchestration:** TODO — confirm whether Kubernetes, ECS, or other orchestration is in use. If Kubernetes: new `Deployment`, `Service`, and `Ingress` manifests required per extracted service.
- **API Gateway / Reverse Proxy:** TODO — confirm existing gateway (e.g., Kong, AWS API Gateway, nginx, Envoy). Routing rules must be added per extraction phase.
- **Service Mesh:** TODO — evaluate whether a service mesh (e.g., Istio, Linkerd) is warranted based on number of services and traffic complexity.
- **CI/CD Pipelines:** TODO — confirm existing CI/CD tooling. New pipeline templates required per extracted service (build → test → container build → deploy).
- **Secrets Management:** TODO — confirm secrets management approach for inter-service credentials.
- **Observability Stack:** TODO — confirm logging aggregator, metrics platform, and tracing backend (e.g., ELK, Prometheus/Grafana, Jaeger/Zipkin).

---

## Rollback Strategy

### Phase 0 — Discovery & Domain Mapping
- **Rollback:** No production changes made. Discard decomposition candidate register and revert to monolith-only operation. Zero risk.

### Phase 1 — Foundation
- **Rollback:** Decommission the API gateway / routing facade. All traffic continues to flow directly to the monolith. Remove CI/CD pipeline templates and observability infrastructure if not yet in use.
- **Trigger:** Foundation infrastructure is unstable or incompatible with monolith entry points.

### Phase 2 — Extract First Candidate Service
- **Rollback:** Update the strangler-fig routing rule for the extracted bounded context to redirect 100% of traffic back to the monolith. The extracted service can be scaled to zero or decommissioned without affecting monolith operation.
- **Trigger:** Extracted service fails parity validation or introduces latency regression beyond agreed SLO.
- **Prerequisite:** Monolith code path for the extracted context must not be deleted until the service is declared stable (maintain monolith code in a feature branch or behind a flag during Phase 2).

### Phase 3 — Extract Subsequent Services (Iterative)
- **Rollback:** Same pattern as Phase 2, applied per service independently. Each service extraction is independently reversible via routing rule reversion.
- **Trigger:** Per-service parity or performance failure.

### Phase 4 — Monolith Decommission
- **Rollback:** This phase is the highest-risk rollback scenario. Mitigation: do not decommission the monolith deployment until all services have been stable in production for a defined soak period (TODO: define soak period SLA). If rollback is required, restore monolith deployment and revert gateway routing rules to monolith.
- **Trigger:** Critical regression discovered post-decommission.

---

## Testing Strategy

### Unit Tests
- **Scope:** Each extracted service's internal business logic.
- **Tools:** TODO — confirm test framework once language/runtime is known.
- **Coverage Target:** ≥ 80% line coverage per extracted service.
- **CI Gate:** Block merge on coverage regression.

### Integration Tests
- **Scope:** Service-to-service interactions; extracted service against its own data store; strangler-fig routing layer.
- **Tools:** TODO — confirm integration test tooling. Recommend contract testing (e.g., Pact) for consumer-driven contract validation between services.
- **CI Gate:** All integration tests must pass before promotion to staging.

### Regression Tests
- **Scope:** End-to-end behavioral parity between monolith and extracted service for each extracted bounded context.
- **Approach:** Record monolith request/response pairs in production (traffic shadowing or log capture) during Phase 0; replay against extracted service during Phase 2/3 to validate parity.
- **Tools:** TODO — confirm traffic shadowing tooling (e.g., GoReplay, Diffy, or equivalent).
- **CI Gate:** Zero parity failures on recorded regression suite before routing cutover.

### Performance / Load Tests
- **Scope:** Latency and throughput of extracted services under production-representative load; comparison against monolith baseline.
- **Tools:** TODO — confirm load testing tooling (e.g., k6, Gatling, Locust).
- **Targets:** TODO — define SLOs (p95 latency, error rate) based on current monolith baselines captured in Phase 0.
- **CI Gate:** Performance tests run on staging before each routing cutover; block cutover if SLO targets are breached.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Codebase audit complete; bounded context register published | 0 | TODO | TODO |
| Decomposition candidate priority list approved | 0 | TODO | TODO |
| API gateway / routing facade live in production (pass-through) | 1 | TODO | TODO |
| CI/CD pipeline templates and observability stack operational | 1 | TODO | TODO |
| First service extracted and serving production traffic | 2 | TODO | TODO |
| First service parity validated; monolith code path frozen | 2 | TODO | TODO |
| All priority services extracted and stable | 3 | TODO | TODO |
| Monolith decommissioned | 4 | TODO | TODO |

> **TODO:** All estimated completion dates and owners are pending: (1) confirmation of codebase size and complexity from Phase 0 audit, (2) team capacity allocation, and (3) detailed person-day estimates from the upgrade option. Populate this table at the conclusion of Phase 0.

---

*Document generated from available context. All TODO items must be resolved before Phase 1 execution begins.*