from __future__ import annotations

from fastapi import FastAPI

from option_pricing_lab.api.errors import register_exception_handlers
from option_pricing_lab.api.routers.pricing import router as pricing_router
from option_pricing_lab.api.routers.system import router as system_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="Option Pricing Lab API",
        version="0.1.0",
        description="HTTP API for the FITE7405 mini option pricer.",
    )
    register_exception_handlers(app)
    app.include_router(system_router)
    app.include_router(pricing_router)
    return app


app = create_app()
