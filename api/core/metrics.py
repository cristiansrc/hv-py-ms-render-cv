from __future__ import annotations

import logging
import os
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from api.core.logging import get_logger

logger = get_logger("api.metrics")

# ---- Prometheus Metrics ----

try:
    from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest

    _prometheus_available = True
except ImportError:  # pragma: no cover
    _prometheus_available = False

    # Fallback mock classes when prometheus-client is not installed
    class Counter:  # type: ignore[no-redef]  # pragma: no cover
        def __init__(self, name: str, documentation: str, labelnames: tuple[str, ...] = ()) -> None: ...
        def labels(self, **labelvalues: str) -> "_MockMetric": ...

    class Histogram:  # type: ignore[no-redef]  # pragma: no cover
        def __init__(  # type: ignore[no-redef]
            self, name: str, documentation: str, labelnames: tuple[str, ...] = (), buckets: tuple[float, ...] = ()
        ) -> None: ...
        def labels(self, **labelvalues: str) -> "_MockMetric": ...
        def observe(self, amount: float) -> None: ...

    class _MockMetric:  # pragma: no cover
        def inc(self, increment: float = 1.0) -> None: ...
        def observe(self, amount: float) -> None: ...

    CONTENT_TYPE_LATEST = "text/plain; charset=utf-8"  # pragma: no cover

    def generate_latest() -> bytes:  # pragma: no cover
        return b""

    logger.warning("prometheus-client not installed. Metrics will be no-op.")  # pragma: no cover


# Metric: total render requests
render_requests_total = Counter(
    "render_requests",
    "Total number of render requests",
    labelnames=("status",),
)

# Metric: render duration histogram
RENDER_DURATION_BUCKETS = (0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0)
render_duration_seconds = Histogram(
    "render_duration_seconds",
    "Duration of render requests in seconds",
    labelnames=("status",),
    buckets=RENDER_DURATION_BUCKETS,
)

# Metric: render errors by type
render_errors_total = Counter(
    "render_errors",
    "Total number of render errors by type",
    labelnames=("error_type",),
)


def is_metrics_enabled() -> bool:
    """Check if metrics are enabled via METRICS_ENABLED env var.

    Returns True unless METRICS_ENABLED is explicitly set to 'false' (case-insensitive).
    """
    value = os.environ.get("METRICS_ENABLED", "true").strip().lower()
    return value != "false"


# ---- Metrics Middleware ----

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware that captures request duration for POST /render.

    Only records metrics when METRICS_ENABLED=true.
    Must be placed after TraceMiddleware in the middleware stack.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not is_metrics_enabled():
            return await call_next(request)

        start_time = time.monotonic()
        response: Response | None = None
        exception_raised = False

        try:
            response = await call_next(request)
            return response
        except Exception:
            exception_raised = True
            raise
        finally:
            elapsed = time.monotonic() - start_time

            # Only record metrics for POST /render
            if request.method == "POST" and request.url.path == "/render":
                if exception_raised:
                    render_requests_total.labels(status="error").inc()
                    render_duration_seconds.labels(status="error").observe(elapsed)
                    render_errors_total.labels(error_type="internal_error").inc()
                elif response is not None:
                    status_category = _classify_status(response.status_code)
                    render_requests_total.labels(status=status_category).inc()
                    render_duration_seconds.labels(status=status_category).observe(elapsed)

                    if response.status_code >= 400:
                        error_type = _classify_error(response.status_code)
                        render_errors_total.labels(error_type=error_type).inc()


def _classify_status(status_code: int) -> str:
    """Classify HTTP response status into success or error for metrics."""
    return "success" if status_code < 400 else "error"


def _classify_error(status_code: int) -> str:
    """Classify HTTP status code into error type for metrics."""
    if status_code in (400, 422):
        return "validation_error"
    if status_code < 500:
        return "user_error"
    return "internal_error"
