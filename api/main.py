from fastapi import FastAPI

from api.core.errors import (
    rendercv_internal_error_handler,
    rendercv_user_error_handler,
    rendercv_user_validation_error_handler,
)
from api.routers.render import router as render_router
from rendercv.exception import (
    RenderCVInternalError,
    RenderCVUserError,
    RenderCVUserValidationError,
)


def create_app() -> FastAPI:
    app = FastAPI(title="RenderCV API", version="1.0.0")
    app.include_router(render_router)

    app.add_exception_handler(
        RenderCVUserValidationError, rendercv_user_validation_error_handler
    )
    app.add_exception_handler(RenderCVUserError, rendercv_user_error_handler)
    app.add_exception_handler(RenderCVInternalError, rendercv_internal_error_handler)

    return app


app = create_app()
