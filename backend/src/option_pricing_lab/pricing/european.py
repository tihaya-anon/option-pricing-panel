from __future__ import annotations

import math

from option_pricing_lab.domain.contracts import EuropeanOptionSpec, OptionType
from option_pricing_lab.pricing.core import normal_cdf, normal_pdf


def black_scholes_price(spec: EuropeanOptionSpec) -> float:
    if spec.volatility == 0.0:
        discounted_forward = spec.spot * math.exp(-spec.dividend_yield * spec.maturity)
        discounted_strike = spec.strike * math.exp(-spec.rate * spec.maturity)
        intrinsic = discounted_forward - discounted_strike
        return max(intrinsic, 0.0) if spec.option_type is OptionType.CALL else max(-intrinsic, 0.0)

    d_1, d_2 = _d1_d2(spec)
    discounted_spot = spec.spot * math.exp(-spec.dividend_yield * spec.maturity)
    discounted_strike = spec.strike * math.exp(-spec.rate * spec.maturity)

    if spec.option_type is OptionType.CALL:
        return discounted_spot * normal_cdf(d_1) - discounted_strike * normal_cdf(d_2)
    return discounted_strike * normal_cdf(-d_2) - discounted_spot * normal_cdf(-d_1)


def black_scholes_vega(spec: EuropeanOptionSpec) -> float:
    if spec.volatility == 0.0:
        return 0.0
    d_1, _ = _d1_d2(spec)
    discounted_spot = spec.spot * math.exp(-spec.dividend_yield * spec.maturity)
    return discounted_spot * math.sqrt(spec.maturity) * normal_pdf(d_1)


def implied_volatility(
    premium: float,
    spec: EuropeanOptionSpec,
    initial_volatility: float = 0.2,
    tolerance: float = 1e-8,
    max_iterations: int = 200,
    volatility_lower_bound: float = 1e-6,
    volatility_upper_bound: float = 5.0,
) -> float:
    if premium <= 0.0:
        raise ValueError("premium must be positive")
    if initial_volatility <= 0.0:
        raise ValueError("initial_volatility must be positive")
    if tolerance <= 0.0:
        raise ValueError("tolerance must be positive")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    if volatility_lower_bound <= 0.0:
        raise ValueError("volatility_lower_bound must be positive")
    if volatility_upper_bound <= volatility_lower_bound:
        raise ValueError("volatility_upper_bound must be greater than volatility_lower_bound")

    lower = volatility_lower_bound
    upper = volatility_upper_bound
    sigma = min(max(initial_volatility, lower), upper)

    for _ in range(max_iterations):
        trial = EuropeanOptionSpec(
            spot=spec.spot,
            strike=spec.strike,
            maturity=spec.maturity,
            rate=spec.rate,
            volatility=sigma,
            option_type=spec.option_type,
            dividend_yield=spec.dividend_yield,
        )
        price = black_scholes_price(trial)
        difference = price - premium
        if abs(difference) < tolerance:
            return sigma

        vega = black_scholes_vega(trial)
        if vega > 1e-8:
            candidate = sigma - difference / vega
            if lower < candidate < upper:
                sigma = candidate
                continue

        if difference > 0.0:
            upper = sigma
        else:
            lower = sigma
        sigma = 0.5 * (lower + upper)

    raise RuntimeError("implied volatility did not converge")


def _d1_d2(spec: EuropeanOptionSpec) -> tuple[float, float]:
    volatility_term = spec.volatility * math.sqrt(spec.maturity)
    d_1 = (
        math.log(spec.spot / spec.strike)
        + (spec.rate - spec.dividend_yield + 0.5 * spec.volatility * spec.volatility) * spec.maturity
    ) / volatility_term
    d_2 = d_1 - volatility_term
    return d_1, d_2
