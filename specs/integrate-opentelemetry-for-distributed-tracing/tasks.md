# Tasks: Integrate OpenTelemetry for Distributed Tracing

> **Scope:** Add OpenTelemetry instrumentation for distributed tracing.
> **Upgrade Option:** Moderate
> **Note:** Language, runtime, and build tooling were not specified in the tech analysis. Tasks below are written at the logical/conceptual level. Once the stack is confirmed, file paths and package names must be substituted with actuals before assigning to an agent.

---

## Prerequisites

- [ ] [XS] Confirm target language, runtime version, and build tool by inspecting the repository root (e.g., `package.json`, `pom.xml`, `go.mod`, `requirements.txt`, `Cargo.toml`) and record findings in a pinned issue or ADR file
- [ ] [XS] Confirm the OpenTelemetry SDK stable release for the identified language at [opentelemetry.io/docs](https://opentelemetry.io/docs/) and record the exact version to be adopted
- [ ] [XS] Verify access to the target observability backend (e.g., Jaeger, Tempo, OTLP-compatible collector) and obtain the collector endpoint URL and any required auth credentials, storing them as CI/CD secrets
- [ ] [XS] Confirm that the team has write access to the application repository, the CI/CD pipeline configuration, and the infrastructure/deployment config files

---

## Phase 1 — Preparation

- [ ] [XS] Create a dedicated feature branch (e.g., `feat/opentelemetry-tracing`) from the main branch for all tracing integration work
- [ ] [S] Audit existing logging and monitoring dependencies in the build manifest (e.g., `package.json`, `pom.xml`, `go.mod`) to identify conflicts or overlapping instrumentation libraries that must be removed or reconciled before adding OpenTelemetry
- [ ] [S] Capture a pre-integration test baseline by running the full existing test suite and saving the results (pass/fail counts, coverage report) as a reference artifact in the repository (e.g., `docs/test-baseline-pre-otel.md`)
- [ ] [XS] Define and document the minimum tracing coverage requirement (e.g., all inbound HTTP requests, outbound HTTP calls, and database queries must produce spans) in a new ADR file (e.g., `docs/adr/0001-opentelemetry-tracing.md`)
- [ ] [XS] Configure a CI gate that fails the build if the OpenTelemetry SDK dependency is absent or if the tracer provider is not initialized, using a lint or startup-check mechanism appropriate to the identified runtime

---

## Phase 2 — Core Upgrade

- [ ] [M] Add the OpenTelemetry SDK and API packages (core, trace, context-propagation) to the build manifest at the confirmed stable version, ensuring no duplicate or conflicting telemetry libraries remain
- [ ] [M] Create a tracer provider initialization module (e.g., `src/telemetry/tracer.{ext}`) that configures the OTLP exporter, sets the service name via the `OTEL_SERVICE_NAME` environment variable, and registers the global tracer provider at application startup
- [ ] [M] Instrument all inbound HTTP request handlers to start and end root spans, attach standard HTTP semantic attributes (`http.method`, `http.route`, `http.status_code`), and propagate trace context from incoming headers using the W3C TraceContext propagator
- [ ] [M] Instrument all outbound HTTP client calls to create child spans, inject trace context into outgoing headers, and record `http.url` and `http.status_code` attributes
- [ ] [S] Instrument database query execution points to create child spans with `db.system`, `db.statement`, and `db.name` attributes, ensuring no sensitive data is captured in span attributes
- [ ] [S] Wire the tracer provider initialization module into the application entry point (e.g., `src/main.{ext}`, `src/app.{ext}`) so the provider is registered before any request handling begins
- [ ] [S] Add `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, and `OTEL_TRACES_SAMPLER` to the application environment configuration (e.g., `.env.example`, `config/env.yaml`) with documented default values and instructions for local development

---

## Phase 3 — Testing & Validation

- [ ] [M] Write unit tests for the tracer provider initialization module (e.g., `src/telemetry/tracer.test.{ext}`) verifying that the provider registers successfully, the OTLP exporter is configured with the correct endpoint, and the service name is read from the environment variable
- [ ] [M] Write integration tests for the instrumented HTTP handlers verifying that a root span is created per request, trace context is propagated in responses, and span attributes match the HTTP semantic conventions
- [ ] [S] Write integration tests for the instrumented outbound HTTP client verifying that child spans are created and trace context headers (`traceparent`, `tracestate`) are injected into outgoing requests
- [ ] [S] Run the full test suite and compare results against the pre-integration baseline captured in `docs/test-baseline-pre-otel.md`; document any regressions and resolve before merging
- [ ] [S] Perform a manual end-to-end validation in a staging environment by triggering representative user flows and confirming complete traces appear in the observability backend with correct parent-child span relationships and no missing spans

---

## Phase 4 — CI/CD & Infrastructure

- [ ] [S] Add `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, and `OTEL_TRACES_SAMPLER` as secrets or environment variables in the CI/CD pipeline configuration file (e.g., `.github/workflows/ci.yml`, `Jenkinsfile`, `.gitlab-ci.yml`) for staging and production environments
- [ ] [S] Update the application's deployment configuration (e.g., `docker-compose.yml`, Kubernetes `Deployment` manifest, or equivalent) to pass the required `OTEL_*` environment variables to the application container and, if self-hosted, to include an OpenTelemetry Collector sidecar or service definition
- [ ] [XS] Verify that the OpenTelemetry Collector (or managed OTLP endpoint) is reachable from the application's network context in staging and that the CI pipeline includes a connectivity smoke-test step

---

## Phase 5 — Documentation & Rollout

- [ ] [S] Update `CHANGELOG.md` with an entry describing the OpenTelemetry integration, the instrumented surfaces (HTTP in/out, database), the required environment variables, and the target observability backend
- [ ] [S] Update the developer runbook (e.g., `docs/runbook.md` or `README.md`) with instructions for running the application locally with tracing enabled, how to view traces in the local/staging backend, and how to add new spans for future instrumentation
- [ ] [XS] Configure an alert or dashboard in the observability backend to monitor trace ingestion rate and error span rate as post-migration health signals, and document the alert thresholds in `docs/runbook.md`
- [ ] [XS] Conduct a staged rollout by enabling tracing in staging first, validating trace data for 24 hours, then promoting to production with the `OTEL_TRACES_SAMPLER` set to a conservative sampling rate (e.g., `parentbased_traceidratio` at `0.1`) before increasing to the target rate