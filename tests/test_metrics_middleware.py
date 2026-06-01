from __future__ import annotations

import pytest
from prometheus_client import REGISTRY

from api.core.metrics import (
    _classify_error,
    _classify_status,
    MetricsMiddleware,
    render_duration_seconds,
    render_errors_total,
    render_requests_total,
)


def _counter_value(name: str, labels: dict[str, str] | None = None) -> float:
    """Get the current value of a Counter metric."""
    full_sample_name = name + "_total"
    for metric in REGISTRY.collect():
        if metric.name == name:
            for sample in metric.samples:
                if sample.name == full_sample_name:
                    if labels is None:
                        return sample.value
                    match = all(
                        sample.labels.get(k) == v for k, v in labels.items()
                    )
                    if match:
                        return sample.value
    return 0.0


def _histogram_count(name: str, labels: dict[str, str] | None = None) -> float:
    """Get the count of a Histogram metric."""
    full_sample_name = name + "_count"
    for metric in REGISTRY.collect():
        if metric.name == name:
            for sample in metric.samples:
                if sample.name == full_sample_name:
                    if labels is None:
                        return sample.value
                    match = all(
                        sample.labels.get(k) == v for k, v in labels.items()
                    )
                    if match:
                        return sample.value
    return 0.0


class TestMetricsMiddlewareExceptionPath:
    """Tests for MetricsMiddleware exception handling path (lines 103-105, 112-114)."""

    @pytest.mark.asyncio
    async def test_middleware_records_metrics_on_exception(self) -> None:
        """MetricsMiddleware should record error metrics when exception is raised."""
        from unittest.mock import AsyncMock, MagicMock
        from starlette.requests import Request
        from starlette.responses import Response

        baseline_errors = _counter_value("render_errors", {"error_type": "internal_error"})
        baseline_error_requests = _counter_value("render_requests", {"status": "error"})
        baseline_duration = _histogram_count("render_duration_seconds", {"status": "error"})

        middleware = MetricsMiddleware(app=None)

        mock_request = MagicMock(spec=Request)
        mock_request.method = "POST"
        mock_request.url.path = "/render"

        async def raise_exception(request):
            raise RuntimeError("Simulated failure")

        with pytest.raises(RuntimeError, match="Simulated failure"):
            await middleware.dispatch(mock_request, raise_exception)

        # Verify metrics were incremented despite the exception
        new_errors = _counter_value("render_errors", {"error_type": "internal_error"})
        assert new_errors > baseline_errors, (
            f"Expected render_errors_total{{error_type='internal_error'}} to increase "
            f"(baseline={baseline_errors}, new={new_errors})"
        )

        new_error_requests = _counter_value("render_requests", {"status": "error"})
        assert new_error_requests > baseline_error_requests, (
            f"Expected render_requests{{status='error'}} to increase "
            f"(baseline={baseline_error_requests}, new={new_error_requests})"
        )

        new_duration = _histogram_count("render_duration_seconds", {"status": "error"})
        assert new_duration > baseline_duration, (
            f"Expected render_duration_seconds_count{{status='error'}} to increase "
            f"(baseline={baseline_duration}, new={new_duration})"
        )


class TestClassifyErrorEdgeCases:
    """Additional tests for _classify_error to cover all branches."""

    def test_user_error_for_405(self) -> None:
        """405 should be classified as user_error."""
        assert _classify_error(405) == "user_error"

    def test_user_error_for_429(self) -> None:
        """429 should be classified as user_error."""
        assert _classify_error(429) == "user_error"

    def test_internal_error_for_501(self) -> None:
        """501 should be classified as internal_error."""
        assert _classify_error(501) == "internal_error"

    def test_internal_error_for_504(self) -> None:
        """504 should be classified as internal_error."""
        assert _classify_error(504) == "internal_error"


class TestClassifyStatusEdgeCases:
    """Additional tests for _classify_status to cover all branches."""

    def test_success_for_302(self) -> None:
        """302 should be classified as success."""
        assert _classify_status(302) == "success"

    def test_success_for_399(self) -> None:
        """399 should be classified as success."""
        assert _classify_status(399) == "success"

    def test_error_for_400_boundary(self) -> None:
        """400 should be classified as error."""
        assert _classify_status(400) == "error"

    def test_error_for_599(self) -> None:
        """599 should be classified as error."""
        assert _classify_status(599) == "error"
