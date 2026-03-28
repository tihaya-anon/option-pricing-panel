import math

from option_pricing_lab.domain.contracts import (
    ArithmeticAsianOptionSpec,
    ArithmeticBasketOptionSpec,
    EuropeanOptionSpec,
    GeometricAsianOptionSpec,
    GeometricBasketOptionSpec,
    KikoPutOptionSpec,
    OptionType,
)
from option_pricing_lab.pricing.asian import arithmetic_asian_price, geometric_asian_price
from option_pricing_lab.pricing.basket import arithmetic_basket_price, geometric_basket_price
from option_pricing_lab.pricing.european import black_scholes_price
from option_pricing_lab.pricing.kiko import quasi_monte_carlo_kiko_put


def test_geometric_asian_with_single_observation_reduces_to_european() -> None:
    asian_spec = GeometricAsianOptionSpec(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.2,
        observations=1,
        option_type=OptionType.CALL,
    )
    european_spec = EuropeanOptionSpec(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.2,
        option_type=OptionType.CALL,
    )
    assert math.isclose(
        geometric_asian_price(asian_spec),
        black_scholes_price(european_spec),
        rel_tol=1e-9,
    )


def test_geometric_basket_with_identical_assets_reduces_to_european() -> None:
    basket_spec = GeometricBasketOptionSpec(
        spot_1=100.0,
        spot_2=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility_1=0.2,
        volatility_2=0.2,
        correlation=1.0,
        option_type=OptionType.PUT,
    )
    european_spec = EuropeanOptionSpec(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.2,
        option_type=OptionType.PUT,
    )
    assert math.isclose(
        geometric_basket_price(basket_spec),
        black_scholes_price(european_spec),
        rel_tol=1e-9,
    )


def test_arithmetic_asian_control_variate_runs_and_returns_interval() -> None:
    estimate = arithmetic_asian_price(
        ArithmeticAsianOptionSpec(
            spot=100.0,
            strike=100.0,
            maturity=3.0,
            rate=0.05,
            volatility=0.3,
            observations=50,
            option_type=OptionType.PUT,
            paths=20_000,
            seed=7,
            use_control_variate=True,
        )
    )
    assert estimate.confidence_interval.lower <= estimate.price <= estimate.confidence_interval.upper
    assert estimate.std_error > 0.0


def test_arithmetic_basket_control_variate_runs_and_returns_interval() -> None:
    estimate = arithmetic_basket_price(
        ArithmeticBasketOptionSpec(
            spot_1=100.0,
            spot_2=100.0,
            strike=100.0,
            maturity=3.0,
            rate=0.05,
            volatility_1=0.3,
            volatility_2=0.3,
            correlation=0.5,
            option_type=OptionType.CALL,
            paths=20_000,
            seed=7,
            use_control_variate=True,
        )
    )
    assert estimate.confidence_interval.lower <= estimate.price <= estimate.confidence_interval.upper
    assert estimate.std_error > 0.0


def test_kiko_with_zero_reachable_knock_in_has_zero_value() -> None:
    result = quasi_monte_carlo_kiko_put(
        KikoPutOptionSpec(
            spot=100.0,
            strike=100.0,
            maturity=3.0,
            rate=0.05,
            volatility=0.2,
            lower_barrier=0.01,
            upper_barrier=200.0,
            observations=32,
            rebate=0.0,
            paths=2048,
            delta_shift=0.5,
        )
    )
    assert math.isclose(result.price, 0.0, abs_tol=1e-12)
    assert math.isclose(result.delta, 0.0, abs_tol=1e-12)
