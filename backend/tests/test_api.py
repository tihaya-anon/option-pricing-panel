from fastapi.testclient import TestClient

from option_pricing_lab.api import app
from option_pricing_lab.domain.contracts import EuropeanOptionSpec, OptionType
from option_pricing_lab.pricing.european import black_scholes_price


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "option-pricing-lab"}


def test_european_pricing_endpoint() -> None:
    response = client.post(
        "/pricing/european",
        json={
            "spot": 100.0,
            "strike": 100.0,
            "maturity": 1.0,
            "rate": 0.05,
            "volatility": 0.2,
            "dividend_yield": 0.0,
            "option_type": "call",
        },
    )
    assert response.status_code == 200
    assert response.json()["price"] > 0.0


def test_implied_volatility_endpoint_accepts_solver_parameters() -> None:
    premium = black_scholes_price(
        EuropeanOptionSpec(
            spot=100.0,
            strike=95.0,
            maturity=1.5,
            rate=0.03,
            volatility=0.35,
            dividend_yield=0.01,
            option_type=OptionType.PUT,
        )
    )
    response = client.post(
        "/pricing/implied-volatility",
        json={
            "premium": premium,
            "spot": 100.0,
            "strike": 95.0,
            "maturity": 1.5,
            "rate": 0.03,
            "dividend_yield": 0.01,
            "option_type": "put",
            "initial_volatility": 0.5,
            "tolerance": 1e-10,
            "max_iterations": 300,
            "volatility_lower_bound": 0.01,
            "volatility_upper_bound": 3.0,
        },
    )
    assert response.status_code == 200
    assert abs(response.json()["implied_volatility"] - 0.35) < 1e-6
