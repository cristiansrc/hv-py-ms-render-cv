from __future__ import annotations

import subprocess
import time
from collections.abc import Callable
from functools import wraps

from api.core.logging import get_logger

logger = get_logger("api.typst_check")

# Cache state
_last_check: float = 0.0
_last_result: bool = False
CACHE_TTL: float = 30.0  # seconds


def is_typst_available() -> bool:
    """Check if Typst is available in the PATH.

    Result is cached for CACHE_TTL seconds to avoid excessive subprocess calls.
    """
    global _last_check, _last_result

    now = time.monotonic()
    if now - _last_check < CACHE_TTL:
        return _last_result

    _last_check = now

    try:
        result = subprocess.run(
            ["typst", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        available = result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError) as e:
        logger.warning("Typst check failed: %s", e)
        available = False

    _last_result = available
    logger.info("Typst available=%s", available)
    return available


def reset_typst_cache() -> None:
    """Reset the cached Typst availability result.

    Useful for testing to force a fresh check.
    """
    global _last_check, _last_result
    _last_check = 0.0
    _last_result = False
