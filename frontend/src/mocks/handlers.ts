import type {
  AmericanOptionRequest,
  ArithmeticAsianOptionRequest,
  ArithmeticBasketOptionRequest,
  EuropeanOptionRequest,
  GeometricAsianOptionRequest,
  GeometricBasketOptionRequest,
  ImpliedVolatilityRequest,
  KikoPutOptionRequest,
  KikoResultResponse,
  MonteCarloEstimateResponse,
  PriceResponse,
} from "@/api/model";
import {
  getHealthHealthGetMockHandler,
  getPriceAmericanPricingAmericanPostMockHandler,
  getPriceArithmeticAsianPricingAsianArithmeticPostMockHandler,
  getPriceArithmeticBasketPricingBasketArithmeticPostMockHandler,
  getPriceEuropeanPricingEuropeanPostMockHandler,
  getPriceGeometricAsianPricingAsianGeometricPostMockHandler,
  getPriceGeometricBasketPricingBasketGeometricPostMockHandler,
  getPriceKikoPutPricingKikoPutPostMockHandler,
  getSolveImpliedVolatilityPricingImpliedVolatilityPostMockHandler,
} from "@/api/option_price.msw";

const DEFAULT_HEALTH_RESPONSE = {
  service: "option-pricing-lab",
  status: "ok",
};

function clamp(value: number, lower: number, upper: number) {
  return Math.min(Math.max(value, lower), upper);
}

function round(value: number, digits = 4) {
  return Number(value.toFixed(digits));
}

function normalCdf(value: number) {
  const sign = value < 0 ? -1 : 1;
  const absoluteValue = Math.abs(value) / Math.sqrt(2);
  const a1 = 0.254829592;
  const a2 = -0.284496736;
  const a3 = 1.421413741;
  const a4 = -1.453152027;
  const a5 = 1.061405429;
  const p = 0.3275911;
  const t = 1 / (1 + p * absoluteValue);
  const erf =
    1 -
    (((((a5 * t + a4) * t + a3) * t + a2) * t + a1) * t) *
      Math.exp(-absoluteValue * absoluteValue);

  return 0.5 * (1 + sign * erf);
}

function blackScholesPrice(input: {
  spot: number;
  strike: number;
  maturity: number;
  rate: number;
  volatility: number;
  dividendYield?: number;
  optionType: "call" | "put";
}) {
  const { spot, strike, maturity, rate, volatility, optionType } = input;
  const dividendYield = input.dividendYield ?? 0;

  if (volatility <= 0 || maturity <= 0) {
    const intrinsicValue =
      optionType === "call"
        ? Math.max(spot - strike, 0)
        : Math.max(strike - spot, 0);

    return round(intrinsicValue, 4);
  }

  const sigmaRootT = volatility * Math.sqrt(maturity);
  const d1 =
    (Math.log(spot / strike) +
      (rate - dividendYield + 0.5 * volatility * volatility) * maturity) /
    sigmaRootT;
  const d2 = d1 - sigmaRootT;
  const discountedSpot = spot * Math.exp(-dividendYield * maturity);
  const discountedStrike = strike * Math.exp(-rate * maturity);

  if (optionType === "call") {
    return round(
      discountedSpot * normalCdf(d1) - discountedStrike * normalCdf(d2),
      4
    );
  }

  return round(
    discountedStrike * normalCdf(-d2) - discountedSpot * normalCdf(-d1),
    4
  );
}

function createInterval(center: number, width: number) {
  return {
    lower: round(Math.max(center - width, 0), 4),
    upper: round(center + width, 4),
  };
}

async function getRequestBody<TPayload>(request: Request) {
  return (await request.json()) as TPayload;
}

function toMonteCarloEstimate(
  price: number,
  paths: number,
  adjustment: number
): MonteCarloEstimateResponse {
  const safePaths = Math.max(paths, 2_048);
  const stdError = round((Math.abs(price) * adjustment) / Math.sqrt(safePaths), 4);
  const intervalWidth = round(1.96 * stdError, 4);

  return {
    price: round(price, 4),
    std_error: stdError,
    confidence_interval: createInterval(price, intervalWidth),
  };
}

async function createEuropeanResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<EuropeanOptionRequest>(request);

  return {
    price: blackScholesPrice({
      spot: payload.spot,
      strike: payload.strike,
      maturity: payload.maturity,
      rate: payload.rate,
      volatility: payload.volatility,
      dividendYield: payload.dividend_yield,
      optionType: payload.option_type,
    }),
  } satisfies PriceResponse;
}

async function createAmericanResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<AmericanOptionRequest>(request);
  const europeanPrice = blackScholesPrice({
    spot: payload.spot,
    strike: payload.strike,
    maturity: payload.maturity,
    rate: payload.rate,
    volatility: payload.volatility,
    dividendYield: payload.dividend_yield,
    optionType: payload.option_type,
  });
  const earlyExercisePremium =
    payload.option_type === "put"
      ? 0.018 * payload.strike + 0.0004 * payload.steps
      : 0.004 * payload.strike + 0.0002 * payload.steps;

  return {
    price: round(europeanPrice + earlyExercisePremium, 4),
  } satisfies PriceResponse;
}

async function createGeometricAsianResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<GeometricAsianOptionRequest>(request);
  const basePrice = blackScholesPrice({
    spot: payload.spot,
    strike: payload.strike,
    maturity: payload.maturity,
    rate: payload.rate,
    volatility: payload.volatility * 0.82,
    optionType: payload.option_type,
  });

  return {
    price: round(basePrice * 0.93, 4),
  } satisfies PriceResponse;
}

async function createArithmeticAsianResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<ArithmeticAsianOptionRequest>(request);
  const anchorPrice = blackScholesPrice({
    spot: payload.spot,
    strike: payload.strike,
    maturity: payload.maturity,
    rate: payload.rate,
    volatility: payload.volatility * 0.88,
    optionType: payload.option_type,
  });
  const controlVariateBonus = payload.use_control_variate ? 0.18 : 0.42;

  return toMonteCarloEstimate(
    anchorPrice * 0.97 + controlVariateBonus,
    payload.paths ?? 100_000,
    payload.use_control_variate ? 1.9 : 2.6
  );
}

function basketInputsToEquivalent(
  payload:
    | GeometricBasketOptionRequest
    | ArithmeticBasketOptionRequest
): {
  spot: number;
  strike: number;
  maturity: number;
  rate: number;
  volatility: number;
  optionType: "call" | "put";
} {
  const blendedSpot = (payload.spot_1 + payload.spot_2) / 2;
  const basketVolatility = Math.sqrt(
    (payload.volatility_1 * payload.volatility_1 +
      payload.volatility_2 * payload.volatility_2 +
      2 * payload.correlation * payload.volatility_1 * payload.volatility_2) /
      4
  );

  return {
    spot: blendedSpot,
    strike: payload.strike,
    maturity: payload.maturity,
    rate: payload.rate,
    volatility: clamp(basketVolatility, 0.01, 2),
    optionType: payload.option_type,
  };
}

async function createGeometricBasketResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<GeometricBasketOptionRequest>(request);
  const equivalent = basketInputsToEquivalent(payload);

  return {
    price: round(blackScholesPrice(equivalent) * 0.94, 4),
  } satisfies PriceResponse;
}

async function createArithmeticBasketResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<ArithmeticBasketOptionRequest>(request);
  const equivalent = basketInputsToEquivalent(payload);
  const anchorPrice = blackScholesPrice({
    ...equivalent,
    volatility: equivalent.volatility * 1.04,
  });
  const controlVariateBonus = payload.use_control_variate ? 0.12 : 0.28;

  return toMonteCarloEstimate(
    anchorPrice * 0.99 + controlVariateBonus,
    payload.paths ?? 100_000,
    payload.use_control_variate ? 1.7 : 2.4
  );
}

async function createKikoResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<KikoPutOptionRequest>(request);
  const basePutPrice = blackScholesPrice({
    spot: payload.spot,
    strike: payload.strike,
    maturity: payload.maturity,
    rate: payload.rate,
    volatility: payload.volatility,
    optionType: "put",
  });
  const barrierPressure = clamp(
    (payload.upper_barrier - payload.lower_barrier) / Math.max(payload.spot, 1),
    0.15,
    1.5
  );
  const price = round(basePutPrice * 0.64 + payload.rebate * 0.35 + barrierPressure, 4);
  const paths = payload.paths ?? 8_192;
  const stdError = round((price * 2.2) / Math.sqrt(paths), 4);

  return {
    price,
    delta: round(clamp(-0.48 + (payload.strike - payload.spot) / payload.strike, -0.92, -0.08), 4),
    std_error: stdError,
    confidence_interval: createInterval(price, round(stdError * 1.96, 4)),
  } satisfies KikoResultResponse;
}

async function createImpliedVolatilityResponse({ request }: { request: Request }) {
  const payload = await getRequestBody<ImpliedVolatilityRequest>(request);
  let lowerBound = payload.volatility_lower_bound ?? 0.000001;
  let upperBound = payload.volatility_upper_bound ?? 5;
  const targetPrice = payload.premium;
  const maxIterations = payload.max_iterations ?? 200;
  const tolerance = payload.tolerance ?? 0.00000001;
  let volatility = payload.initial_volatility ?? 0.2;

  for (let iteration = 0; iteration < maxIterations; iteration += 1) {
    volatility = (lowerBound + upperBound) / 2;
    const price = blackScholesPrice({
      spot: payload.spot,
      strike: payload.strike,
      maturity: payload.maturity,
      rate: payload.rate,
      volatility,
      dividendYield: payload.dividend_yield,
      optionType: payload.option_type,
    });

    if (Math.abs(price - targetPrice) <= tolerance) {
      break;
    }

    if (price > targetPrice) {
      upperBound = volatility;
      continue;
    }

    lowerBound = volatility;
  }

  return {
    implied_volatility: round(volatility, 4),
  };
}

export const pricingHandlers = [
  getHealthHealthGetMockHandler(DEFAULT_HEALTH_RESPONSE),
  getPriceEuropeanPricingEuropeanPostMockHandler(createEuropeanResponse),
  getPriceAmericanPricingAmericanPostMockHandler(createAmericanResponse),
  getPriceGeometricAsianPricingAsianGeometricPostMockHandler(
    createGeometricAsianResponse
  ),
  getPriceArithmeticAsianPricingAsianArithmeticPostMockHandler(
    createArithmeticAsianResponse
  ),
  getPriceGeometricBasketPricingBasketGeometricPostMockHandler(
    createGeometricBasketResponse
  ),
  getPriceArithmeticBasketPricingBasketArithmeticPostMockHandler(
    createArithmeticBasketResponse
  ),
  getPriceKikoPutPricingKikoPutPostMockHandler(createKikoResponse),
  getSolveImpliedVolatilityPricingImpliedVolatilityPostMockHandler(
    createImpliedVolatilityResponse
  ),
];
