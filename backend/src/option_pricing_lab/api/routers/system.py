from __future__ import annotations

from fastapi import APIRouter

from option_pricing_lab.api.schemas import HealthResponse

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()
