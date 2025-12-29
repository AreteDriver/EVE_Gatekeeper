"""Prometheus metrics endpoint."""

from fastapi import APIRouter, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

from ..core.config import settings

router = APIRouter()

# =============================================================================
# HTTP Metrics
# =============================================================================

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0),
)

# =============================================================================
# Cache Metrics
# =============================================================================

CACHE_HITS = Counter(
    "cache_hits_total",
    "Total cache hits",
    ["cache_type"],
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total cache misses",
    ["cache_type"],
)

# =============================================================================
# ESI Metrics
# =============================================================================

ESI_REQUESTS_TOTAL = Counter(
    "esi_requests_total",
    "Total ESI API requests",
    ["endpoint", "status"],
)

# =============================================================================
# WebSocket Metrics
# =============================================================================

WEBSOCKET_CONNECTIONS = Gauge(
    "websocket_connections_active",
    "Active WebSocket connections",
)

# =============================================================================
# Application Metrics
# =============================================================================

ROUTE_CALCULATIONS = Counter(
    "route_calculations_total",
    "Total route calculations",
    ["profile"],
)

RISK_CALCULATIONS = Counter(
    "risk_calculations_total",
    "Total risk score calculations",
)

ZKILL_EVENTS = Counter(
    "zkill_events_total",
    "Total zKillboard events received",
    ["event_type"],
)

# =============================================================================
# Info Metric
# =============================================================================

INFO = Gauge(
    "eve_gatekeeper_info",
    "Application information",
    ["version"],
)
INFO.labels(version=settings.API_VERSION).set(1)


@router.get("/metrics", include_in_schema=False)
async def metrics() -> Response:
    """
    Prometheus metrics endpoint.

    Returns metrics in Prometheus text format for scraping.
    """
    if not settings.METRICS_ENABLED:
        return Response(content="Metrics disabled", status_code=404)

    return Response(
        content=generate_latest(REGISTRY),
        media_type=CONTENT_TYPE_LATEST,
    )


# =============================================================================
# Helper Functions for Recording Metrics
# =============================================================================


def record_http_request(method: str, path: str, status: int, duration: float) -> None:
    """Record an HTTP request."""
    # Normalize path to avoid high cardinality
    normalized_path = normalize_path(path)
    HTTP_REQUESTS_TOTAL.labels(method=method, path=normalized_path, status=status).inc()
    HTTP_REQUEST_DURATION.labels(method=method, path=normalized_path).observe(duration)


def normalize_path(path: str) -> str:
    """Normalize path to reduce cardinality (replace IDs with placeholders)."""
    import re
    # Replace numeric IDs
    path = re.sub(r"/\d+", "/{id}", path)
    # Replace UUIDs
    path = re.sub(
        r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        "/{uuid}",
        path,
        flags=re.IGNORECASE,
    )
    return path


def record_cache_hit(cache_type: str = "memory") -> None:
    """Record a cache hit."""
    CACHE_HITS.labels(cache_type=cache_type).inc()


def record_cache_miss(cache_type: str = "memory") -> None:
    """Record a cache miss."""
    CACHE_MISSES.labels(cache_type=cache_type).inc()


def record_esi_request(endpoint: str, status: int) -> None:
    """Record an ESI API request."""
    ESI_REQUESTS_TOTAL.labels(endpoint=endpoint, status=status).inc()


def record_route_calculation(profile: str) -> None:
    """Record a route calculation."""
    ROUTE_CALCULATIONS.labels(profile=profile).inc()


def record_risk_calculation() -> None:
    """Record a risk calculation."""
    RISK_CALCULATIONS.inc()


def record_zkill_event(event_type: str = "kill") -> None:
    """Record a zKillboard event."""
    ZKILL_EVENTS.labels(event_type=event_type).inc()


def set_websocket_connections(count: int) -> None:
    """Set the current number of WebSocket connections."""
    WEBSOCKET_CONNECTIONS.set(count)
