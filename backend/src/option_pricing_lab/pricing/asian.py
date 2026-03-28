from __future__ import annotations

import math

import numpy as np

from option_pricing_lab.domain.contracts import ArithmeticAsianOptionSpec, GeometricAsianOptionSpec, OptionType
from option_pricing_lab.pricing.core import monte_carlo_estimate, normal_cdf, payoff


def geometric_asian_price(spec: GeometricAsianOptionSpec) -> float:
    time_weight = spec.maturity * (spec.observations + 1.0) / (2.0 * spec.observations)
    variance = (
        spec.volatility
        * spec.volatility
        * spec.maturity
        * (spec.observations + 1.0)
        * (2.0 * spec.observations + 1.0)
        / (6.0 * spec.observations * spec.observations)
    )
    mean = math.log(spec.spot) + (spec.rate - 0.5 * spec.volatility * spec.volatility) * time_weight
    standard_deviation = math.sqrt(variance)

    if standard_deviation == 0.0:
        deterministic_average = math.exp(mean)
        discounted_payoff = math.exp(-spec.rate * spec.maturity) * max(
            deterministic_average - spec.strike if spec.option_type is OptionType.CALL else spec.strike - deterministic_average,
            0.0,
        )
        return discounted_payoff

    d_1 = (mean - math.log(spec.strike) + variance) / standard_deviation
    d_2 = d_1 - standard_deviation
    discounted_mean = math.exp(-spec.rate * spec.maturity + mean + 0.5 * variance)
    discounted_strike = spec.strike * math.exp(-spec.rate * spec.maturity)

    if spec.option_type is OptionType.CALL:
        return discounted_mean * normal_cdf(d_1) - discounted_strike * normal_cdf(d_2)
    return discounted_strike * normal_cdf(-d_2) - discounted_mean * normal_cdf(-d_1)


def arithmetic_asian_price(spec: ArithmeticAsianOptionSpec):
    rng = np.random.default_rng(spec.seed)
    dt = spec.maturity / spec.observations
    drift = (spec.rate - 0.5 * spec.volatility * spec.volatility) * dt
    diffusion = spec.volatility * math.sqrt(dt)

    spots = np.full(spec.paths, spec.spot, dtype=float)
    arithmetic_sum = np.zeros(spec.paths, dtype=float)
    geometric_log_sum = np.zeros(spec.paths, dtype=float)

    for _ in range(spec.observations):
        shocks = rng.standard_normal(spec.paths)
        spots *= np.exp(drift + diffusion * shocks)
        arithmetic_sum += spots
        geometric_log_sum += np.log(spots)

    arithmetic_average = arithmetic_sum / spec.observations
    geometric_average = np.exp(geometric_log_sum / spec.observations)
    discount = math.exp(-spec.rate * spec.maturity)

    arithmetic_payoffs = discount * payoff(spec.option_type, arithmetic_average, spec.strike)

    if not spec.use_control_variate:
        return monte_carlo_estimate(arithmetic_payoffs)

    geometric_payoffs = discount * payoff(spec.option_type, geometric_average, spec.strike)
    exact_geometric_price = geometric_asian_price(
        GeometricAsianOptionSpec(
            spot=spec.spot,
            strike=spec.strike,
            maturity=spec.maturity,
            rate=spec.rate,
            volatility=spec.volatility,
            observations=spec.observations,
            option_type=spec.option_type,
        )
    )
    covariance = np.cov(arithmetic_payoffs, geometric_payoffs, ddof=1)[0, 1]
    geometric_variance = np.var(geometric_payoffs, ddof=1)
    beta = 0.0 if geometric_variance == 0.0 else covariance / geometric_variance
    adjusted_payoffs = arithmetic_payoffs - beta * (geometric_payoffs - exact_geometric_price)
    return monte_carlo_estimate(adjusted_payoffs)
