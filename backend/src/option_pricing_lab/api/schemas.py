from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from option_pricing_lab.domain.contracts import (
    AmericanOptionSpec,
    ArithmeticAsianOptionSpec,
    ArithmeticBasketOptionSpec,
    ConfidenceInterval,
    EuropeanOptionSpec,
    GeometricAsianOptionSpec,
    GeometricBasketOptionSpec,
    KikoPutOptionSpec,
    KikoResult,
    MonteCarloEstimate,
    OptionType,
)


class ApiModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, extra="forbid")


class HealthResponse(ApiModel):
    status: str = "ok"
    service: str = "option-pricing-lab"


class PriceResponse(ApiModel):
    price: float


class ImpliedVolatilityRequest(ApiModel):
    premium: float = Field(gt=0)
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    maturity: float = Field(gt=0)
    rate: float
    dividend_yield: float = 0.0
    option_type: OptionType
    initial_volatility: float = Field(default=0.2, gt=0)
    tolerance: float = Field(default=1e-8, gt=0)
    max_iterations: int = Field(default=200, gt=0)
    volatility_lower_bound: float = Field(default=1e-6, gt=0)
    volatility_upper_bound: float = Field(default=5.0, gt=0)

    def to_contract(self) -> EuropeanOptionSpec:
        return EuropeanOptionSpec(
            spot=self.spot,
            strike=self.strike,
            maturity=self.maturity,
            rate=self.rate,
            volatility=self.initial_volatility,
            dividend_yield=self.dividend_yield,
            option_type=self.option_type,
        )


class ImpliedVolatilityResponse(ApiModel):
    implied_volatility: float


class ConfidenceIntervalResponse(ApiModel):
    lower: float
    upper: float

    @classmethod
    def from_contract(cls, value: ConfidenceInterval) -> "ConfidenceIntervalResponse":
        return cls(lower=value.lower, upper=value.upper)


class MonteCarloEstimateResponse(ApiModel):
    price: float
    std_error: float
    confidence_interval: ConfidenceIntervalResponse

    @classmethod
    def from_contract(cls, value: MonteCarloEstimate) -> "MonteCarloEstimateResponse":
        return cls(
            price=value.price,
            std_error=value.std_error,
            confidence_interval=ConfidenceIntervalResponse.from_contract(value.confidence_interval),
        )


class KikoResultResponse(ApiModel):
    price: float
    delta: float
    std_error: float
    confidence_interval: ConfidenceIntervalResponse

    @classmethod
    def from_contract(cls, value: KikoResult) -> "KikoResultResponse":
        return cls(
            price=value.price,
            delta=value.delta,
            std_error=value.std_error,
            confidence_interval=ConfidenceIntervalResponse.from_contract(value.confidence_interval),
        )


class EuropeanOptionRequest(ApiModel):
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    maturity: float = Field(gt=0)
    rate: float
    volatility: float = Field(ge=0)
    dividend_yield: float = 0.0
    option_type: OptionType

    def to_contract(self) -> EuropeanOptionSpec:
        return EuropeanOptionSpec(**self.model_dump())


class AmericanOptionRequest(ApiModel):
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    maturity: float = Field(gt=0)
    rate: float
    volatility: float = Field(ge=0)
    steps: int = Field(gt=0)
    dividend_yield: float = 0.0
    option_type: OptionType

    def to_contract(self) -> AmericanOptionSpec:
        return AmericanOptionSpec(**self.model_dump())


class GeometricAsianOptionRequest(ApiModel):
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    maturity: float = Field(gt=0)
    rate: float
    volatility: float = Field(ge=0)
    observations: int = Field(gt=0)
    option_type: OptionType

    def to_contract(self) -> GeometricAsianOptionSpec:
        return GeometricAsianOptionSpec(**self.model_dump())


class ArithmeticAsianOptionRequest(GeometricAsianOptionRequest):
    paths: int = Field(default=100_000, gt=1)
    seed: int = 42
    use_control_variate: bool = True

    def to_contract(self) -> ArithmeticAsianOptionSpec:
        return ArithmeticAsianOptionSpec(**self.model_dump())


class GeometricBasketOptionRequest(ApiModel):
    spot_1: float = Field(gt=0)
    spot_2: float = Field(gt=0)
    strike: float = Field(gt=0)
    maturity: float = Field(gt=0)
    rate: float
    volatility_1: float = Field(ge=0)
    volatility_2: float = Field(ge=0)
    correlation: float = Field(ge=-1.0, le=1.0)
    option_type: OptionType

    def to_contract(self) -> GeometricBasketOptionSpec:
        return GeometricBasketOptionSpec(**self.model_dump())


class ArithmeticBasketOptionRequest(GeometricBasketOptionRequest):
    paths: int = Field(default=100_000, gt=1)
    seed: int = 42
    use_control_variate: bool = True

    def to_contract(self) -> ArithmeticBasketOptionSpec:
        return ArithmeticBasketOptionSpec(**self.model_dump())


class KikoPutOptionRequest(ApiModel):
    spot: float = Field(gt=0)
    strike: float = Field(gt=0)
    maturity: float = Field(gt=0)
    rate: float
    volatility: float = Field(ge=0)
    lower_barrier: float = Field(ge=0)
    upper_barrier: float = Field(gt=0)
    observations: int = Field(gt=0)
    rebate: float = Field(ge=0)
    paths: int = Field(default=8_192, gt=1)
    delta_shift: float = Field(default=0.5, gt=0)

    def to_contract(self) -> KikoPutOptionSpec:
        return KikoPutOptionSpec(**self.model_dump())
