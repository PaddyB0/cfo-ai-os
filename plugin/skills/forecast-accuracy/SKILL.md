---
name: forecast-accuracy
description: Measures how good the previous forecast was on the months that have since closed (net error, WAPE, bias, optimistic or cautious), flags where the new forecast steps away from the recent run rate, and builds the full year by splicing actuals to the reference month with the current cycle after it, each month from one source only. Use when a new forecast cycle is loaded or a month closes and a CFO asks whether the forecast still holds, how accurate the last forecast was, whether the forecast is too optimistic, for a forecast critique or reforecast review, or for the latest full-year outlook against budget. Not for a plain budget-versus-actual table (use variance-analysis) or for cash runway (use cash-runway).
---

# Forecast accuracy

The numbers are worked out by `scripts/accuracy.py`. It refuses inputs that would double count, such as actuals after the reference month or a full-year month with no source, because a spliced full year that adds actuals and forecast for the same month is the commonest silent error in a reforecast.

## 1. Settle the inputs before reading any figure

- **Reference month**: the last closed month.
- **Previous cycle**: the forecast being judged. Its months up to the reference month are compared with actuals.
- **Current cycle**: the forecast being reviewed. Its months after the reference month build the full year and the run-rate check.
- **Full-year months**: the fiscal year, as yyyy-mm months.
- **Sign convention**: `natural` (revenue positive, costs negative) or `costs_positive`.
- **Step threshold**: how large a change from run rate needs explaining. The default is 15%.

In a CFO OS folder, the reference month, cycles and cycle rule are in `01 Context/Data.md`, the sign convention in `02 Rules and style/Rules.md`, and the steps and filing in `04 Workflows/Monthly/Forecast critique.md`. Follow the workflow; this skill does its steps 2, 3 and 5. Elsewhere, ask, and say what you assumed.

## 2. Read the figures

For each line (board revenue, operating costs, closing cash, and any line the CFO tracks), read monthly values, one query per scenario and cycle:

1. Actuals from the start of the fiscal year (or of the comparison) to the reference month.
2. The previous cycle for the same closed months.
3. The current cycle for the months after the reference month to the end of the fiscal year.
4. The budget full year and, if wanted, the previous cycle's full year.

Balance lines (cash, debt, headcount, customers) get type `balance`: the script reads them at a month, never sums them.

## 3. Run the script

Write the inputs to a JSON file in the working folder, then run the script from this skill's own folder, the base directory given when the skill loads (for example `/mnt/skills/user/forecast-accuracy` in the Claude apps), not from the working folder:

```
python "<skill folder>/scripts/accuracy.py" accuracy-input.json
```

Shape:

```json
{
  "reference_month": "yyyy-mm",
  "full_year_months": ["yyyy-mm", "..."],
  "sign_convention": "natural",
  "step_change_percent": 15,
  "run_rate_months": 3,
  "actual_label": "Actuals", "prior_label": "Forecast <previous cycle>",
  "current_label": "Forecast <current cycle>", "budget_label": "Budget",
  "currency": "GBP", "unit": "thousands",
  "lines": [
    {"line": "Revenue", "type": "revenue",
     "actuals": {"yyyy-mm": 0}, "prior_forecast": {"yyyy-mm": 0}, "current_forecast": {"yyyy-mm": 0},
     "budget_full_year": 0, "prior_full_year": 0}
  ]
}
```

`examples/input.example.json` is a complete fictional example. Exit code 1 means the input broke a rule: fix the input, do not work around it.

## 4. Read the results, then write up

- **WAPE** says how far off the forecast was month by month. **Bias** says whether it leaned one way. A low bias with a high WAPE means timing errors that cancel out. A bias that is "optimistic" for several cycles running is a finding for `Key findings` and a question for the forecast owner.
- **Steps from run rate** are where the current cycle departs from what the business has just been doing. Each one needs a named reason (a price rise, a new contract, a hire plan, seasonality) and an owner. A step without a reason is a weak assumption: list it with the figure that makes it look weak.
- **Full year** shows its split (for example 6+6) and its basis. Variances are full year less budget, and less the previous cycle.

State the reference month, both cycles and the sign convention in the output, keep the script's figures as they are, and end with the questions for each assumption owner.
