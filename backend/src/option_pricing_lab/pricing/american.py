from __future__ import annotations

import math

import numpy as np

from option_pricing_lab.domain.contracts import AmericanOptionSpec, OptionType


def american_option_price(spec: AmericanOptionSpec) -> float:
    dt = spec.maturity / spec.steps
    if dt <= 0.0:
        raise ValueError("time step must be positive")

    if spec.volatility == 0.0:
        forward_spot = spec.spot * math.exp((spec.rate - spec.dividend_yield) * spec.maturity)
        exercise = (
            max(forward_spot - spec.strike, 0.0)
            if spec.option_type is OptionType.CALL
            else max(spec.strike - forward_spot, 0.0)
        )
        return math.exp(-spec.rate * spec.maturity) * exercise

    up = math.exp(spec.volatility * math.sqrt(dt))
    down = 1.0 / up
    growth = math.exp((spec.rate - spec.dividend_yield) * dt)
    probability = (growth - down) / (up - down)
    if not 0.0 <= probability <= 1.0:
        raise ValueError("invalid tree parameters, increase the number of steps")

    discount = math.exp(-spec.rate * dt)
    step_indices = np.arange(spec.steps + 1)
    asset_prices = spec.spot * (up ** (spec.steps - step_indices)) * (down ** step_indices)
    option_values = _exercise_value(spec.option_type, asset_prices, spec.strike)

    for _ in range(spec.steps - 1, -1, -1):
        asset_prices = asset_prices[:-1] / up
        continuation = discount * (
            probability * option_values[:-1] + (1.0 - probability) * option_values[1:]
        )
        exercise = _exercise_value(spec.option_type, asset_prices, spec.strike)
        option_values = np.maximum(continuation, exercise)

    return float(option_values[0])


def _exercise_value(option_type: OptionType, spots: np.ndarray, strike: float) -> np.ndarray:
    if option_type is OptionType.CALL:
        return np.maximum(spots - strike, 0.0)
    return np.maximum(strike - spots, 0.0)
