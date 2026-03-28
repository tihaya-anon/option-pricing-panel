from __future__ import annotations

import math

import numpy as np

from option_pricing_lab.domain.contracts import ConfidenceInterval, KikoPutOptionSpec, KikoResult
from option_pricing_lab.pricing.core import CI_Z_SCORE, halton_normal_matrix, sample_std_error


def quasi_monte_carlo_kiko_put(spec: KikoPutOptionSpec) -> KikoResult:
    normals = halton_normal_matrix(size=spec.paths, dimension=spec.observations)
    base_payoffs = _kiko_path_payoffs(spec=spec, initial_spot=spec.spot, normals=normals)
    up_payoffs = _kiko_path_payoffs(spec=spec, initial_spot=spec.spot + spec.delta_shift, normals=normals)
    down_payoffs = _kiko_path_payoffs(spec=spec, initial_spot=max(spec.spot - spec.delta_shift, 1e-8), normals=normals)

    price = float(np.mean(base_payoffs))
    std_error = sample_std_error(base_payoffs)
    radius = CI_Z_SCORE * std_error
    delta = float(np.mean(up_payoffs - down_payoffs) / (2.0 * spec.delta_shift))

    return KikoResult(
        price=price,
        delta=delta,
        std_error=std_error,
        confidence_interval=ConfidenceInterval(lower=price - radius, upper=price + radius),
    )


def _kiko_path_payoffs(spec: KikoPutOptionSpec, initial_spot: float, normals: np.ndarray) -> np.ndarray:
    dt = spec.maturity / spec.observations
    drift = (spec.rate - 0.5 * spec.volatility * spec.volatility) * dt
    diffusion = spec.volatility * math.sqrt(dt)

    spots = np.full(spec.paths, initial_spot, dtype=float)
    active = np.ones(spec.paths, dtype=bool)
    knocked_in = np.zeros(spec.paths, dtype=bool)
    payoffs = np.zeros(spec.paths, dtype=float)

    for step in range(spec.observations):
        spots *= np.exp(drift + diffusion * normals[:, step])
        time = (step + 1) * dt

        knocked_out_now = active & (spots >= spec.upper_barrier)
        if np.any(knocked_out_now):
            payoffs[knocked_out_now] = spec.rebate * math.exp(-spec.rate * time)
            active[knocked_out_now] = False

        knocked_in_now = active & (spots <= spec.lower_barrier)
        if np.any(knocked_in_now):
            knocked_in[knocked_in_now] = True

    maturity_hits = active & knocked_in
    if np.any(maturity_hits):
        payoffs[maturity_hits] = np.maximum(spec.strike - spots[maturity_hits], 0.0) * math.exp(
            -spec.rate * spec.maturity
        )

    return payoffs
