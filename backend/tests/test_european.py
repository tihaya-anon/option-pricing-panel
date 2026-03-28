import math

from option_pricing_lab.domain.contracts import EuropeanOptionSpec, OptionType
from option_pricing_lab.pricing.european import black_scholes_price, implied_volatility


def test_black_scholes_call_matches_reference_value() -> None:
    spec = EuropeanOptionSpec(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.2,
        dividend_yield=0.0,
        option_type=OptionType.CALL,
    )
    assert math.isclose(black_scholes_price(spec), 10.450583572185565, rel_tol=1e-9)


def test_implied_volatility_recovers_original_sigma() -> None:
    spec = EuropeanOptionSpec(
        spot=100.0,
        strike=95.0,
        maturity=1.5,
        rate=0.03,
        volatility=0.35,
        dividend_yield=0.01,
        option_type=OptionType.PUT,
    )
    premium = black_scholes_price(spec)
    solver_spec = EuropeanOptionSpec(
        spot=spec.spot,
        strike=spec.strike,
        maturity=spec.maturity,
        rate=spec.rate,
        volatility=0.2,
        dividend_yield=spec.dividend_yield,
        option_type=spec.option_type,
    )
    assert math.isclose(implied_volatility(premium=premium, spec=solver_spec), 0.35, rel_tol=1e-7)
