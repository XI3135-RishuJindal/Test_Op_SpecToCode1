# TASKS: Integrate Micrometer with Prometheus Metrics Export

> **Scope:** Add Micrometer core + Prometheus registry to the application and expose a `/actuator/prometheus` (or equivalent) scrape endpoint.
> **Upgrade Option:** Moderate — instrument existing key components; do not refactor unrelated code.
> **Note:** Language, runtime, and build tool were not provided in the tech analysis. Tasks below are written for the most common host environment (JVM / Spring Boot / Maven or Gradle). Adjust file paths and dependency coordinates if your stack differs.

---

## Prerequisites

- [ ] [XS] Confirm the target runtime, framework version, and build tool by inspecting the project root (`pom.xml`, `build.gradle`, `package.json`, `pyproject.toml`, etc.) and record findings in a `MIGRATION_NOTES.md` file
- [ ] [XS] Verify that a Prometheus scrape target (local Prometheus server or Prometheus-compatible agent) is reachable from the development environment for end-to-end validation
- [ ] [XS] Confirm that the CI pipeline has network access to the central artifact repository (Maven Central / npm / PyPI) needed to resolve Micrometer and Prometheus client packages
- [ ] [XS] Ensure all team members have write access to the feature branch and that branch protection rules allow the required status checks to pass before merge

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch `feature/micrometer-prometheus` from the main integration branch
- [ ] [S] Audit existing dependency manifest (`pom.xml` / `build.gradle` / equivalent) for any pre-existing metrics libraries (Dropwizard Metrics, Spring Boot Actuator without Micrometer, Prometheus `simpleclient`, etc.) that may conflict with Micrometer, and document conflicts in `MIGRATION_NOTES.md`
- [ ] [XS] Capture the current application startup log and any existing `/metrics` or `/health` endpoint responses as a baseline snapshot in `test/baseline/metrics_baseline.txt`
- [ ] [XS] Add a CI gate (in the existing pipeline config file) that fails the build if Micrometer or `micrometer-registry-prometheus` dependencies are removed or downgraded below the agreed version

---

## Phase 2 — Core Upgrade

- [ ] [M] Add `micrometer-core` and `micrometer-registry-prometheus` dependencies at their latest stable versions to the build manifest (`pom.xml` or `build.gradle`), pinning exact versions in a `<dependencyManagement>` block or `ext` block to prevent transitive version drift
- [ ] [S] Configure a `PrometheusMeterRegistry` bean (or equivalent registry factory) in the application configuration file (e.g., `src/main/resources/application.yml` or a `MetricsConfig` class), setting `management.metrics.export.prometheus.enabled=true` and `management.endpoints.web.exposure.include=prometheus`
- [ ] [S] Expose the Prometheus scrape endpoint — verify `/actuator/prometheus` returns `text/plain; version=0.0.4` content type, or wire a dedicated `/metrics` route if the framework does not use Spring Actuator
- [ ] [M] Instrument the application's primary inbound request path (e.g., the main HTTP filter, controller advice, or middleware) with `Timer` and `Counter` meters using `MeterRegistry` injection, recording request count and latency by HTTP method and status code
- [ ] [S] Instrument any existing background jobs, scheduled tasks, or message consumers identified in the codebase with `Timer` meters so their execution duration is captured
- [ ] [XS] Add common JVM and system metrics by registering `JvmMetrics`, `ProcessorMetrics`, and `UptimeMetrics` binders (or their framework equivalents) in the `MetricsConfig` class
- [ ] [XS] Set a global `commonTags` configuration (e.g., `application`, `environment`) on the `MeterRegistry` in `MetricsConfig` so every metric carries consistent label dimensions

---

## Phase 3 — Testing & Validation

- [ ] [M] Write an integration test (e.g., `PrometheusEndpointIT.java` or equivalent) that starts the application context, hits the scrape endpoint, and asserts that `jvm_memory_used_bytes`, `process_uptime_seconds`, and at least one application-level `http_server_requests` metric are present in the response
- [ ] [S] Write unit tests for each newly instrumented component (HTTP filter / middleware, background jobs) using `SimpleMeterRegistry` to assert that the expected meters are registered and incremented on execution
- [ ] [XS] Compare the live scrape output against `test/baseline/metrics_baseline.txt` and confirm no previously existing metrics have been removed or renamed without a documented reason in `MIGRATION_NOTES.md`
- [ ] [XS] Validate that the Prometheus scrape endpoint returns HTTP 200 and well-formed Prometheus exposition format by running `promtool check metrics <(curl -s http://localhost:8080/actuator/prometheus)` locally and recording the result

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Update the CI pipeline configuration file to add a post-startup smoke-test step that curls `/actuator/prometheus` and asserts HTTP 200, failing the build if the endpoint is unavailable
- [ ] [XS] Add or update the `Dockerfile` (if present) to ensure port `8080` (or the configured management port) is `EXPOSE`d so Prometheus can scrape the containerised application
- [ ] [XS] Add or update the Prometheus scrape config (`prometheus.yml` or the relevant service-discovery annotation/label block) with a new job entry targeting the application's scrape endpoint, including correct `metrics_path` and `scrape_interval`
- [ ] [XS] Verify that no firewall rules or Kubernetes `NetworkPolicy` resources block traffic from the Prometheus server to the application's management port, and document any required changes in `MIGRATION_NOTES.md`

---

## Phase 5 — Documentation & Rollout

- [ ] [XS] Add a `CHANGELOG.md` entry under an `[Unreleased]` heading describing the Micrometer + Prometheus integration, listing new endpoint URL, added metric names, and common tag keys
- [ ] [S] Update (or create) a `docs/observability/metrics.md` runbook documenting: scrape endpoint URL, all registered meter names and their labels, how to add new meters, and how to query key metrics in PromQL
- [ ] [XS] Deploy to the staging environment and confirm that the Prometheus server successfully scrapes the application by checking `up{job="<app-job-name>"}` equals `1` in the Prometheus UI
- [ ] [XS] Set up a basic Prometheus alerting rule (in the existing `alerts.yml` or equivalent) for `up{job="<app-job-name>"} == 0` to detect scrape failures post-rollout
- [ ] [XS] Schedule a 48-hour post-production-deployment review to inspect scrape success rate, cardinality of new metrics, and any unexpected label explosion, and record findings in `MIGRATION_NOTES.md`