# PLAN: Monolith Decomposition into Microservices

> **Status:** Draft
> **Upgrade Option:** Moderate
> **Urgency:** Medium

---

## Overview

**Migration Strategy: Strangler-Fig**

Given the medium urgency rating and a moderate effort/risk profile, a **strangler-fig pattern** is the recommended approach. Rather than a big-bang rewrite, bounded contexts are extracted incrementally from the monolith while the monolith continues to serve unextracted functionality. Each extracted service is placed behind a routing layer (API gateway or reverse proxy) that progressively redirects traffic away from the monolith.

**Justification:**
- Medium urgency does not warrant the high risk of a big-bang cutover.
- The strangler-fig pattern allows independent rollback of each extracted service without affecting the remaining monolith.
- Parallel-run validation can be applied per service boundary before traffic is shifted, reducing regression risk.
- Because the language, runtime, and framework details are not yet confirmed (see TODOs below), locking in a full decomposition schedule prematurely would introduce unnecessary rework risk.

> **TODO:** Once the tech analysis is completed (language, runtime, build tool, frameworks confirmed), re-evaluate whether any domain boundaries are constrained by framework coupling that would change this strategy.

---

## Phases

| Phase | Description | Dependencies | Estimated Effort |
|-------|-------------|--------------|-----------------|
| 1 | **Discovery & Domain Mapping** — Identify bounded contexts, data ownership boundaries, and inter-module coupling via static analysis and team workshops. Produce a decomposition candidate register. | Access to codebase, team availability | TODO (derive from confirmed person-days once tech analysis is complete) |
| 2 | **Routing Layer Introduction** — Deploy an API gateway or reverse proxy in front of the monolith with pass-through routing. No behavioral change; establishes the traffic control plane for future extractions. | Phase 1 complete; infrastructure access | TODO |
| 3 | **Pilot Service Extraction** — Extract the lowest-coupling, highest-value bounded context identified in Phase 1 as a proof-of-concept microservice. Validate data isolation, API contracts, and deployment pipeline. | Phase 2 complete; CI/CD pipeline available | TODO |
| 4 | **Incremental Service Extractions** — Extract remaining prioritized bounded contexts one at a time, following the pattern validated in Phase 3. Each extraction includes its own data store migration if required. | Phase 3 complete; per-service dependencies | TODO |
| 5 | **Monolith Decommission & Cleanup** — Once all targeted bounded contexts are extracted and traffic fully redirected, decommission residual monolith modules. Remove dead code and shared-schema coupling. | All Phase 4 extractions complete | TODO |

> **TODO:** Populate effort estimates (person-days) once the upgrade option details and tech analysis are confirmed.

---

## Component Changes

> **TODO:** Specific file names, class names, method names, and API signatures cannot be identified because the codebase context has not been provided. The structure below defines what must be documented once context is available.

### General Structural Changes Per Extracted Service

**Monolith (source)**
- Identify and isolate the module/package representing the bounded context.
- Replace internal method calls that cross the boundary with an interface or anti-corruption layer.
- Remove direct database table access from outside the boundary; enforce ownership via service API.
- TODO: List specific files, classes, and methods once codebase context is provided.

**New Microservice (target)**
- Owns its own data store (schema or database instance, depending on isolation requirements).
- Exposes a versioned API (REST, gRPC, or messaging — TODO: confirm based on tech stack).
- Contains its own build, test, and deployment pipeline.
- TODO: Define service scaffolding conventions once language/runtime is confirmed.

**Routing Layer**
- API gateway or reverse proxy configuration updated per extraction to redirect routes.
- TODO: Identify specific gateway product/config files once infrastructure context is provided.

**Shared Libraries / Cross-Cutting Concerns**
- Authentication, logging, tracing, and configuration must be extracted into shared libraries or sidecars before or during Phase 3.
- TODO: Identify existing shared utilities in the monolith codebase.

---

## Dependency Upgrade Plan

> **TODO:** No dependency versions are available from the provided tech analysis (language, runtime, build tool, and frameworks are listed as unknown). This table must be populated once the tech analysis is completed.

| Dependency | Current Version | Target Version | Breaking Changes | Migration Notes |
|------------|----------------|----------------|-----------------|-----------------|
| TODO | TODO | TODO | TODO | TODO |

---

## Infrastructure Changes

> **TODO:** No infrastructure context (Docker, Kubernetes, CI/CD, IaC) has been provided. The following items must be investigated and confirmed before Phase 2 begins.

- **Container Strategy:** TODO — Determine whether the monolith is currently containerized. Each extracted microservice will require its own container image and base image definition.
- **Orchestration:** TODO — Confirm whether Kubernetes, ECS, or another orchestrator is in use. Kubernetes manifests (Deployment, Service, ConfigMap, HorizontalPodAutoscaler) will be required per extracted service.
- **API Gateway / Reverse Proxy:** TODO — Confirm existing gateway tooling (e.g., Kong, NGINX, AWS API Gateway, Envoy). Phase 2 routing layer configuration depends on this.
- **Service Discovery:** TODO — Confirm DNS-based or registry-based service discovery mechanism.
- **CI/CD Pipeline:** TODO — Confirm pipeline tooling (e.g., GitHub Actions, Jenkins, GitLab CI). Each microservice will require an independent pipeline with build, test, and deploy stages.
- **Observability Stack:** TODO — Confirm logging, metrics, and distributed tracing infrastructure. Microservices require correlation IDs and distributed trace propagation from day one.
- **IaC:** TODO — Confirm whether Terraform, Pulumi, CloudFormation, or another tool manages infrastructure. New service infrastructure must be codified in the same toolchain.

---

## Rollback Strategy

Each phase is independently reversible. Rollback must be executable without requiring rollback of a prior phase.

| Phase | Rollback Steps |
|-------|---------------|
| **Phase 1 — Discovery** | Discard decomposition candidate register. No production change has been made. Resume monolith-only operations. |
| **Phase 2 — Routing Layer** | Reconfigure the routing layer to forward 100% of traffic to the monolith. Remove or disable the gateway if it introduced latency or instability. Monolith is unmodified and fully operational. |
| **Phase 3 — Pilot Extraction** | Re-route traffic for the pilot service's endpoints back to the monolith via the routing layer (feature-flag or weighted routing). Re-enable the monolith code path for that bounded context. Migrate any data written to the new service's store back to the monolith schema if writes occurred. Decommission the pilot service container/deployment. |
| **Phase 4 — Incremental Extractions** | Per-service rollback follows the same procedure as Phase 3. Services are extracted independently, so rolling back one does not affect others. Maintain the monolith code path for each bounded context until the extraction is confirmed stable (do not delete monolith code until Phase 5). |
| **Phase 5 — Decommission** | This phase is the point of no return for decommissioned code. Ensure all Phase 4 extractions have been running in production for a defined stability window (TODO: define SLA, e.g., 30 days with no P1 incidents) before executing Phase 5. Use version control history for recovery if needed. |

---

## Testing Strategy

> **TODO:** Specific test frameworks, tools, and coverage thresholds must be confirmed once the language and runtime are identified. The structure below defines the required test pyramid for this decomposition effort.

### Test Pyramid

| Layer | Scope | Tooling | Coverage Target | CI Gate |
|-------|-------|---------|----------------|---------|
| **Unit** | Individual functions/classes within each extracted service and the modified monolith | TODO (language-specific) | TODO (recommend ≥80% line coverage as baseline) | Block merge on failure |
| **Integration** | Service-to-service API contracts; database interactions within each service boundary | TODO (e.g., Testcontainers, WireMock, Pact) | All API contract endpoints covered | Block merge on failure |
| **Contract / Consumer-Driven** | Verify that the extracted service's API fulfills the monolith consumer's expectations during transition | TODO (e.g., Pact, Spring Cloud Contract) | 100% of cross-boundary contracts | Block deployment on failure |
| **Regression** | End-to-end flows that span the routing layer, extracted services, and residual monolith | TODO (e.g., Postman/Newman, Playwright, Karate) | All critical user journeys covered | Block release on failure |
| **Performance / Load** | Validate that extraction has not introduced latency regression; baseline from monolith, compare per extraction | TODO (e.g., k6, Gatling, Locust) | P99 latency ≤ monolith baseline + TODO% | Advisory gate; block on severe regression |

### Additional Testing Requirements
- **Parallel-run validation (Phase 3 & 4):** Shadow traffic or dual-write comparison between monolith and extracted service before full cutover.
- **Data migration testing:** Any schema or data store migration must be validated with a production data clone before execution.
- **Chaos/resilience testing:** TODO — Confirm whether a chaos engineering tool (e.g., Chaos Monkey, Litmus) is available to validate service isolation and circuit-breaker behavior.

---

## Timeline

> **TODO:** Person-days estimates are not available because the upgrade option details were not provided and the tech analysis is incomplete. The milestone structure below must be populated once those inputs are confirmed.

| Milestone | Phase | Estimated Completion | Owner |
|-----------|-------|---------------------|-------|
| Bounded context map and decomposition candidate register complete | Phase 1 | TODO | TODO |
| Routing layer live in production (pass-through) | Phase 2 | TODO | TODO |
| Pilot microservice live and serving production traffic | Phase 3 | TODO | TODO |
| All prioritized bounded contexts extracted | Phase 4 | TODO | TODO |
| Monolith residual decommissioned | Phase 5 | TODO | TODO |

---

## Open TODOs Summary

| # | Item | Blocking Phase |
|---|------|---------------|
| 1 | Complete tech analysis: confirm language, runtime, build tool, frameworks | Phase 1 |
| 2 | Provide codebase context for specific file/class/method identification | Phase 1 |
| 3 | Confirm infrastructure: container strategy, orchestrator, API gateway, CI/CD tooling | Phase 2 |
| 4 | Confirm observability stack for distributed tracing | Phase 2 |
| 5 | Confirm IaC tooling | Phase 2 |
| 6 | Populate dependency version table from completed tech analysis | Phase 3 |
| 7 | Define person-days estimates from upgrade option details | All phases |
| 8 | Define stability window SLA for Phase 5 decommission gate | Phase 5 |
| 9 | Confirm test framework tooling per language/runtime | Phase 3 |
| 10 | Confirm coverage targets and performance regression thresholds | Phase 3 |