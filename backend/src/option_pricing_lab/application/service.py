from __future__ import annotations

from option_pricing_lab.domain.contracts import (
    AmericanOptionSpec,
    ArithmeticAsianOptionSpec,
    ArithmeticBasketOptionSpec,
    EuropeanOptionSpec,
    GeometricAsianOptionSpec,
    GeometricBasketOptionSpec,
    KikoPutOptionSpec,
    KikoResult,
    MonteCarloEstimate,
)
from option_pricing_lab.pricing import (
    american_option_price,
    arithmetic_asian_price,
    arithmetic_basket_price,
    black_scholes_price,
    geometric_asian_price,
    geometric_basket_price,
    implied_volatility,
    quasi_monte_carlo_kiko_put,
)


class OptionPricingService:
    def price_european(self, spec: EuropeanOptionSpec) -> float:
        return black_scholes_price(spec)

    def solve_implied_volatility(
        self,
        premium: float,
        spec: EuropeanOptionSpec,
        initial_volatility: float = 0.2,
        tolerance: float = 1e-8,
        max_iterations: int = 200,
        volatility_lower_bound: float = 1e-6,
        volatility_upper_bound: float = 5.0,
    ) -> float:
        return implied_volatility(
            premium=premium,
            spec=spec,
            initial_volatility=initial_volatility,
            tolerance=tolerance,
            max_iterations=max_iterations,
            volatility_lower_bound=volatility_lower_bound,
            volatility_upper_bound=volatility_upper_bound,
        )

    def price_geometric_asian(self, spec: GeometricAsianOptionSpec) -> float:
        return geometric_asian_price(spec)

    def price_arithmetic_asian(self, spec: ArithmeticAsianOptionSpec) -> MonteCarloEstimate:
        return arithmetic_asian_price(spec)

    def price_geometric_basket(self, spec: GeometricBasketOptionSpec) -> float:
        return geometric_basket_price(spec)

    def price_arithmetic_basket(self, spec: ArithmeticBasketOptionSpec) -> MonteCarloEstimate:
        return arithmetic_basket_price(spec)

    def price_american(self, spec: AmericanOptionSpec) -> float:
        return american_option_price(spec)

    def price_kiko_put(self, spec: KikoPutOptionSpec) -> KikoResult:
        return quasi_monte_carlo_kiko_put(spec)


def create_ui_backend() -> OptionPricingService:
    return OptionPricingService()
