"""
Standard JSON and themed HTML error responses.
"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.app.utilities import config

VALIDATION_ERROR = "VALIDATION_ERROR"
AUTH_FAILED = "AUTH_FAILED"
FORBIDDEN = "FORBIDDEN"
NOT_FOUND = "NOT_FOUND"
CONFLICT = "CONFLICT"
INTERNAL_ERROR = "INTERNAL_ERROR"
SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"


def _body(status_code: int, code: str, message: str, details: Any = None) -> dict[str, Any]:
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details,
            "status": status_code,
        }
    }


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=_body(status_code, code, message, details),
    )


def _code_for_status(status_code: int) -> str:
    return {
        400: VALIDATION_ERROR,
        401: AUTH_FAILED,
        403: FORBIDDEN,
        404: NOT_FOUND,
        409: CONFLICT,
        503: SERVICE_UNAVAILABLE,
    }.get(status_code, INTERNAL_ERROR)


def _wants_html(request: Request) -> bool:
    accept = request.headers.get("accept", "")
    return "text/html" in accept and "application/json" not in accept


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = _code_for_status(exc.status_code)
    message = str(exc.detail)
    logger.warning(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")

    if _wants_html(request):
        from src.app.main import templates

        return templates.TemplateResponse(
            request,
            "error.html",
            {"status": exc.status_code, "code": code, "message": message},
            status_code=exc.status_code,
        )

    return error_response(exc.status_code, code, message)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    details = exc.errors()
    logger.warning(f"Validation error on {request.url.path}: {details}")
    return error_response(
        422,
        VALIDATION_ERROR,
        "Request validation failed.",
        details=details,
    )


async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error on {request.url.path}: {exc}")
    details = None if config.RUN_ENVIRONMENT == "production" else str(exc)
    if _wants_html(request):
        from src.app.main import templates

        return templates.TemplateResponse(
            request,
            "error.html",
            {
                "status": 500,
                "code": INTERNAL_ERROR,
                "message": "An unexpected error occurred.",
            },
            status_code=500,
        )
    return error_response(
        500,
        INTERNAL_ERROR,
        "An unexpected error occurred.",
        details=details,
    )
