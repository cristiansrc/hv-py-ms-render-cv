from __future__ import annotations

import os
from typing import Any
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from prometheus_client import REGISTRY

from api.core.metrics import render_duration_seconds, render_errors_total, render_requests_total


def _sample_value(
    metric_name: str, sample_suffix: str, labels: dict[str, str] | None = None
) -> float:
    """Get the value of a specific sample from the Prometheus registry.

    Args:
        metric_name: The name of the metric (e.g. 'render_requests').
        sample_suffix: The suffix to append (e.g. '_total', '_count', '_sum').
        labels: Optional dict of label filters.
    """
    full_sample_name = metric_name + sample_suffix
    for metric in REGISTRY.collect():
        if metric.name == metric_name:
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


def _counter_value(name: str, labels: dict[str, str] | None = None) -> float:
    """Get the current value of a Counter metric."""
    return _sample_value(name, "_total", labels)


def _histogram_count(name: str, labels: dict[str, str] | None = None) -> float:
    """Get the count of a Histogram metric."""
    return _sample_value(name, "_count", labels)


VALID_CV_PAYLOAD: dict[str, Any] = {
    "cv": {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "sections": {
            "experience": [
                {
                    "company": "Acme Corp",
                    "position": "Senior Engineer",
                    "start_date": "2023-01",
                    "end_date": "present",
                }
            ]
        },
        "locale": {"language": "english"},
        "design": {"theme": "engineeringclassic"},
    }
}


@pytest.mark.asyncio
async def test_metrics_endpoint_returns_200(client: AsyncClient) -> None:
    """GET /metrics should return 200 with Prometheus content type."""
    response = await client.get("/metrics")

    assert response.status_code == 200
    assert response.headers.get("content-type", "").startswith("text/plain")


@pytest.mark.asyncio
async def test_metrics_returns_503_when_disabled(client: AsyncClient) -> None:
    """GET /metrics should return 503 when METRICS_ENABLED=false."""
    with patch.dict(os.environ, {"METRICS_ENABLED": "false"}, clear=False):
        response = await client.get("/metrics")

    assert response.status_code == 503
    assert response.text == "Metrics disabled"
    assert response.headers.get("content-type", "").startswith("text/plain")


@pytest.mark.asyncio
async def test_render_requests_total_increments(client: AsyncClient) -> None:
    """POST /render should increment render_requests counter."""
    baseline = _counter_value("render_requests", {"status": "success"})

    with patch(
        "api.routers.render.render_pdf_base64",
        return_value="JVBERi0xLjQKfakebase64",
    ):
        response = await client.post("/render", json=VALID_CV_PAYLOAD)

    assert response.status_code == 200

    new_value = _counter_value("render_requests", {"status": "success"})
    assert new_value > baseline, (
        f"Expected render_requests_total{{status='success'}} to increase "
        f"(baseline={baseline}, new={new_value})"
    )


@pytest.mark.asyncio
async def test_render_errors_total_increments_on_validation_error(
    client: AsyncClient,
) -> None:
    """Failed POST /render (validation error) should increment error counter."""
    baseline_errors = _counter_value("render_errors", {"error_type": "validation_error"})
    baseline_error_requests = _counter_value("render_requests", {"status": "error"})

    response = await client.post("/render", json={})

    assert response.status_code == 400

    new_errors = _counter_value("render_errors", {"error_type": "validation_error"})
    assert new_errors > baseline_errors, (
        f"Expected render_errors_total{{error_type='validation_error'}} to increase "
        f"(baseline={baseline_errors}, new={new_errors})"
    )

    new_error_requests = _counter_value("render_requests", {"status": "error"})
    assert new_error_requests > baseline_error_requests, (
        f"Expected render_requests{{status='error'}} to increase "
        f"(baseline={baseline_error_requests}, new={new_error_requests})"
    )


@pytest.mark.asyncio
async def test_render_duration_seconds_records(client: AsyncClient) -> None:
    """POST /render should record duration in histogram."""
    baseline = _histogram_count("render_duration_seconds", {"status": "success"})

    with patch(
        "api.routers.render.render_pdf_base64",
        return_value="JVBERi0xLjQKfakebase64",
    ):
        response = await client.post("/render", json=VALID_CV_PAYLOAD)

    assert response.status_code == 200

    new_count = _histogram_count("render_duration_seconds", {"status": "success"})
    assert new_count > baseline, (
        f"Expected render_duration_seconds_count{{status='success'}} to increase "
        f"(baseline={baseline}, new={new_count})"
    )


@pytest.mark.asyncio
async def test_metrics_contains_expected_metrics(client: AsyncClient) -> None:
    """GET /metrics body should contain expected metric names."""
    response = await client.get("/metrics")
    content = response.text

    assert "render_requests_total" in content
    assert "render_duration_seconds" in content
    assert "render_errors_total" in content
