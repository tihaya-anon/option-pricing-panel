from __future__ import annotations

import uvicorn

from option_pricing_lab.api import app as fastapi_app


def main() -> None:
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
