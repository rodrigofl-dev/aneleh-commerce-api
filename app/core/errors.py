from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


def _error_response(
    status_code: int, code: str, message: str, details: dict | None = None
):
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    # Business exceptions (AppException, see core/exceptions.py) always set detail
    # as {"code", "message", "details"?}. But framework-raised exceptions (e.g. a
    # 404 from an unmatched route) use a plain string as detail — this fallback
    # covers both cases without requiring every raise site to be rewritten.
    if isinstance(exc.detail, dict):
        code = exc.detail.get("code", "HTTP_ERROR")
        message = exc.detail.get("message", "Unexpected error.")
        details = exc.detail.get("details")
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)
        details = None

    return _error_response(exc.status_code, code, message, details)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Automatic Pydantic/FastAPI validation errors (422)
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "VALIDATION_ERROR",
        "Validation error in the submitted data.",
        {"fields": exc.errors()},
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
