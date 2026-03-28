from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OptionType(str, Enum):
    CALL = "call"
    PUT = "put"

    @classmethod
    def from_value(cls, value: str) -> "OptionType":
        normalized = value.strip().lower()
        try:
            return cls(normalized)
        except ValueError as exc:
            raise ValueError(f"Unsupported option type: {value}") from exc


@dataclass(frozen=True)
class ConfidenceInterval:
    lower: float
    upper: float


@dataclass(frozen=True)
class MonteCarloEstimate:
    price: float
    std_error: float
    confidence_interval: ConfidenceInterval


@dataclass(frozen=True)
class KikoResult:
    price: float
    delta: float
    std_error: float
    confidence_interval: ConfidenceInterval


@dataclass(frozen=True)
class EuropeanOptionSpec:
    spot: float
    strike: float
    maturity: float
    rate: float
    volatility: float
    option_type: OptionType
    dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        _validate_positive("spot", self.spot)
        _validate_positive("strike", self.strike)
        _validate_positive("maturity", self.maturity)
        _validate_non_negative("volatility", self.volatility)


@dataclass(frozen=True)
class AmericanOptionSpec:
    spot: float
    strike: float
    maturity: float
    rate: float
    volatility: float
    steps: int
    option_type: OptionType
    dividend_yield: float = 0.0

    def __post_init__(self) -> None:
        _validate_positive("spot", self.spot)
        _validate_positive("strike", self.strike)
        _validate_positive("maturity", self.maturity)
        _validate_non_negative("volatility", self.volatility)
        if self.steps <= 0:
            raise ValueError("steps must be positive")


@dataclass(frozen=True)
class GeometricAsianOptionSpec:
    spot: float
    strike: float
    maturity: float
    rate: float
    volatility: float
    observations: int
    option_type: OptionType

    def __post_init__(self) -> None:
        _validate_positive("spot", self.spot)
        _validate_positive("strike", self.strike)
        _validate_positive("maturity", self.maturity)
        _validate_non_negative("volatility", self.volatility)
        if self.observations <= 0:
            raise ValueError("observations must be positive")


@dataclass(frozen=True)
class ArithmeticAsianOptionSpec(GeometricAsianOptionSpec):
    paths: int = 100_000
    seed: int = 42
    use_control_variate: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.paths <= 1:
            raise ValueError("paths must be greater than 1")


@dataclass(frozen=True)
class GeometricBasketOptionSpec:
    spot_1: float
    spot_2: float
    strike: float
    maturity: float
    rate: float
    volatility_1: float
    volatility_2: float
    correlation: float
    option_type: OptionType

    def __post_init__(self) -> None:
        _validate_positive("spot_1", self.spot_1)
        _validate_positive("spot_2", self.spot_2)
        _validate_positive("strike", self.strike)
        _validate_positive("maturity", self.maturity)
        _validate_non_negative("volatility_1", self.volatility_1)
        _validate_non_negative("volatility_2", self.volatility_2)
        if not -1.0 <= self.correlation <= 1.0:
            raise ValueError("correlation must be between -1 and 1")


@dataclass(frozen=True)
class ArithmeticBasketOptionSpec(GeometricBasketOptionSpec):
    paths: int = 100_000
    seed: int = 42
    use_control_variate: bool = True

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.paths <= 1:
            raise ValueError("paths must be greater than 1")


@dataclass(frozen=True)
class KikoPutOptionSpec:
    spot: float
    strike: float
    maturity: float
    rate: float
    volatility: float
    lower_barrier: float
    upper_barrier: float
    observations: int
    rebate: float
    paths: int = 8_192
    delta_shift: float = 0.5

    def __post_init__(self) -> None:
        _validate_positive("spot", self.spot)
        _validate_positive("strike", self.strike)
        _validate_positive("maturity", self.maturity)
        _validate_non_negative("volatility", self.volatility)
        _validate_positive("upper_barrier", self.upper_barrier)
        _validate_non_negative("lower_barrier", self.lower_barrier)
        _validate_non_negative("rebate", self.rebate)
        _validate_positive("delta_shift", self.delta_shift)
        if self.lower_barrier >= self.spot:
            raise ValueError("lower_barrier must be lower than the initial spot")
        if self.upper_barrier <= self.spot:
            raise ValueError("upper_barrier must be higher than the initial spot")
        if self.observations <= 0:
            raise ValueError("observations must be positive")
        if self.paths <= 1:
            raise ValueError("paths must be greater than 1")


def _validate_positive(name: str, value: float) -> None:
    if value <= 0.0:
        raise ValueError(f"{name} must be positive")


def _validate_non_negative(name: str, value: float) -> None:
    if value < 0.0:
        raise ValueError(f"{name} must be non-negative")
