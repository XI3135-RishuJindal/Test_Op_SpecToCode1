# PLAN: Monolith Decomposition into Microservices

> **Status:** Draft
> **Upgrade Option:** Moderate
> **Urgency:** Medium

---

## Overview

**Migration Strategy: Strangler-Fig**

Given the medium urgency rating and a moderate effort/risk profile, a **strangler-fig pattern** is the recommended approach. Rather than a big-bang rewrite, individual bounded contexts are extracted incrementally from the monolith while the monolith continues to serve unextracted functionality. Each extracted service is placed behind a routing facade (API gateway or reverse proxy), allowing traffic to be shifted gradually and rolled back per-service without full system downtime.

**Justification:**
- Medium urgency does not warrant the high risk of a big-bang cutover.
- The strangler-fig pattern allows value delivery in phases while limiting blast radius.
- Parallel-run is considered for high-risk service boundaries (e.g., data ownership transitions) but is not the primary strategy due to the cost of maintaining dual write paths.
- Feature-flag gating will be used within phases to control traffic routing to new services.

> **TODO:** Confirm bounded context map once codebase language, runtime, and framework details are available from a full tech analysis. The phases below are structured around a generic decomposition workflow and must be refined against actual module/domain boundaries.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Discovery & Domain Mapping** — Identify bounded contexts, data ownership, and inter-module coupling. Produce a decomposition candidate register. | Access to full codebase and architecture diagrams | TODO (person-days — derive from moderate option once detail is provided) |
| 2 | **Foundation** — Establish shared infrastructure: API gateway, service mesh or inter-service communication pattern, centralized logging/tracing, CI/CD pipeline templates for microservices, and container baseline. | Phase 1 complete; infrastructure decisions finalized | TODO |
| 3 | **Pilot Extraction** — Extract one low-risk, loosely coupled bounded context as a proof-of-concept microservice. Validate operational patterns (deployment, observability, rollback). | Phase 2 complete | TODO |
| 4 | **Incremental Extraction** — Extract remaining high-priority bounded contexts one at a time, applying lessons from Phase 3. Each extraction follows: isolate → anti-corruption layer → extract → migrate data → cut over traffic. | Phase 3 complete; per-service data migration plans | TODO |
| 5 | **Monolith Decommission** — Retire residual monolith shell once all bounded contexts are extracted and traffic fully migrated. | Phase 4 complete; all services stable in production | TODO |

> **TODO:** Populate effort estimates (person-days) once the moderate upgrade option detail and codebase inventory are provided.

---

## Component Changes

> **TODO:** Specific class names, method names, and file paths cannot be identified because the language, runtime, build tool, and codebase context were not provided in the tech analysis. The structural changes below are described generically and **must be mapped to actual components** during Phase 1 discovery.

### General Structural Changes Per Extracted Service

| Concern | Monolith State | Target Microservice State |
|---------|---------------|--------------------------|
| **Routing** | Internal method/function calls | HTTP/gRPC endpoints or async messaging (TODO: confirm transport) |
| **Data store** | Shared monolith database | Dedicated per-service data store (database-per-service pattern) |
| **Authentication** | Centralized in-process auth | Delegated to API gateway or shared auth service |
| **Configuration** | Single config file/env block | Per-service config, externalized (TODO: confirm config management tooling) |
| **Build artifact** | Single deployable unit | Independent container image per service |
| **Inter-service calls** | In-process | Anti-corruption layer → synchronous REST/gRPC or async event bus (TODO: confirm broker) |

### Anti-Corruption Layer (ACL)
- During extraction, an ACL module must be introduced at the monolith boundary to translate between the monolith's internal domain model and the new service's API contract.
- **TODO:** Identify specific modules/classes that represent domain boundaries once code context is available.

### API Gateway / Routing Facade
- A routing facade must be introduced in Phase 2 to front both the monolith and extracted services, enabling traffic shifting without client-side changes.
- **TODO:** Select and name the gateway component (e.g., Kong, AWS API Gateway, Nginx, Envoy) based on infrastructure context.

---

## Dependency Upgrade Plan

> **TODO:** No dependency versions were provided in the tech analysis (language, runtime, framework, and build tool are all listed as unknown). This table must be populated after Phase 1 discovery identifies the technology stack.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| TODO | TODO | TODO | TODO | TODO |

**Note:** All version numbers will be sourced exclusively from the tech analysis output — no assumptions will be made from external sources.

---

## Infrastructure Changes

> **TODO:** No infrastructure context (Docker, Kubernetes, CI/CD, IaC) was provided. The items below represent the expected infrastructure concerns for this decomposition and must be confirmed or replaced with actual context.

- **Container Runtime:** TODO — Confirm whether Docker or an alternative container runtime is in use. Each extracted microservice will require its own `Dockerfile` and image build pipeline.
- **Orchestration:** TODO — Confirm whether Kubernetes, ECS, or another orchestrator is the target. Kubernetes is assumed as the likely target; if confirmed, each service will require `Deployment`, `Service`, and `ConfigMap` manifests.
- **Service Mesh:** TODO — Evaluate whether a service mesh (e.g., Istio, Linkerd) is warranted for inter-service mTLS, traffic management, and observability.
- **API Gateway:** TODO — Select and configure a gateway to front the strangler-fig routing facade (Phase 2).
- **CI/CD Pipelines:** TODO — Existing monolith pipeline must be extended or replaced with per-service pipeline templates. Confirm current CI/CD tooling (e.g., GitHub Actions, Jenkins, GitLab CI).
- **Observability Stack:** TODO — Centralized distributed tracing (e.g., Jaeger, Zipkin), metrics (e.g., Prometheus/Grafana), and log aggregation (e.g., ELK, Loki) must be in place before Phase 3.
- **IaC:** TODO — Confirm IaC tooling (Terraform, Pulumi, CloudFormation) for provisioning per-service infrastructure.

---

## Rollback Strategy

Each phase is independently reversible. Rollback is executed per-service, not per-phase wholesale.

### Phase 1 — Discovery & Domain Mapping
- **Rollback:** No production changes made. Discard decomposition candidate register and revert to monolith-only operation. No technical rollback required.

### Phase 2 — Foundation
- **Rollback:** Remove API gateway / routing facade from the traffic path. All requests revert to the monolith directly. Decommission shared infrastructure provisioned in this phase.
- **Gate:** Do not proceed to Phase 3 until the routing facade has been validated in a non-production environment.

### Phase 3 — Pilot Extraction
- **Rollback:** Flip the feature flag / routing rule at the API gateway to redirect 100% of traffic for the pilot service back to the monolith. The extracted service can be stopped without affecting other functionality.
- **Data Rollback:** If data migration has occurred, execute the documented reverse migration script before decommissioning the extracted service's data store.
- **Gate:** Pilot service must pass all integration and smoke tests before Phase 4 begins.

### Phase 4 — Incremental Extraction (per service)
- **Rollback:** Each service extraction is independently reversible using the same mechanism as Phase 3: reroute traffic at the gateway back to the monolith, execute reverse data migration if applicable, stop the extracted service.
- **Sequencing:** Services must be extracted in dependency order (leaf services first) to avoid cascading rollback requirements.
- **TODO:** Define maximum acceptable rollback window (RTO) per service once SLAs are known.

### Phase 5 — Monolith Decommission
- **Rollback:** Monolith artifact and data store must be retained (not deleted) for a defined retention period post-decommission. If a critical regression is detected, the monolith can be redeployed and the gateway routing rules reverted.
- **TODO:** Define retention period and decommission sign-off criteria.

---

## Testing Strategy

### Test Pyramid

| Layer | Scope | Tools | Coverage Target | CI Gate |
|-------|-------|-------|----------------|---------|
| **Unit** | Individual service logic, domain models, ACL translation | TODO (derive from stack once language is known) | ≥ 80% line coverage per extracted service | Block merge on failure |
| **Integration** | Service-to-service contracts, database interactions, API gateway routing rules | TODO — consider Pact for consumer-driven contract testing; Testcontainers for DB | All inter-service contracts covered | Block merge on failure |
| **Regression** | End-to-end flows covering business-critical paths that span monolith + extracted services | TODO (e.g., Playwright, Postman/Newman, RestAssured — derive from stack) | 100% of P0/P1 user journeys | Block release on failure |
| **Performance** | Latency and throughput baselines for extracted services vs. monolith equivalent | TODO (e.g., k6, Gatling, Locust — derive from stack) | p99 latency ≤ monolith baseline; no throughput regression | Block release if regression > 10% |

### Additional Testing Concerns

- **Contract Testing:** Introduce consumer-driven contract tests (e.g., Pact) at each service boundary before extraction to detect breaking API changes early.
- **Chaos/Resilience Testing:** TODO — Once services are in production (Phase 4+), introduce fault injection to validate circuit breakers and fallback behavior.
- **Data Migration Validation:** Each data migration script must have a corresponding validation test that asserts row counts, referential integrity, and spot-check data fidelity before traffic cutover.
- **Feature Flag Testing:** Routing flag states (monolith path vs. service path) must both be covered in integration and regression suites.

---

## Timeline

> **TODO:** Person-day estimates were not provided in the moderate upgrade option detail. The milestone structure below is correct; effort values and completion dates must be populated once the upgrade option is fully specified and Phase 1 discovery is complete.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Decomposition candidate register finalized | Phase 1 | TODO | TODO |
| Bounded context map approved by stakeholders | Phase 1 | TODO | TODO |
| API gateway and observability stack live in non-prod | Phase 2 | TODO | TODO |
| CI/CD pipeline templates for microservices validated | Phase 2 | TODO | TODO |
| Pilot service extracted and serving production traffic | Phase 3 | TODO | TODO |
| Pilot service rollback procedure validated | Phase 3 | TODO | TODO |
| All priority-1 bounded contexts extracted | Phase 4 | TODO | TODO |
| All bounded contexts extracted; monolith in maintenance mode | Phase 4 | TODO | TODO |
| Monolith decommissioned | Phase 5 | TODO | TODO |

---

*This document will be updated as Phase 1 discovery produces concrete bounded context definitions, technology stack confirmation, and refined effort estimates from the moderate upgrade option.*