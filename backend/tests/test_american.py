from option_pricing_lab.domain.contracts import AmericanOptionSpec, EuropeanOptionSpec, OptionType
from option_pricing_lab.pricing.american import american_option_price
from option_pricing_lab.pricing.european import black_scholes_price


def test_american_put_is_at_least_european_put() -> None:
    american_spec = AmericanOptionSpec(
        spot=100.0,
        strike=100.0,
        maturity=1.0,
        rate=0.05,
        volatility=0.2,
        steps=400,
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
    assert american_option_price(american_spec) >= black_scholes_price(european_spec)
