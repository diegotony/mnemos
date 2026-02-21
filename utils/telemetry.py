"""
OpenTelemetry configuration for Mnemos.
Provides structured logging, tracing, and metrics.
"""

import os
import logging
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter


# Configuración desde environment
OTEL_ENABLED = os.getenv("OTEL_ENABLED", "false").lower() == "true"
OTEL_SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "mnemos")
OTEL_EXPORTER_ENDPOINT = os.getenv(
    "OTEL_EXPORTER_ENDPOINT", None
)  # e.g., "http://localhost:4317"
OTEL_ENVIRONMENT = os.getenv("OTEL_ENVIRONMENT", "development")


def setup_opentelemetry():
    """
    Configura OpenTelemetry para tracing, metrics, y logging.

    Returns:
        Tuple of (tracer, meter, logger)
    """
    if not OTEL_ENABLED:
        logging.info("📊 OpenTelemetry disabled (OTEL_ENABLED=false)")
        return None, None, None

    # Resource: información sobre el servicio
    resource = Resource.create(
        {
            "service.name": OTEL_SERVICE_NAME,
            "service.version": "1.0.0",
            "deployment.environment": OTEL_ENVIRONMENT,
        }
    )

    # ==================== TRACING ====================

    trace_provider = TracerProvider(resource=resource)

    if OTEL_EXPORTER_ENDPOINT:
        # OTLP exporter (para enviar a Jaeger, Honeycomb, etc.)
        otlp_span_exporter = OTLPSpanExporter(endpoint=OTEL_EXPORTER_ENDPOINT)
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_span_exporter))
        logging.info(f"📤 OTLP Span Exporter configured: {OTEL_EXPORTER_ENDPOINT}")
    else:
        # Console exporter (para desarrollo)
        console_span_exporter = ConsoleSpanExporter()
        trace_provider.add_span_processor(BatchSpanProcessor(console_span_exporter))
        logging.info("🖥️  Console Span Exporter configured (development)")

    trace.set_tracer_provider(trace_provider)
    tracer = trace.get_tracer(__name__)

    # ==================== METRICS ====================

    if OTEL_EXPORTER_ENDPOINT:
        metric_reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=OTEL_EXPORTER_ENDPOINT)
        )
        logging.info(f"📤 OTLP Metric Exporter configured: {OTEL_EXPORTER_ENDPOINT}")
    else:
        metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter())
        logging.info("🖥️  Console Metric Exporter configured (development)")

    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    meter = metrics.get_meter(__name__)

    # ==================== LOGGING ====================

    logger_provider = LoggerProvider(resource=resource)

    if OTEL_EXPORTER_ENDPOINT:
        # OTLP log exporter (aún experimental)
        logging.info(f"📤 OTLP Logs would be sent to: {OTEL_EXPORTER_ENDPOINT}")
        # Note: OTLP log exporter not yet stable, using console for now
        console_log_exporter = ConsoleLogExporter()
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(console_log_exporter)
        )
    else:
        console_log_exporter = ConsoleLogExporter()
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(console_log_exporter)
        )
        logging.info("🖥️  Console Log Exporter configured (development)")

    set_logger_provider(logger_provider)

    # Agregar handler de OpenTelemetry al logger de Python
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)

    logging.info(f"✅ OpenTelemetry configured for service: {OTEL_SERVICE_NAME}")

    return tracer, meter, logger_provider


def instrument_fastapi(app):
    """
    Instrumenta una aplicación FastAPI con OpenTelemetry.

    Args:
        app: Instancia de FastAPI
    """
    if not OTEL_ENABLED:
        return

    FastAPIInstrumentor.instrument_app(app)
    logging.info("🎯 FastAPI instrumented with OpenTelemetry")


# Singleton instances
_tracer = None
_meter = None
_logger_provider = None


def get_tracer():
    """Obtiene el tracer de OpenTelemetry."""
    global _tracer
    if _tracer is None:
        _tracer, _, _ = setup_opentelemetry()
    return _tracer


def get_meter():
    """Obtiene el meter de OpenTelemetry."""
    global _meter
    if _meter is None:
        _, _meter, _ = setup_opentelemetry()
    return _meter


# ==================== CUSTOM METRICS ====================


def create_custom_meters():
    """
    Crea meters personalizados para métricas de negocio.

    Returns:
        Dict con counters y histograms
    """
    if not OTEL_ENABLED:
        return {}

    meter = get_meter()

    return {
        # Counters
        "events_synced": meter.create_counter(
            "mnemos.events.synced",
            description="Number of events synced from Google Calendar",
            unit="1",
        ),
        "events_created": meter.create_counter(
            "mnemos.events.created",
            description="Number of events created locally",
            unit="1",
        ),
        "events_updated": meter.create_counter(
            "mnemos.events.updated",
            description="Number of events updated",
            unit="1",
        ),
        "events_deleted": meter.create_counter(
            "mnemos.events.deleted",
            description="Number of events deleted",
            unit="1",
        ),
        # Histograms
        "event_duration": meter.create_histogram(
            "mnemos.events.duration",
            description="Duration of events in hours",
            unit="hours",
        ),
        "sync_duration": meter.create_histogram(
            "mnemos.sync.duration",
            description="Time taken to sync events",
            unit="seconds",
        ),
    }


# Inicializar custom meters
custom_meters = create_custom_meters()
