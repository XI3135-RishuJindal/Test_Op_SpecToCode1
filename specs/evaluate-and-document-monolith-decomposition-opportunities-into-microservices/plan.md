# PLAN: Monolith Decomposition into Microservices

> **Status:** Draft
> **Spec reference:** spec.md
> **Option selected:** Moderate decomposition path

---

## Overview

**Migration Strategy: Strangler-Fig**

Given the moderate upgrade urgency and the nature of monolith decomposition (an inherently incremental, risk-managed activity), a **strangler-fig pattern** is the recommended strategy. New microservices are carved out of the monolith one bounded context at a time, with the monolith continuing to serve unextracted functionality until each domain is fully migrated and verified.

**Justification:**
- A big-bang rewrite is ruled out due to insufficient context on the existing codebase size, test coverage, and runtime — the risk of a full cutover without parallel validation is unacceptably high at medium urgency.
- Strangler-fig allows independent deployment, rollback per service, and incremental value delivery.
- Parallel-run is a supporting tactic within individual phases (not the overarching strategy) and will be applied at the API boundary level during cutover of each extracted service.
- Feature-flag gating will be used at routing boundaries to control traffic shifting between monolith and extracted services.

> **TODO:** Once language, runtime, and build tool are confirmed from codebase analysis, validate that the strangler-fig approach is compatible with the existing inter-module communication patterns (in-process calls vs. shared database vs. shared memory).

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| **0 — Discovery & Domain Mapping** | Analyze the monolith codebase to identify bounded contexts, data ownership boundaries, and coupling hotspots. Produce a domain map and decomposition candidate list. | Access to full source code and production traffic data | TODO (person-days — derive once codebase size is known) |
| **1 — Foundation & Infrastructure Scaffolding** | Establish shared infrastructure: service mesh or API gateway, container orchestration baseline, CI/CD pipeline templates, observability stack (logging, tracing, metrics), and inter-service communication contracts (e.g., async messaging or REST/gRPC stubs). | Phase 0 domain map | TODO |
| **2 — Extract First Bounded Context (Pilot Service)** | Select the lowest-coupling, highest-value domain identified in Phase 0. Extract it as the pilot microservice. Validate the end-to-end operational model (deploy, observe, rollback). | Phase 1 infrastructure | TODO |
| **3 — Iterative Extraction of Remaining Contexts** | Repeat the extraction pattern for each subsequent bounded context, in dependency order. Each extraction is a sub-phase with its own rollback gate. | Phase 2 validated pattern | TODO |
| **4 — Monolith Decommission & Cleanup** | Retire residual monolith modules as each domain is fully migrated. Remove shared database coupling. Finalize service ownership and runbooks. | All Phase 3 extractions complete | TODO |

> **TODO:** Populate effort estimates (person-days) once the upgrade option's detailed estimate is provided and the Phase 0 domain map is complete.

---

## Component Changes

> **TODO:** Specific class names, method names, and file paths cannot be identified because the language, runtime, and codebase context have not been provided. The structure below defines what must be documented once source analysis is complete.

### General Pattern Per Extracted Component

**For each bounded context identified in Phase 0:**

| Concern | What Changes | Files Affected | APIs Modified |
|---------|-------------|----------------|---------------|
| **Domain Logic** | Moved from monolith module/package into standalone service repository | TODO — identify source module paths in Phase 0 | Internal method calls become network calls (REST, gRPC, or async events) |
| **Data Layer** | Shared database tables owned by this domain are migrated to a dedicated datastore; monolith accesses via service API during transition | TODO — identify schema ownership in Phase 0 | Direct DB queries replaced with service client calls |
| **API Surface** | Monolith exposes a facade/proxy at the existing endpoint; facade routes to new service once validated | TODO — identify controller/handler files | Existing public API contracts must be preserved (no breaking changes to consumers) |
| **Configuration** | Service-specific config extracted from monolith config files into per-service config | TODO — identify config file paths | Config keys scoped to service namespace |
| **Authentication/Authorization** | Shared auth context must be propagated via token (e.g., JWT) rather than in-process session | TODO | Auth middleware added to each extracted service |

> **TODO:** Re-populate this section with concrete class/method/file references after Phase 0 discovery is complete.

---

## Dependency Upgrade Plan

N/A — not applicable to this task.

> The tech analysis does not specify current dependency versions, frameworks, or upgrade targets. Dependency changes will be scoped per extracted service during Phase 2–3 and documented in per-service PLAN documents at that time.

---

## Infrastructure Changes

> **TODO:** Infrastructure stack (Docker, Kubernetes, CI/CD, IaC tooling) is not specified in the provided context. The following represents the required infrastructure decisions that must be resolved in Phase 1.

| Infrastructure Concern | Required Decision | Current State | Target State |
|-----------------------|-------------------|---------------|--------------|
| **Container runtime** | Containerize each extracted service | TODO — unknown if monolith is containerized | Each microservice ships as an independently deployable container image |
| **Orchestration** | Service scheduling and scaling | TODO | TODO (e.g., Kubernetes, ECS — select based on existing platform) |
| **API Gateway / Ingress** | Route traffic between monolith and extracted services during transition | TODO | TODO — single ingress point with routing rules per bounded context |
| **Service Mesh** | Mutual TLS, observability, traffic shifting | TODO | TODO (e.g., Istio, Linkerd, or cloud-native equivalent) |
| **Async Messaging** | Decouple services that currently communicate in-process | TODO | TODO (e.g., Kafka, RabbitMQ, cloud pub/sub) |
| **Observability** | Distributed tracing, centralized logging, metrics aggregation | TODO | TODO (e.g., OpenTelemetry + Jaeger/Zipkin, ELK/Loki, Prometheus/Grafana) |
| **CI/CD Pipeline** | Per-service pipelines with independent deploy gates | TODO — unknown current pipeline tooling | Per-service pipeline template; monolith pipeline remains until decommission |
| **IaC** | Infrastructure as code for new services | TODO | TODO (e.g., Terraform, Pulumi, Helm charts) |
| **Secrets Management** | Per-service secret scoping | TODO | TODO (e.g., Vault, cloud-native secrets manager) |

---

## Rollback Strategy

Rollback is designed to be **per-phase and independently reversible**. The strangler-fig pattern ensures the monolith remains the authoritative system until each extraction is explicitly promoted.

### Phase 0 — Discovery & Domain Mapping
- **Rollback:** No production changes made. Discard domain map artifacts. No action required.

### Phase 1 — Foundation & Infrastructure Scaffolding
- **Rollback steps:**
  1. Disable/tear down any new infrastructure provisioned (API gateway rules, service mesh config) without affecting the running monolith.
  2. Remove CI/CD pipeline templates added for microservices; monolith pipeline is unaffected.
  3. Decommission observability stack additions if they introduce overhead on the monolith.
- **Gate:** Monolith must pass its existing smoke/regression suite before and after Phase 1 infrastructure is introduced.

### Phase 2 — Extract Pilot Service
- **Rollback steps:**
  1. Feature flag / traffic routing rule at the API gateway is set to `monolith=100%, new-service=0%` — instant traffic revert without redeployment.
  2. New service containers are stopped and removed from orchestration.
  3. Any database schema changes made for the pilot service must be backward-compatible (expand-contract pattern); contract phase is not applied until rollback window closes.
  4. Revert CI/CD routing to monolith-only deployment.
- **Gate:** Pilot service must serve ≥ N days of production traffic (TODO: define N) with error rate ≤ monolith baseline before the rollback window closes.

### Phase 3 — Iterative Extraction
- **Rollback steps (per extracted service):**
  1. Same traffic-flag revert as Phase 2, applied per service independently.
  2. Services are extracted in dependency order; rolling back service B does not require rolling back service A if A has no runtime dependency on B.
  3. Maintain monolith code paths for each extracted domain until the rollback window closes — do not delete monolith code until Phase 4.
- **Gate:** Each service extraction must pass its integration test suite and a defined soak period before the next extraction begins.

### Phase 4 — Monolith Decommission
- **Rollback steps:**
  1. Monolith decommission is irreversible by design — do not proceed until all Phase 3 rollback windows are closed and all services have passed production soak.
  2. Maintain a tagged, deployable monolith artifact in the artifact registry for a defined retention period (TODO: define retention window, e.g., 90 days) as a last-resort recovery option.
  3. Database decommission follows a separate, explicitly gated runbook — retain read replicas for the retention period.

---

## Testing Strategy

### Test Pyramid

```
          [Performance]
         [Regression / E2E]
        [Integration / Contract]
       [Unit Tests per Service]
```

| Layer | Scope | Tools | Coverage Target | CI Gate |
|-------|-------|-------|-----------------|---------|
| **Unit** | Individual service business logic in isolation | TODO — select based on confirmed language/runtime | ≥ 80% line coverage per extracted service | Block merge on failure |
| **Contract** | API contracts between services (consumer-driven) | TODO (e.g., Pact, Spring Cloud Contract) | 100% of inter-service API endpoints covered | Block merge on failure |
| **Integration** | Service + its own datastore; service + downstream stubs | TODO (e.g., Testcontainers, Docker Compose test environments) | All happy-path and primary error-path flows | Block merge on failure |
| **Regression / E2E** | Full user journeys spanning monolith + extracted services during transition; full microservices post-transition | TODO (e.g., Playwright, Cypress, Karate, Postman/Newman) | Cover all journeys present in monolith acceptance suite | Block deployment to staging on failure |
| **Performance / Load** | Latency and throughput parity with monolith baseline per extracted service | TODO (e.g., k6, Gatling, Locust) | p99 latency ≤ monolith baseline + 10%; error rate ≤ baseline | Block promotion to production on regression |
| **Chaos / Resilience** | Failure injection per service (network partition, dependency timeout) | TODO (e.g., Chaos Monkey, Toxiproxy, LitmusChaos) | Cover all inter-service dependencies | Run in staging; advisory gate initially |

### Additional Testing Notes

- **Contract tests are mandatory** before any service extraction goes to production. The monolith's existing API behavior must be captured as the consumer contract baseline.
- **Parallel-run validation:** During Phase 2–3, shadow traffic or request mirroring (TODO: confirm platform support) should be used to compare monolith vs. new service responses before traffic is shifted.
- **Monolith regression suite** must continue to pass throughout all phases until Phase 4 decommission.
- **TODO:** Define specific coverage tooling once language/runtime is confirmed.

---

## Timeline

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Domain map and decomposition candidate list complete | Phase 0 | TODO — derive from person-days estimate once provided | TODO |
| Infrastructure scaffolding complete and validated | Phase 1 | TODO | TODO |
| Pilot service live in production with rollback window open | Phase 2 | TODO | TODO |
| Pilot service rollback window closed; pattern documented | Phase 2 | TODO | TODO |
| All bounded contexts extracted and in production soak | Phase 3 | TODO | TODO |
| All Phase 3 rollback windows closed | Phase 3 | TODO | TODO |
| Monolith decommissioned; artifact retained in registry | Phase 4 | TODO | TODO |

> **TODO:** All timeline estimates are pending (a) confirmation of the upgrade option's person-days breakdown, (b) completion of Phase 0 domain mapping to determine the number of bounded contexts, and (c) assignment of engineering owners.

---

## Open TODOs Summary

| # | TODO Item | Blocking Phase |
|---|-----------|---------------|
| 1 | Confirm language, runtime, and build tool from codebase analysis | Phase 0 |
| 2 | Confirm existing infrastructure (container platform, CI/CD tooling, database technology) | Phase 1 |
| 3 | Populate person-days estimates from upgrade option detail | All phases |
| 4 | Identify bounded contexts, module paths, and data ownership from source code | Phase 0 → Phase 2 |
| 5 | Select inter-service communication mechanism (sync REST/gRPC vs. async messaging) | Phase 1 |
| 6 | Select and provision observability stack | Phase 1 |
| 7 | Define production soak period and rollback window duration | Phase 2 |
| 8 | Define monolith artifact retention period post-decommission | Phase 4 |
| 9 | Assign engineering owners to each milestone | All phases |
| 10 | Confirm contract testing tooling compatible with confirmed language/runtime | Phase 2 |