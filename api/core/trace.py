from __future__ import annotations

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class TraceMiddleware(BaseHTTPMiddleware):
    """Middleware that generates/propagates a trace_id per request.

    - If the X-Trace-Id header is present in the request, it is used.
    - Otherwise, a new UUID4 is generated.
    - The trace_id is available at request.state.trace_id.
    - The X-Trace-Id header is added to the response.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        trace_id = request.headers.get("X-Trace-Id", "").strip()
        if not trace_id:
            trace_id = str(uuid.uuid4())

        request.state.trace_id = trace_id

        logger = logging.getLogger("api.trace")
        logger.info(
            "Request method=%s path=%s trace_id=%s",
            request.method,
            request.url.path,
            trace_id,
        )

        response = await call_next(request)

        response.headers["X-Trace-Id"] = trace_id

        return response
