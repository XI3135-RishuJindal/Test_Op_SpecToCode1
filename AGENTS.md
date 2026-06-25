```markdown
# AGENTS.md

## Observability & Audit Service Scaffold

### Stack

- **OpenTelemetry:** Used for distributed tracing and metrics collection. 
- **Prometheus/Grafana:** Prometheus for metrics scraping and storage; Grafana for dashboard visualizations.
- **ELK (Elasticsearch, Logstash, Kibana)/CloudWatch/Datadog:** Log aggregation and analysis; choose one based on deployment environment and existing infrastructure.
- **Alertmanager/PagerDuty:** Alerting mechanism for monitoring significant metrics/events.

### Project Structure

```
observability-audit-service/
├── config/                      # Configuration files for all components
│   ├── prometheus.yml           # Prometheus configuration
│   ├── alertmanager.yml         # Alertmanager configuration
│   └── opentelemetry-config.yml # OpenTelemetry collectors and exporters config
├── docker/                      # Docker-related files
│   ├── Dockerfile               # Dockerfile for containerizing the service
│   └── docker-compose.yml       # Docker Compose setup for local infrastructure
├── src/                         # Source code
│   ├── main/                    # Primary application logic
│   └── test/                    # Test suites
├── dashboards/                  # Preconfigured Grafana dashboards
└── .github/                     # GitHub CI/CD configuration
    └── workflows/
        └── ci.yml              # Continuous Integration workflow
```

### Required Workflow

1. **Read Specs:** Review all project and feature specifications provided.
2. **Create tasks.md:** Break down the specs into actionable tasks and document them in `tasks.md`.
3. **Implement:** Begin coding based on tasks, ensuring compliance with coding conventions and integration needs.
4. **Test:** Execute unit and integration tests, aiming for 90%+ code coverage.
5. **Validate:** Conduct manual and automated validations, verifying expected outputs.

### Coding Conventions

- **Naming:** Use `camelCase` for variables and methods, `PascalCase` for class names, and `SCREAMING_SNAKE_CASE` for environment variables.
- **Style:** Follow PEP 8 (Python) or other relevant guidelines for your chosen programming language(s).
- **Architecture Patterns:** Utilize microservices architecture, with clear separation between log ingestion, storage, and alerting services.

### Testing

- **Unit Testing:** Target core logic functions with unit tests. Aim for at least 90% coverage.
- **Integration Testing:** Verify interoperability between OpenTelemetry, Prometheus, Grafana, and the ES/CloudWatch/Datadog stack.
- **Testing Frameworks:** Prefer industry-standard tools such as PyTest (Python), JUnit (Java) depending on your source language.
- **Run Tests:** Execute via `docker-compose` to simulate production-like environments.

### Docker & CI

- **Dockerfile:** 
  ```Dockerfile
  FROM appropriate-base-image
  COPY . /app
  WORKDIR /app
  RUN install_dependencies_script
  CMD ["run_main_service_script"]
  ```

- **docker-compose.yml:**
  ```yaml
  version: '3.8'
  services:
    prometheus:
      image: prom/prometheus
      volumes:
        - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
    grafana:
      image: grafana/grafana
    app:
      build: .
      depends_on:
        - prometheus
        - grafana
  ```

- **CI Pipeline (GitHub Actions):** `.github/workflows/ci.yml` 
  ```yaml
  name: CI

  on:
    push:
      branches: [main]
    pull_request:
      branches: [main]

  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v2
        - name: Build Docker containers
          run: docker-compose -f docker/docker-compose.yml up --build
        - name: Run tests
          run: run_test_script
        - name: Upload code coverage
          uses: codecov/codecov-action@v2
  ```

### Constraints

- **No PII Storage:** Ensure logs and metrics do not contain sensitive PII.
- **Immutable Audit Trails:** Audit logs must remain unchanged post-entry.
- **Alerting Thresholds:** Alerting for DLQ spikes, outbox lag, and error thresholds must be maintained rigorously.
- **Correlation Capabilities:** Enable end-to-end traceability across all services.
```
