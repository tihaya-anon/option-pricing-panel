import { useState } from "react";
import {
  Activity,
  Blocks,
  ChartCandlestick,
  ChartColumnIncreasing,
  ChartSpline,
  CircleGauge,
  Gauge,
  GitBranch,
  Layers2,
  ShieldAlert,
} from "lucide-react";

import type { HTTPValidationError, OptionType } from "@/api/model";
import { OptionType as OptionTypeValues } from "@/api/model";
import {
  useHealthHealthGet,
  usePriceAmericanPricingAmericanPost,
  usePriceArithmeticAsianPricingAsianArithmeticPost,
  usePriceArithmeticBasketPricingBasketArithmeticPost,
  usePriceEuropeanPricingEuropeanPost,
  usePriceGeometricAsianPricingAsianGeometricPost,
  usePriceGeometricBasketPricingBasketGeometricPost,
  usePriceKikoPutPricingKikoPutPost,
  useSolveImpliedVolatilityPricingImpliedVolatilityPost,
} from "@/api/option_price";
import { isMockEnabled } from "@/config/env";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  formatCurrency,
  formatDecimal,
  formatPercentage,
} from "@/lib/formatters";
import { cn } from "@/lib/utils";

type ProductId =
  | "european"
  | "american"
  | "geometric_asian"
  | "arithmetic_asian"
  | "geometric_basket"
  | "arithmetic_basket"
  | "kiko_put"
  | "implied_volatility";

type FieldType = "number" | "select" | "toggle";
type FormValue = string | boolean;
type ProductFormState = Record<string, FormValue>;
type ProductForms = Record<ProductId, ProductFormState>;

type FieldDefinition = {
  name: string;
  label: string;
  type: FieldType;
  step?: string;
  min?: string;
  max?: string;
  suffix?: string;
  options?: Array<{ label: string; value: string }>;
};

type ProductDefinition = {
  id: ProductId;
  label: string;
  category: string;
  method: string;
  icon: typeof Activity;
  fields: FieldDefinition[];
};

type ResultMetric = {
  label: string;
  value: string;
  tone?: "default" | "positive" | "accent";
};

type RunResult = {
  productId: ProductId;
  title: string;
  headlineValue: string;
  headlineLabel: string;
  metrics: ResultMetric[];
  timestamp: string;
};

const optionTypeOptions = [
  { label: "Call", value: OptionTypeValues.call },
  { label: "Put", value: OptionTypeValues.put },
] satisfies Array<{ label: string; value: OptionType }>;

const RESULT_CARD_SLOTS = 3;

const productDefinitions: ProductDefinition[] = [
  {
    id: "european",
    label: "European",
    category: "Closed Form",
    method: "Black-Scholes benchmark",
    icon: ChartCandlestick,
    fields: [
      createSelectField("option_type", "Option Type", "Call or put payoff.", optionTypeOptions),
      createNumberField("spot", "Spot", "Current underlying spot.", "0.01"),
      createNumberField("strike", "Strike", "Contract strike price.", "0.01"),
      createNumberField("maturity", "Maturity", "Years to expiry.", "0.01"),
      createNumberField("rate", "Rate", "Risk-free annualized rate.", "0.0001"),
      createNumberField("volatility", "Volatility", "Annualized sigma.", "0.0001"),
      createNumberField(
        "dividend_yield",
        "Dividend Yield",
        "Continuous dividend carry.",
        "0.0001"
      ),
    ],
  },
  {
    id: "american",
    label: "American",
    category: "Lattice",
    method: "Binomial tree",
    icon: GitBranch,
    fields: [
      createSelectField("option_type", "Option Type", "Call or put payoff.", optionTypeOptions),
      createNumberField("spot", "Spot", "Current underlying spot.", "0.01"),
      createNumberField("strike", "Strike", "Contract strike price.", "0.01"),
      createNumberField("maturity", "Maturity", "Years to expiry.", "0.01"),
      createNumberField("rate", "Rate", "Risk-free annualized rate.", "0.0001"),
      createNumberField("volatility", "Volatility", "Annualized sigma.", "0.0001"),
      createNumberField(
        "dividend_yield",
        "Dividend Yield",
        "Continuous dividend carry.",
        "0.0001"
      ),
      createNumberField("steps", "Steps", "Tree depth for convergence.", "1", "1"),
    ],
  },
  {
    id: "geometric_asian",
    label: "Geometric Asian",
    category: "Closed Form",
    method: "Geometric average solution",
    icon: ChartSpline,
    fields: [
      createSelectField("option_type", "Option Type", "Call or put payoff.", optionTypeOptions),
      createNumberField("spot", "Spot", "Current underlying spot.", "0.01"),
      createNumberField("strike", "Strike", "Contract strike price.", "0.01"),
      createNumberField("maturity", "Maturity", "Years to expiry.", "0.01"),
      createNumberField("rate", "Rate", "Risk-free annualized rate.", "0.0001"),
      createNumberField("volatility", "Volatility", "Annualized sigma.", "0.0001"),
      createNumberField(
        "observations",
        "Observations",
        "Number of averaging points.",
        "1",
        "1"
      ),
    ],
  },
  {
    id: "arithmetic_asian",
    label: "Arithmetic Asian",
    category: "Monte Carlo",
    method: "Monte Carlo + control variate",
    icon: ChartColumnIncreasing,
    fields: [
      createSelectField("option_type", "Option Type", "Call or put payoff.", optionTypeOptions),
      createNumberField("spot", "Spot", "Current underlying spot.", "0.01"),
      createNumberField("strike", "Strike", "Contract strike price.", "0.01"),
      createNumberField("maturity", "Maturity", "Years to expiry.", "0.01"),
      createNumberField("rate", "Rate", "Risk-free annualized rate.", "0.0001"),
      createNumberField("volatility", "Volatility", "Annualized sigma.", "0.0001"),
      createNumberField(
        "observations",
        "Observations",
        "Number of averaging points.",
        "1",
        "1"
      ),
      createNumberField("paths", "Paths", "Monte Carlo path count.", "1", "2"),
      createNumberField("seed", "Seed", "Random seed for repeatability.", "1"),
      createToggleField(
        "use_control_variate",
        "Control Variate",
        "Use geometric Asian estimator to tighten error bands."
      ),
    ],
  },
  {
    id: "geometric_basket",
    label: "Geometric Basket",
    category: "Closed Form",
    method: "Basket analytical approximation",
    icon: Layers2,
    fields: basketFields(false),
  },
  {
    id: "arithmetic_basket",
    label: "Arithmetic Basket",
    category: "Monte Carlo",
    method: "Monte Carlo basket estimator",
    icon: Blocks,
    fields: basketFields(true),
  },
  {
    id: "kiko_put",
    label: "KIKO Put",
    category: "Exotic",
    method: "Monte Carlo barrier engine",
    icon: ShieldAlert,
    fields: [
      createNumberField("spot", "Spot", "Current underlying spot.", "0.01"),
      createNumberField("strike", "Strike", "Contract strike price.", "0.01"),
      createNumberField("maturity", "Maturity", "Years to expiry.", "0.01"),
      createNumberField("rate", "Rate", "Risk-free annualized rate.", "0.0001"),
      createNumberField("volatility", "Volatility", "Annualized sigma.", "0.0001"),
      createNumberField(
        "lower_barrier",
        "Lower Barrier",
        "Knock-in barrier.",
        "0.01",
        "0"
      ),
      createNumberField(
        "upper_barrier",
        "Upper Barrier",
        "Knock-out barrier.",
        "0.01",
        "0.01"
      ),
      createNumberField(
        "observations",
        "Observations",
        "Barrier monitoring count.",
        "1",
        "1"
      ),
      createNumberField("rebate", "Rebate", "Cash rebate paid on knock-out.", "0.01", "0"),
      createNumberField("paths", "Paths", "Monte Carlo path count.", "1", "2"),
      createNumberField("delta_shift", "Delta Shift", "Bump size for delta estimate.", "0.01", "0.01"),
    ],
  },
  {
    id: "implied_volatility",
    label: "Implied Vol",
    category: "Calibration",
    method: "Bisection solver",
    icon: CircleGauge,
    fields: [
      createSelectField("option_type", "Option Type", "Call or put payoff.", optionTypeOptions),
      createNumberField("premium", "Premium", "Observed option premium.", "0.01", "0.01"),
      createNumberField("spot", "Spot", "Current underlying spot.", "0.01"),
      createNumberField("strike", "Strike", "Contract strike price.", "0.01"),
      createNumberField("maturity", "Maturity", "Years to expiry.", "0.01"),
      createNumberField("rate", "Rate", "Risk-free annualized rate.", "0.0001"),
      createNumberField(
        "dividend_yield",
        "Dividend Yield",
        "Continuous dividend carry.",
        "0.0001"
      ),
      createNumberField(
        "initial_volatility",
        "Initial Sigma",
        "Starting point for the solver.",
        "0.0001",
        "0.0001"
      ),
      createNumberField("tolerance", "Tolerance", "Convergence tolerance.", "0.00000001", "0.00000001"),
      createNumberField("max_iterations", "Max Iterations", "Maximum bisection rounds.", "1", "1"),
      createNumberField(
        "volatility_lower_bound",
        "Lower Bound",
        "Solver lower search bound.",
        "0.000001",
        "0.000001"
      ),
      createNumberField(
        "volatility_upper_bound",
        "Upper Bound",
        "Solver upper search bound.",
        "0.0001",
        "0.0001"
      ),
    ],
  },
];

const defaultForms: ProductForms = {
  european: {
    spot: "100",
    strike: "100",
    maturity: "1",
    rate: "0.05",
    volatility: "0.2",
    dividend_yield: "0",
    option_type: OptionTypeValues.call,
  },
  american: {
    spot: "100",
    strike: "100",
    maturity: "1",
    rate: "0.05",
    volatility: "0.24",
    dividend_yield: "0.01",
    steps: "200",
    option_type: OptionTypeValues.put,
  },
  geometric_asian: {
    spot: "100",
    strike: "98",
    maturity: "1",
    rate: "0.04",
    volatility: "0.22",
    observations: "12",
    option_type: OptionTypeValues.call,
  },
  arithmetic_asian: {
    spot: "100",
    strike: "100",
    maturity: "1",
    rate: "0.04",
    volatility: "0.25",
    observations: "52",
    paths: "100000",
    seed: "42",
    use_control_variate: true,
    option_type: OptionTypeValues.call,
  },
  geometric_basket: {
    spot_1: "102",
    spot_2: "96",
    strike: "100",
    maturity: "1",
    rate: "0.04",
    volatility_1: "0.21",
    volatility_2: "0.27",
    correlation: "0.35",
    option_type: OptionTypeValues.call,
  },
  arithmetic_basket: {
    spot_1: "102",
    spot_2: "96",
    strike: "100",
    maturity: "1",
    rate: "0.04",
    volatility_1: "0.21",
    volatility_2: "0.27",
    correlation: "0.35",
    paths: "120000",
    seed: "42",
    use_control_variate: true,
    option_type: OptionTypeValues.call,
  },
  kiko_put: {
    spot: "100",
    strike: "95",
    maturity: "0.75",
    rate: "0.03",
    volatility: "0.28",
    lower_barrier: "78",
    upper_barrier: "118",
    observations: "180",
    rebate: "2.5",
    paths: "8192",
    delta_shift: "0.5",
  },
  implied_volatility: {
    premium: "11.4",
    spot: "100",
    strike: "100",
    maturity: "1",
    rate: "0.05",
    dividend_yield: "0",
    initial_volatility: "0.2",
    tolerance: "0.00000001",
    max_iterations: "200",
    volatility_lower_bound: "0.000001",
    volatility_upper_bound: "5",
    option_type: OptionTypeValues.call,
  },
};

export function OptionPricingDashboard() {
  const [selectedProductId, setSelectedProductId] = useState<ProductId>("european");
  const [forms, setForms] = useState<ProductForms>(defaultForms);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const healthQuery = useHealthHealthGet();
  const europeanMutation = usePriceEuropeanPricingEuropeanPost();
  const americanMutation = usePriceAmericanPricingAmericanPost();
  const geometricAsianMutation = usePriceGeometricAsianPricingAsianGeometricPost();
  const arithmeticAsianMutation = usePriceArithmeticAsianPricingAsianArithmeticPost();
  const geometricBasketMutation = usePriceGeometricBasketPricingBasketGeometricPost();
  const arithmeticBasketMutation = usePriceArithmeticBasketPricingBasketArithmeticPost();
  const kikoMutation = usePriceKikoPutPricingKikoPutPost();
  const impliedVolatilityMutation = useSolveImpliedVolatilityPricingImpliedVolatilityPost();

  const selectedProduct =
    productDefinitions.find((product) => product.id === selectedProductId) ??
    productDefinitions[0];
  const SelectedProductIcon = selectedProduct.icon;
  const activeForm = forms[selectedProductId];

  const isSubmitting =
    europeanMutation.isPending ||
    americanMutation.isPending ||
    geometricAsianMutation.isPending ||
    arithmeticAsianMutation.isPending ||
    geometricBasketMutation.isPending ||
    arithmeticBasketMutation.isPending ||
    kikoMutation.isPending ||
    impliedVolatilityMutation.isPending;

  function updateField(name: string, value: FormValue) {
    setForms((currentForms) => ({
      ...currentForms,
      [selectedProductId]: {
        ...currentForms[selectedProductId],
        [name]: value,
      },
    }));
  }

  async function handleSubmit() {
    setErrorMessage(null);

    try {
      const payload = buildPayload(selectedProduct, activeForm);
      const response = await submitProductRequest(selectedProductId, payload, {
        europeanMutation,
        americanMutation,
        geometricAsianMutation,
        arithmeticAsianMutation,
        geometricBasketMutation,
        arithmeticBasketMutation,
        kikoMutation,
        impliedVolatilityMutation,
      });

      if (response.status !== 200) {
        setErrorMessage(extractValidationMessage(response.data));
        return;
      }

      setRunResult(createRunResult(selectedProduct, response.data));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Request failed.");
    }
  }

  return (
    <main className="relative h-dvh overflow-hidden bg-background text-foreground">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_top_left,rgba(196,151,72,0.16),transparent_24%),radial-gradient(circle_at_90%_15%,rgba(27,85,122,0.28),transparent_28%),linear-gradient(180deg,rgba(7,12,24,0.94),rgba(3,8,18,1))]" />
      <div className="pointer-events-none fixed inset-0 opacity-[0.05] [background-image:linear-gradient(rgba(255,255,255,0.8)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.8)_1px,transparent_1px)] [background-size:72px_72px]" />

      <div className="relative mx-auto flex h-dvh max-w-[1500px] flex-col gap-4 overflow-hidden px-4 py-4 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-4 rounded-[28px] border border-white/10 bg-white/5 px-5 py-5 backdrop-blur-xl sm:flex-row sm:items-end sm:justify-between sm:px-6">
          <div className="space-y-2">
            <p className="text-[11px] uppercase tracking-[0.28em] text-primary/80">
              Quant Workstation
            </p>
            <h1 className="font-heading text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              Option Pricing Desk
            </h1>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <div className="inline-flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5 text-xs text-emerald-200">
              <Gauge className="size-3.5" />
              {healthQuery.data?.data.status ?? "loading"}
            </div>
            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-slate-950/35 px-3 py-1.5 text-xs text-slate-300">
              <Activity className="size-3.5" />
              {isMockEnabled ? "MSW Mock" : "Live API"}
            </div>
          </div>
        </header>

        <Card className="shrink-0 border-white/12 bg-slate-950/55">
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between gap-3">
              <CardTitle className="text-white">Pricing Engines</CardTitle>
              <div className="text-xs uppercase tracking-[0.24em] text-slate-500">Grid</div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
              {productDefinitions.map((product) => {
                const Icon = product.icon;
                const isActive = product.id === selectedProductId;

                return (
                  <button
                    key={product.id}
                    type="button"
                    onClick={() => setSelectedProductId(product.id)}
                    className={cn(
                      "cursor-pointer rounded-[18px] border px-4 py-3 text-left transition",
                      isActive
                        ? "border-primary/40 bg-primary/12 shadow-[0_0_0_1px_rgba(196,151,72,0.08)]"
                        : "border-white/8 bg-white/[0.03] hover:border-white/16 hover:bg-white/[0.05]"
                    )}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={cn(
                          "flex size-9 shrink-0 items-center justify-center rounded-2xl border",
                          isActive
                            ? "border-primary/30 bg-primary/15 text-primary"
                            : "border-white/10 bg-white/[0.04] text-slate-300"
                        )}
                      >
                        <Icon className="size-4" />
                      </div>
                      <div className="min-w-0">
                        <p className="truncate font-heading text-sm font-semibold text-white">
                          {product.label}
                        </p>
                        <p className="mt-1 truncate text-[10px] uppercase tracking-[0.18em] text-slate-500">
                          {product.method}
                        </p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </CardContent>
        </Card>

        <section className="grid min-h-0 flex-1 gap-4 xl:grid-cols-[0.92fr_1.08fr]">
          <div className="min-h-0">
            <Card className="flex h-full min-h-0 flex-col border-white/12 bg-slate-950/60">
              <CardHeader>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                  <div>
                    <CardTitle className="text-white">{selectedProduct.label} Inputs</CardTitle>
                    <p className="mt-2 text-xs uppercase tracking-[0.22em] text-slate-500">
                      {selectedProduct.method}
                    </p>
                  </div>
                  <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs uppercase tracking-[0.2em] text-slate-400">
                    <SelectedProductIcon className="size-3.5" />
                    {selectedProduct.label}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="flex min-h-0 flex-1 flex-col gap-4 overflow-hidden">
                <div className="grid min-h-0 flex-1 auto-rows-[104px] gap-4 overflow-auto pr-1 sm:grid-cols-2">
                  {selectedProduct.fields.map((field) => (
                    <div
                      key={field.name}
                      className={cn(
                        "space-y-2",
                        field.type === "toggle" && "sm:col-span-2"
                      )}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <label className="text-sm font-medium text-slate-100">
                          {field.label}
                        </label>
                        {field.suffix ? (
                          <span className="text-xs uppercase tracking-[0.2em] text-slate-500">
                            {field.suffix}
                          </span>
                        ) : null}
                      </div>
                      {renderField(field, activeForm[field.name], updateField)}
                    </div>
                  ))}
                </div>

                {errorMessage ? (
                  <div className="rounded-[20px] border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm leading-6 text-rose-100">
                    {errorMessage}
                  </div>
                ) : null}

                <Button
                  size="lg"
                  className="mt-auto h-12 w-full rounded-2xl bg-primary text-primary-foreground hover:bg-primary/90"
                  onClick={handleSubmit}
                  disabled={isSubmitting}
                >
                  {isSubmitting ? "Running valuation..." : `Run ${selectedProduct.label}`}
                </Button>
              </CardContent>
            </Card>
          </div>

          <div className="min-h-0">
            <Card className="flex h-full min-h-0 flex-col overflow-hidden border-primary/15 bg-[linear-gradient(135deg,rgba(10,16,30,0.96),rgba(12,26,42,0.92))]">
              <CardHeader className="relative overflow-hidden">
                <div className="absolute right-0 top-0 h-40 w-40 rounded-full bg-primary/12 blur-3xl" />
                <div className="absolute bottom-0 left-1/3 h-28 w-28 rounded-full bg-cyan-400/10 blur-3xl" />
                <div className="relative flex flex-col gap-5">
                  <div>
                    <p className="text-[11px] uppercase tracking-[0.28em] text-primary/80">
                      Output
                    </p>
                    <h2 className="mt-3 font-heading text-3xl font-semibold tracking-tight text-white sm:text-4xl">
                      {selectedProduct.label}
                    </h2>
                  </div>
                  <div className="grid gap-3 sm:grid-cols-2">
                    <DeskMetaRow label="Method" value={selectedProduct.method} />
                    <DeskMetaRow label="Category" value={selectedProduct.category} />
                  </div>
                </div>
              </CardHeader>
              <CardContent className="relative flex min-h-0 flex-1 flex-col overflow-auto">
                {runResult ? (
                  <div className="grid flex-1 gap-4 xl:grid-cols-[1.15fr_0.85fr]">
                    <div className="flex min-h-[260px] flex-col rounded-[26px] border border-white/10 bg-black/20 p-6">
                      <p className="text-xs uppercase tracking-[0.28em] text-primary/80">
                        {runResult.headlineLabel}
                      </p>
                      <p className="mt-4 font-heading text-5xl font-semibold text-white sm:text-6xl">
                        {runResult.headlineValue}
                      </p>
                      <p className="mt-auto pt-6 text-xs uppercase tracking-[0.24em] text-slate-500">
                        Last run {runResult.timestamp}
                      </p>
                    </div>

                    <div className="grid auto-rows-fr gap-3">
                      {toMetricSlots(runResult.metrics).map((metric, index) => (
                        <div
                          key={metric?.label ?? `metric-slot-${index}`}
                          className={cn(
                            "rounded-[22px] border p-5",
                            metric
                              ? "border-white/10 bg-white/[0.04]"
                              : "border-dashed border-white/6 bg-white/[0.015]"
                          )}
                        >
                          {metric ? (
                            <>
                              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                                {metric.label}
                              </p>
                              <p
                                className={cn(
                                  "mt-3 font-heading text-2xl font-semibold",
                                  metric.tone === "positive" && "text-emerald-300",
                                  metric.tone === "accent" && "text-primary",
                                  !metric.tone && "text-white"
                                )}
                              >
                                {metric.value}
                              </p>
                            </>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="grid flex-1 gap-4 lg:grid-cols-[1.15fr_0.85fr]">
                    <div className="flex min-h-[260px] flex-col rounded-[26px] border border-dashed border-white/15 bg-black/20 p-6">
                      <p className="text-xs uppercase tracking-[0.28em] text-primary/80">Ready</p>
                      <p className="mt-4 font-heading text-4xl font-semibold text-white">
                        Run a valuation.
                      </p>
                      <p className="mt-auto pt-6 text-xs uppercase tracking-[0.24em] text-slate-600">
                        Waiting for output
                      </p>
                    </div>
                    <div className="grid auto-rows-fr gap-3">
                      <SpotlightCard label="Product" value={selectedProduct.label} />
                      <SpotlightCard label="Category" value={selectedProduct.category} />
                      <SpotlightCard label="Routing" value={isMockEnabled ? "Mock" : "Live"} />
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </section>
      </div>
    </main>
  );
}

function renderField(
  field: FieldDefinition,
  value: FormValue | undefined,
  updateField: (name: string, value: FormValue) => void
) {
  if (field.type === "toggle") {
    return (
      <label className="flex items-center justify-between gap-4 rounded-[22px] border border-white/10 bg-white/[0.03] px-4 py-4">
        <span className="pr-4 text-sm leading-6 text-slate-300">{field.label}</span>
        <button
          type="button"
          role="switch"
          aria-checked={value === true}
          onClick={() => updateField(field.name, value !== true)}
          className={cn(
            "relative h-7 w-12 cursor-pointer rounded-full transition",
            value ? "bg-primary" : "bg-slate-700"
          )}
        >
          <span
            className={cn(
              "absolute left-1 top-1 size-5 rounded-full bg-white transition",
              value && "translate-x-5"
            )}
          />
        </button>
      </label>
    );
  }

  if (field.type === "select") {
    return (
      <div className="grid grid-cols-2 gap-2 rounded-[22px] border border-white/10 bg-white/[0.03] p-1">
        {field.options?.map((option) => {
          const isActive = String(value ?? "") === option.value;

          return (
            <button
              key={option.value}
              type="button"
              onClick={() => updateField(field.name, option.value)}
              className={cn(
                "h-10 cursor-pointer rounded-[16px] text-sm font-medium transition",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-slate-300 hover:bg-white/[0.05]"
              )}
            >
              {option.label}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <Input
      inputMode="decimal"
      value={String(value ?? "")}
      min={field.min}
      max={field.max}
      step={field.step}
      onChange={(event) => updateField(field.name, event.target.value)}
    />
  );
}

function createNumberField(
  name: string,
  label: string,
  _description: string,
  step: string,
  min?: string,
  max?: string,
  suffix?: string
): FieldDefinition {
  void _description;
  return { name, label, type: "number", step, min, max, suffix };
}

function createSelectField(
  name: string,
  label: string,
  _description: string,
  options: Array<{ label: string; value: string }>
): FieldDefinition {
  void _description;
  return { name, label, type: "select", options };
}

function createToggleField(
  name: string,
  label: string,
  _description: string
): FieldDefinition {
  void _description;
  return { name, label, type: "toggle" };
}

function basketFields(includeMonteCarloFields: boolean) {
  const sharedFields = [
    createSelectField("option_type", "Option Type", "Call or put payoff.", optionTypeOptions),
    createNumberField("spot_1", "Spot 1", "First asset spot level.", "0.01"),
    createNumberField("spot_2", "Spot 2", "Second asset spot level.", "0.01"),
    createNumberField("strike", "Strike", "Basket strike price.", "0.01"),
    createNumberField("maturity", "Maturity", "Years to expiry.", "0.01"),
    createNumberField("rate", "Rate", "Risk-free annualized rate.", "0.0001"),
    createNumberField("volatility_1", "Volatility 1", "Asset 1 annualized sigma.", "0.0001"),
    createNumberField("volatility_2", "Volatility 2", "Asset 2 annualized sigma.", "0.0001"),
    createNumberField("correlation", "Correlation", "Instantaneous asset correlation.", "0.01", "-1", "1"),
  ];

  if (!includeMonteCarloFields) {
    return sharedFields;
  }

  return [
    ...sharedFields,
    createNumberField("paths", "Paths", "Monte Carlo path count.", "1", "2"),
    createNumberField("seed", "Seed", "Random seed for repeatability.", "1"),
    createToggleField(
      "use_control_variate",
      "Control Variate",
      "Use geometric basket proxy to reduce variance."
    ),
  ];
}

function buildPayload(
  product: ProductDefinition,
  form: ProductFormState
) {
  const payload: Record<string, number | boolean | string> = {};

  for (const field of product.fields) {
    const rawValue = form[field.name];

    if (field.type === "toggle") {
      payload[field.name] = Boolean(rawValue);
      continue;
    }

    if (field.type === "select") {
      if (typeof rawValue !== "string" || rawValue.length === 0) {
        throw new Error(`Missing value for ${field.label}.`);
      }

      payload[field.name] = rawValue;
      continue;
    }

    if (typeof rawValue !== "string" || rawValue.trim().length === 0) {
      throw new Error(`Missing value for ${field.label}.`);
    }

    const parsedNumber = Number(rawValue);

    if (!Number.isFinite(parsedNumber)) {
      throw new Error(`${field.label} must be a valid number.`);
    }

    payload[field.name] = parsedNumber;
  }

  return payload;
}

async function submitProductRequest(
  productId: ProductId,
  payload: Record<string, number | boolean | string>,
  mutations: {
    europeanMutation: ReturnType<typeof usePriceEuropeanPricingEuropeanPost>;
    americanMutation: ReturnType<typeof usePriceAmericanPricingAmericanPost>;
    geometricAsianMutation: ReturnType<typeof usePriceGeometricAsianPricingAsianGeometricPost>;
    arithmeticAsianMutation: ReturnType<typeof usePriceArithmeticAsianPricingAsianArithmeticPost>;
    geometricBasketMutation: ReturnType<typeof usePriceGeometricBasketPricingBasketGeometricPost>;
    arithmeticBasketMutation: ReturnType<typeof usePriceArithmeticBasketPricingBasketArithmeticPost>;
    kikoMutation: ReturnType<typeof usePriceKikoPutPricingKikoPutPost>;
    impliedVolatilityMutation: ReturnType<
      typeof useSolveImpliedVolatilityPricingImpliedVolatilityPost
    >;
  }
) {
  switch (productId) {
    case "european":
      return mutations.europeanMutation.mutateAsync({ data: payload as never });
    case "american":
      return mutations.americanMutation.mutateAsync({ data: payload as never });
    case "geometric_asian":
      return mutations.geometricAsianMutation.mutateAsync({ data: payload as never });
    case "arithmetic_asian":
      return mutations.arithmeticAsianMutation.mutateAsync({ data: payload as never });
    case "geometric_basket":
      return mutations.geometricBasketMutation.mutateAsync({ data: payload as never });
    case "arithmetic_basket":
      return mutations.arithmeticBasketMutation.mutateAsync({ data: payload as never });
    case "kiko_put":
      return mutations.kikoMutation.mutateAsync({ data: payload as never });
    case "implied_volatility":
      return mutations.impliedVolatilityMutation.mutateAsync({ data: payload as never });
  }
}

function createRunResult(
  product: ProductDefinition,
  data:
    | { price: number }
    | {
        price: number;
        std_error: number;
        confidence_interval: { lower: number; upper: number };
      }
    | {
        price: number;
        delta: number;
        std_error: number;
        confidence_interval: { lower: number; upper: number };
      }
    | { implied_volatility: number }
): RunResult {
  const timestamp = new Intl.DateTimeFormat("en-US", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date());

  if ("implied_volatility" in data) {
    return {
      productId: product.id,
      title: product.label,
      headlineValue: formatPercentage(data.implied_volatility),
      headlineLabel: "Implied Volatility",
      metrics: [
        {
          label: "Annualized Sigma",
          value: formatDecimal(data.implied_volatility),
          tone: "accent",
        },
        {
          label: "Vol In Percent",
          value: formatPercentage(data.implied_volatility),
        },
        {
          label: "Desk Read",
          value:
            data.implied_volatility > 0.35 ? "High premium" : "Contained premium",
          tone: data.implied_volatility > 0.35 ? "positive" : "default",
        },
      ],
      timestamp,
    };
  }

  const metrics: ResultMetric[] = [
    {
      label: "Model Price",
      value: formatCurrency(data.price),
      tone: "accent",
    },
  ];

  if ("std_error" in data) {
    metrics.push({
      label: "Std Error",
      value: formatDecimal(data.std_error),
    });
    metrics.push({
      label: "95% CI",
      value: `${formatCurrency(data.confidence_interval.lower)} to ${formatCurrency(data.confidence_interval.upper)}`,
    });
  }

  if ("delta" in data) {
    metrics.push({
      label: "Delta",
      value: formatDecimal(data.delta),
      tone: data.delta < 0 ? "positive" : "default",
    });
  }

  return {
    productId: product.id,
    title: product.label,
    headlineValue: formatCurrency(data.price),
    headlineLabel: product.label,
    metrics,
    timestamp,
  };
}

function extractValidationMessage(data: HTTPValidationError | unknown) {
  if (!data || typeof data !== "object" || !("detail" in data)) {
    return "The API rejected the request.";
  }

  const details = data.detail;

  if (!Array.isArray(details) || details.length === 0) {
    return "The API rejected the request.";
  }

  return details
    .map((detail) => {
      if (!detail || typeof detail !== "object") {
        return null;
      }

      const path =
        "loc" in detail && Array.isArray(detail.loc)
          ? detail.loc.join(".")
          : "field";
      const message = "msg" in detail ? detail.msg : "Invalid input";

      return `${path}: ${message}`;
    })
    .filter(Boolean)
    .join(" | ");
}

function DeskMetaRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="grid grid-cols-[88px_minmax(0,1fr)] items-center gap-3 rounded-[18px] border border-white/10 bg-white/[0.04] px-4 py-3">
      <p className="text-[11px] uppercase tracking-[0.22em] text-slate-500">{label}</p>
      <p className="truncate text-sm text-right leading-6 text-slate-100">{value}</p>
    </div>
  );
}

function SpotlightCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-[22px] border border-white/10 bg-white/[0.04] p-5">
      <p className="text-xs uppercase tracking-[0.22em] text-slate-500">{label}</p>
      <p className="mt-3 text-sm leading-7 text-slate-200">{value}</p>
    </div>
  );
}

function toMetricSlots(metrics: ResultMetric[]) {
  return Array.from({ length: RESULT_CARD_SLOTS }, (_, index) => metrics[index] ?? null);
}
