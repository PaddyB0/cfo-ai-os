---
name: cash-runway
description: Projects closing cash month by month from an actual opening balance and one forecast cycle, finds the month cash falls below zero or a minimum level, checks the projection against the forecast's own closing cash, compares with trailing burn and runs sensitivities. Use when a CFO or finance lead asks how long the cash lasts, when the money runs out, for runway or months of cash, for a cash projection after a month closes or a new forecast loads, or what a revenue shortfall or hiring delay does to runway. Not for a 13-week receipts and payments forecast, and not for variance commentary on a cash line (use variance-analysis).
---

# Cash runway

The arithmetic is done by `scripts/runway.py`, never by hand, so the same inputs always give the same runway. Your job is to gather the right inputs, run the script, read its checks and write the result up.

## 1. Settle the inputs before reading any figure

- **Reference month**: the last closed month. Actuals stop there.
- **Opening balance**: closing cash at the reference month, from actuals. It is a balance: read the value at that month, never a sum of months.
- **Forecast cycle**: one cycle for every month after the reference month. Name it.
- **Floor**: zero, or the minimum cash level or covenant headroom the business has set.
- **Previous runway**, if one was reported, with its cycle, so the change can be explained.

In a CFO OS folder, the reference month and cycle rule are in `01 Context/Data.md`, the floor and sign convention in `02 Rules and style/Rules.md`, the steps and filing in `04 Workflows/Monthly/Cash runway.md`, and the previous runway in `03 Memory/Key findings.md`. Follow the workflow; this skill does its steps 3 to 6. Elsewhere, ask for anything not given, and say what you assumed.

## 2. Read the figures

From the finance data connector, or from the file the user gives:

1. Closing cash at the reference month, actuals.
2. Net cash movement for each month after the reference month, from the one forecast cycle, with no gap. If the forecast has no cash-movement line, use the month-to-month change in its closing cash and say so.
3. The forecast's own closing cash for the same months, if it has one. The script ties to it.
4. Net cash movement for the last three to six closed months, from actuals, for the burn check.

Never mix actuals and forecast in one month. Never let a connector choose a scenario or cycle without naming it.

## 3. Run the script

Write the inputs to a JSON file in the working folder, then run the script from this skill's own folder, the base directory given when the skill loads (for example `/mnt/skills/user/cash-runway` in the Claude apps), not from the working folder:

```
python "<skill folder>/scripts/runway.py" runway-input.json
```

Shape (amounts are inflows positive, outflows negative; the script rejects gaps, duplicate months, a month at or before the opening, and movements from more than one source):

```json
{
  "currency": "GBP", "unit": "thousands",
  "opening": {"month": "yyyy-mm", "balance": 0, "source": "Actuals, closing cash"},
  "minimum_cash": 0,
  "movements": [{"month": "yyyy-mm", "amount": 0, "source": "Forecast, <cycle>"}],
  "forecast_closing": [{"month": "yyyy-mm", "balance": 0}],
  "trailing_actual_movements": [{"month": "yyyy-mm", "amount": 0}],
  "sensitivities": [
    {"name": "Receipts 10% lower", "adjustments": [{"month": "yyyy-mm", "amount": 0}]},
    {"name": "Extra monthly cost", "monthly": 0}
  ],
  "previous": {"cycle": "<previous cycle>", "runway_month": "yyyy-mm"},
  "tie_tolerance": 0.5
}
```

Only `opening` and `movements` are required. `examples/input.example.json` is a complete fictional example. Add `--json` for machine-readable output and `--decimals 1` for more precision. Exit code 1 means the input broke a rule: fix the input, do not work around it.

## 4. Read the checks, then write up

- **Runway month** is the first month projected cash is below the floor. An opening balance already below it is reported as a breach in the opening month, whatever the forecast does next. "Months covered" counts the full months before it. If it never falls below, report the lowest point instead of a runway date, and say the horizon ends.
- **Tie to forecast closing cash.** A month that does not tie means the movement line and the balance disagree. Explain it before you use the runway: a non-cash item in the movement, a balance-sheet movement left out, or timing.
- **Trailing burn check.** If burn-based months of cash differ a lot from the forecast runway, the forecast assumes a change in burn. Name the change and who owns it.
- **Sensitivities** are worked out, not data. Label them so, and say what each assumes.

The output states: the opening balance and its source, the cycle, the floor, the sign convention, the month-by-month table, the runway month or lowest point, the change since the previous cycle with its reason, and any tie that failed. Use the script's tables as they are; do not retype figures.
