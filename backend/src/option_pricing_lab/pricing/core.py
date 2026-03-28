from __future__ import annotations

import math
from typing import Iterable

import numpy as np

from option_pricing_lab.domain.contracts import ConfidenceInterval, MonteCarloEstimate, OptionType

SQRT_TWO = math.sqrt(2.0)
SQRT_TWO_PI = math.sqrt(2.0 * math.pi)
CI_Z_SCORE = 1.96


def normal_cdf(value: float) -> float:
    return 0.5 * (1.0 + math.erf(value / SQRT_TWO))


def normal_pdf(value: float) -> float:
    return math.exp(-0.5 * value * value) / SQRT_TWO_PI


def payoff(option_type: OptionType, spots: np.ndarray | float, strike: float) -> np.ndarray | float:
    if option_type is OptionType.CALL:
        return np.maximum(np.asarray(spots) - strike, 0.0)
    return np.maximum(strike - np.asarray(spots), 0.0)


def confidence_interval(samples: np.ndarray) -> ConfidenceInterval:
    std_error = sample_std_error(samples)
    mean = float(np.mean(samples))
    radius = CI_Z_SCORE * std_error
    return ConfidenceInterval(lower=mean - radius, upper=mean + radius)


def sample_std_error(samples: np.ndarray) -> float:
    return float(np.std(samples, ddof=1) / math.sqrt(samples.size))


def monte_carlo_estimate(samples: np.ndarray) -> MonteCarloEstimate:
    return MonteCarloEstimate(
        price=float(np.mean(samples)),
        std_error=sample_std_error(samples),
        confidence_interval=confidence_interval(samples),
    )


def generate_correlated_normals(
    paths: int,
    correlation: float,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray]:
    z_1 = rng.standard_normal(paths)
    z_2 = rng.standard_normal(paths)
    correlated_z_2 = correlation * z_1 + math.sqrt(1.0 - correlation * correlation) * z_2
    return z_1, correlated_z_2


def inverse_normal_cdf(probability: float) -> float:
    if probability <= 0.0 or probability >= 1.0:
        raise ValueError("probability must be in the open interval (0, 1)")

    a = (
        -3.969683028665376e01,
        2.209460984245205e02,
        -2.759285104469687e02,
        1.383577518672690e02,
        -3.066479806614716e01,
        2.506628277459239e00,
    )
    b = (
        -5.447609879822406e01,
        1.615858368580409e02,
        -1.556989798598866e02,
        6.680131188771972e01,
        -1.328068155288572e01,
    )
    c = (
        -7.784894002430293e-03,
        -3.223964580411365e-01,
        -2.400758277161838e00,
        -2.549732539343734e00,
        4.374664141464968e00,
        2.938163982698783e00,
    )
    d = (
        7.784695709041462e-03,
        3.224671290700398e-01,
        2.445134137142996e00,
        3.754408661907416e00,
    )

    lower = 0.02425
    upper = 1.0 - lower

    if probability < lower:
        q = math.sqrt(-2.0 * math.log(probability))
        return (
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )

    if probability > upper:
        q = math.sqrt(-2.0 * math.log(1.0 - probability))
        return -(
            (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5])
            / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1.0)
        )

    q = probability - 0.5
    r = q * q
    return (
        (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q
        / (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1.0)
    )


def first_primes(count: int) -> list[int]:
    if count <= 0:
        return []

    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        is_prime = True
        limit = int(math.sqrt(candidate))
        for prime in primes:
            if prime > limit:
                break
            if candidate % prime == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(candidate)
        candidate += 1
    return primes


def van_der_corput(index: int, base: int) -> float:
    result = 0.0
    factor = 1.0 / base
    current = index
    while current > 0:
        result += (current % base) * factor
        current //= base
        factor /= base
    return result


def halton_sequence(size: int, dimension: int, start_index: int = 1) -> np.ndarray:
    if size <= 0:
        raise ValueError("size must be positive")
    if dimension <= 0:
        raise ValueError("dimension must be positive")

    bases = first_primes(dimension)
    samples = np.empty((size, dimension), dtype=float)

    for column, base in enumerate(bases):
        for row in range(size):
            samples[row, column] = van_der_corput(start_index + row, base)

    return samples


def halton_normal_matrix(size: int, dimension: int, start_index: int = 32) -> np.ndarray:
    uniforms = halton_sequence(size=size, dimension=dimension, start_index=start_index)
    clipped = np.clip(uniforms, 1e-12, 1.0 - 1e-12)
    transform = np.vectorize(inverse_normal_cdf)
    return transform(clipped)


def geometric_mean(values: Iterable[float]) -> float:
    array = np.asarray(list(values), dtype=float)
    return float(np.exp(np.mean(np.log(array))))
