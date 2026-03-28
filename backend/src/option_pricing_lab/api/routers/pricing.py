from __future__ import annotations

from fastapi import APIRouter

from option_pricing_lab.api.schemas import (
    AmericanOptionRequest,
    ArithmeticAsianOptionRequest,
    ArithmeticBasketOptionRequest,
    EuropeanOptionRequest,
    GeometricAsianOptionRequest,
    GeometricBasketOptionRequest,
    ImpliedVolatilityRequest,
    ImpliedVolatilityResponse,
    KikoPutOptionRequest,
    KikoResultResponse,
    MonteCarloEstimateResponse,
    PriceResponse,
)
from option_pricing_lab.application.service import OptionPricingService

router = APIRouter(prefix="/pricing", tags=["pricing"])
pricing_service = OptionPricingService()


@router.post("/european", response_model=PriceResponse)
def price_european(request: EuropeanOptionRequest) -> PriceResponse:
    return PriceResponse(price=pricing_service.price_european(request.to_contract()))


@router.post("/implied-volatility", response_model=ImpliedVolatilityResponse)
def solve_implied_volatility(request: ImpliedVolatilityRequest) -> ImpliedVolatilityResponse:
    implied_volatility = pricing_service.solve_implied_volatility(
        premium=request.premium,
        spec=request.to_contract(),
        initial_volatility=request.initial_volatility,
        tolerance=request.tolerance,
        max_iterations=request.max_iterations,
        volatility_lower_bound=request.volatility_lower_bound,
        volatility_upper_bound=request.volatility_upper_bound,
    )
    return ImpliedVolatilityResponse(implied_volatility=implied_volatility)


@router.post("/american", response_model=PriceResponse)
def price_american(request: AmericanOptionRequest) -> PriceResponse:
    return PriceResponse(price=pricing_service.price_american(request.to_contract()))


@router.post("/asian/geometric", response_model=PriceResponse)
def price_geometric_asian(request: GeometricAsianOptionRequest) -> PriceResponse:
    return PriceResponse(price=pricing_service.price_geometric_asian(request.to_contract()))


@router.post("/asian/arithmetic", response_model=MonteCarloEstimateResponse)
def price_arithmetic_asian(request: ArithmeticAsianOptionRequest) -> MonteCarloEstimateResponse:
    return MonteCarloEstimateResponse.from_contract(pricing_service.price_arithmetic_asian(request.to_contract()))


@router.post("/basket/geometric", response_model=PriceResponse)
def price_geometric_basket(request: GeometricBasketOptionRequest) -> PriceResponse:
    return PriceResponse(price=pricing_service.price_geometric_basket(request.to_contract()))


@router.post("/basket/arithmetic", response_model=MonteCarloEstimateResponse)
def price_arithmetic_basket(request: ArithmeticBasketOptionRequest) -> MonteCarloEstimateResponse:
    return MonteCarloEstimateResponse.from_contract(pricing_service.price_arithmetic_basket(request.to_contract()))


@router.post("/kiko-put", response_model=KikoResultResponse)
def price_kiko_put(request: KikoPutOptionRequest) -> KikoResultResponse:
    return KikoResultResponse.from_contract(pricing_service.price_kiko_put(request.to_contract()))
