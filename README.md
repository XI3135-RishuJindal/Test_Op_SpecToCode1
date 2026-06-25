# Observability & Audit Service

This service is responsible for ingesting logs, metrics, and traces from various components,
and provides alerting to maintain system observability and auditing.

## Running the Service

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `python -m observability_audit_service.app`

## Docker

To build and run the service:

1. Build the Docker image: `docker build -t observability-audit-service .`
2. Run the Docker container: `docker run -p 5000:5000 observability-audit-service`

## Configuration

Refer to `.env.example` for configuration options.
