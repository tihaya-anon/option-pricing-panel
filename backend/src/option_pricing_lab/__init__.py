"""Option pricing toolkit for FITE7405 assignment 3."""

from option_pricing_lab.api import app, create_app
from option_pricing_lab.application.service import OptionPricingService, create_ui_backend
from option_pricing_lab.domain.contracts import (
    AmericanOptionSpec,
    ArithmeticAsianOptionSpec,
    ArithmeticBasketOptionSpec,
    ConfidenceInterval,
    EuropeanOptionSpec,
    GeometricAsianOptionSpec,
    GeometricBasketOptionSpec,
    KikoPutOptionSpec,
    KikoResult,
    MonteCarloEstimate,
    OptionType,
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

__all__ = [
    "AmericanOptionSpec",
    "ArithmeticAsianOptionSpec",
    "ArithmeticBasketOptionSpec",
    "ConfidenceInterval",
    "EuropeanOptionSpec",
    "GeometricAsianOptionSpec",
    "GeometricBasketOptionSpec",
    "KikoPutOptionSpec",
    "KikoResult",
    "MonteCarloEstimate",
    "OptionPricingService",
    "OptionType",
    "app",
    "american_option_price",
    "arithmetic_asian_price",
    "arithmetic_basket_price",
    "black_scholes_price",
    "create_app",
    "create_ui_backend",
    "geometric_asian_price",
    "geometric_basket_price",
    "implied_volatility",
    "quasi_monte_carlo_kiko_put",
]
