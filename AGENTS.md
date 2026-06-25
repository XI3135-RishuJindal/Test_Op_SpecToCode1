# AGENTS.md

## Stack

- **Service:** Observability & Audit Service
- **Type:** infrastructure
- **Technologies:**
- OpenTelemetry
- Prometheus/Grafana
- ELK/CloudWatch/Datadog
- Alertmanager/PagerDuty
- **Responsibilities:**
- Ingest logs/metrics/traces from gateway, core, and workers
- Store immutable audit metadata with PII minimization
- Provide alerting for DLQ spikes, outbox lag, and error thresholds
- Enable correlation-based troubleshooting across request/event flows

## General Rules

- Always read files in /specs before implementing
- Never implement without acceptance criteria
- Code should be simple and readable
- Avoid overengineering
- The project follows a hexagonal architecture

## Required Workflow

1. Read the specs in the /specs directory
2. Generate tasks.md if it does not exist
3. Implement based on the tasks
4. Create automated tests
5. Validate acceptance criteria

## Testing

- Cover all acceptance criteria
- Tests should be clear and straightforward
- Generated code must reach **90% unit test coverage**

## Constraints

- Do not invent requirements that are not described
- Do not change behavior without updating the spec
