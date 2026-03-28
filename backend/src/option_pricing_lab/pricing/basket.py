from __future__ import annotations

import math

import numpy as np

from option_pricing_lab.domain.contracts import (
    ArithmeticBasketOptionSpec,
    GeometricBasketOptionSpec,
    OptionType,
)
from option_pricing_lab.pricing.core import (
    generate_correlated_normals,
    geometric_mean,
    monte_carlo_estimate,
    normal_cdf,
    payoff,
)


def geometric_basket_price(spec: GeometricBasketOptionSpec) -> float:
    basket_spot = geometric_mean((spec.spot_1, spec.spot_2))
    basket_variance = (
        spec.volatility_1 * spec.volatility_1
        + 2.0 * spec.correlation * spec.volatility_1 * spec.volatility_2
        + spec.volatility_2 * spec.volatility_2
    ) / 4.0
    basket_volatility = math.sqrt(basket_variance)
    basket_drift = spec.rate - 0.25 * (
        spec.volatility_1 * spec.volatility_1 + spec.volatility_2 * spec.volatility_2
    ) + 0.5 * basket_variance

    if basket_volatility == 0.0:
        terminal_basket = basket_spot * math.exp(basket_drift * spec.maturity)
        discounted = math.exp(-spec.rate * spec.maturity)
        intrinsic = terminal_basket - spec.strike
        return discounted * (max(intrinsic, 0.0) if spec.option_type is OptionType.CALL else max(-intrinsic, 0.0))

    volatility_term = basket_volatility * math.sqrt(spec.maturity)
    d_1 = (
        math.log(basket_spot / spec.strike)
        + (basket_drift + 0.5 * basket_variance) * spec.maturity
    ) / volatility_term
    d_2 = d_1 - volatility_term

    discounted_basket = math.exp(-spec.rate * spec.maturity) * basket_spot * math.exp(basket_drift * spec.maturity)
    discounted_strike = spec.strike * math.exp(-spec.rate * spec.maturity)

    if spec.option_type is OptionType.CALL:
        return discounted_basket * normal_cdf(d_1) - discounted_strike * normal_cdf(d_2)
    return discounted_strike * normal_cdf(-d_2) - discounted_basket * normal_cdf(-d_1)


def arithmetic_basket_price(spec: ArithmeticBasketOptionSpec):
    rng = np.random.default_rng(spec.seed)
    z_1, z_2 = generate_correlated_normals(spec.paths, spec.correlation, rng)

    drift_1 = (spec.rate - 0.5 * spec.volatility_1 * spec.volatility_1) * spec.maturity
    drift_2 = (spec.rate - 0.5 * spec.volatility_2 * spec.volatility_2) * spec.maturity
    diffusion_scale = math.sqrt(spec.maturity)

    terminal_1 = spec.spot_1 * np.exp(drift_1 + spec.volatility_1 * diffusion_scale * z_1)
    terminal_2 = spec.spot_2 * np.exp(drift_2 + spec.volatility_2 * diffusion_scale * z_2)

    arithmetic_basket = 0.5 * (terminal_1 + terminal_2)
    geometric_basket = np.sqrt(terminal_1 * terminal_2)
    discount = math.exp(-spec.rate * spec.maturity)

    arithmetic_payoffs = discount * payoff(spec.option_type, arithmetic_basket, spec.strike)
    if not spec.use_control_variate:
        return monte_carlo_estimate(arithmetic_payoffs)

    geometric_payoffs = discount * payoff(spec.option_type, geometric_basket, spec.strike)
    exact_geometric_price = geometric_basket_price(
        GeometricBasketOptionSpec(
            spot_1=spec.spot_1,
            spot_2=spec.spot_2,
            strike=spec.strike,
            maturity=spec.maturity,
            rate=spec.rate,
            volatility_1=spec.volatility_1,
            volatility_2=spec.volatility_2,
            correlation=spec.correlation,
            option_type=spec.option_type,
        )
    )
    covariance = np.cov(arithmetic_payoffs, geometric_payoffs, ddof=1)[0, 1]
    geometric_variance = np.var(geometric_payoffs, ddof=1)
    beta = 0.0 if geometric_variance == 0.0 else covariance / geometric_variance
    adjusted_payoffs = arithmetic_payoffs - beta * (geometric_payoffs - exact_geometric_price)
    return monte_carlo_estimate(adjusted_payoffs)
