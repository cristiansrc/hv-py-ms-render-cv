from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from api.core.errors import (
    fallback_exception_handler,
    rendercv_internal_error_handler,
    rendercv_user_error_handler,
    rendercv_user_validation_error_handler,
    validation_error_handler,
)
from api.core.logging import setup_logging
from api.core.metrics import MetricsMiddleware
from api.core.trace import TraceMiddleware
from api.routers.health import router as health_router
from api.routers.metrics import router as metrics_router
from api.routers.render import router as render_router
from rendercv.exception import (
    RenderCVInternalError,
    RenderCVUserError,
    RenderCVUserValidationError,
)

# Configure structured logging
setup_logging()


def create_app() -> FastAPI:
    app = FastAPI(
        title="hv-py-ms-render-cv API",
        version=os.environ.get("APP_VERSION", "1.0.0"),
        description="Microservicio de generación de PDFs ATS-friendly para CVs.",
    )

    # Middleware (order matters: trace first, then metrics)
    app.add_middleware(TraceMiddleware)
    app.add_middleware(MetricsMiddleware)

    # Routers
    app.include_router(render_router)
    app.include_router(health_router)
    app.include_router(metrics_router)

    # Exception handlers (most specific first)
    app.add_exception_handler(
        RequestValidationError,
        validation_error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        RenderCVUserValidationError,
        rendercv_user_validation_error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        RenderCVUserError,
        rendercv_user_error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(
        RenderCVInternalError,
        rendercv_internal_error_handler,  # type: ignore[arg-type]
    )
    app.add_exception_handler(Exception, fallback_exception_handler)

    return app


app = create_app()
