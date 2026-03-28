from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


def register_exception_handlers(app: FastAPI) -> None:
    app.exception_handler(ValueError)(_handle_bad_request)
    app.exception_handler(RuntimeError)(_handle_bad_request)


async def _handle_bad_request(_: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=400, content={"detail": str(exc)})
