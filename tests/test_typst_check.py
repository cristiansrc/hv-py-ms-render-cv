from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from api.core.typst_check import is_typst_available, reset_typst_cache


@pytest.fixture(autouse=True)
def reset_cache_before_each():
    """Reset typst cache before each test to ensure isolation."""
    reset_typst_cache()
    yield
    reset_typst_cache()


def test_is_typst_available_returns_true_when_typst_exists() -> None:
    """is_typst_available should return True when typst --version succeeds."""
    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("api.core.typst_check.subprocess.run", return_value=mock_result) as mock_run:
        result = is_typst_available()

    assert result is True
    mock_run.assert_called_once_with(
        ["typst", "--version"],
        capture_output=True,
        text=True,
        timeout=5,
    )


def test_is_typst_available_returns_false_when_file_not_found() -> None:
    """is_typst_available should return False when typst is not in PATH."""
    with patch(
        "api.core.typst_check.subprocess.run",
        side_effect=FileNotFoundError("typst not found"),
    ):
        result = is_typst_available()

    assert result is False


def test_is_typst_available_returns_false_on_timeout() -> None:
    """is_typst_available should return False when typst check times out."""
    with patch(
        "api.core.typst_check.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="typst", timeout=5),
    ):
        result = is_typst_available()

    assert result is False


def test_is_typst_available_returns_false_on_permission_error() -> None:
    """is_typst_available should return False when typst has no execute permission."""
    with patch(
        "api.core.typst_check.subprocess.run",
        side_effect=PermissionError("Permission denied"),
    ):
        result = is_typst_available()

    assert result is False


def test_is_typst_available_returns_false_on_nonzero_returncode() -> None:
    """is_typst_available should return False when typst --version fails."""
    mock_result = MagicMock()
    mock_result.returncode = 1

    with patch("api.core.typst_check.subprocess.run", return_value=mock_result):
        result = is_typst_available()

    assert result is False


def test_is_typst_available_caches_result() -> None:
    """is_typst_available should cache the result and not call subprocess again."""
    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("api.core.typst_check.subprocess.run", return_value=mock_result) as mock_run:
        # First call
        result1 = is_typst_available()
        # Second call within cache TTL
        result2 = is_typst_available()

    assert result1 is True
    assert result2 is True
    # subprocess.run should only be called once due to caching
    mock_run.assert_called_once()


def test_reset_typst_cache_forces_fresh_check() -> None:
    """reset_typst_cache should force a fresh subprocess call."""
    mock_result = MagicMock()
    mock_result.returncode = 0

    with patch("api.core.typst_check.subprocess.run", return_value=mock_result) as mock_run:
        # First call
        is_typst_available()
        # Reset cache
        reset_typst_cache()
        # Second call should trigger new subprocess
        is_typst_available()

    # subprocess.run should be called twice (once before reset, once after)
    assert mock_run.call_count == 2
