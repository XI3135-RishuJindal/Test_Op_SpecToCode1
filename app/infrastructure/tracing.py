"""
OpenTelemetry tracing setup for the API Gateway / BFF Service.

Configures an OTLP gRPC exporter when OTEL_EXPORTER_OTLP_ENDPOINT is set,
otherwise falls back to a no-op tracer so the service runs without a
collector in development.
"""
from __future__ import annotations

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from app.infrastructure.logging import get_logger

logger = get_logger(__name__)


def configure_tracing(service_name: str, otlp_endpoint: str = "") -> None:
    """Initialise the global OpenTelemetry TracerProvider.

    Args:
        service_name: Value for the ``service.name`` resource attribute.
        otlp_endpoint: OTLP gRPC endpoint (e.g. ``http://otel-collector:4317``).
                       When empty, a console exporter is used in development.
    """
    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    if otlp_endpoint:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )

            exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
            provider.add_span_processor(BatchSpanProcessor(exporter))
            logger.info("otel_tracing_configured", extra={"endpoint": otlp_endpoint})
        except ImportError:
            logger.warning(
                "otel_otlp_exporter_unavailable",
                extra={"reason": "opentelemetry-exporter-otlp not installed"},
            )
    else:
        # Development: emit spans to stdout so they are visible without a collector
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        logger.info("otel_tracing_configured", extra={"exporter": "console"})

    trace.set_tracer_provider(provider)


def get_tracer(name: str) -> trace.Tracer:
    """Return a named tracer from the global provider."""
    return trace.get_tracer(name)
