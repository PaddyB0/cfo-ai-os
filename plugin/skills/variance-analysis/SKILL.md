---
name: variance-analysis
description: Builds a variance table (actual against budget, actual against forecast, or one forecast cycle against another) with favourable or adverse marked correctly for the sign convention, materiality applied, totals tied to their lines and, where volumes and prices exist, a price, volume and mix bridge that adds up exactly. Use when a CFO or finance lead asks for budget versus actual, a variance table or commentary, why revenue or a cost line is over or under plan, a price-volume-mix or PVM analysis, or a bridge between two scenarios for management accounts or a board pack. Not for whether a forecast was accurate over closed months (use forecast-accuracy) or for cash runway (use cash-runway).
---

# Variance analysis

The arithmetic and the favourable or adverse calls are done by `scripts/variance.py`. Sign mistakes are the commonest error in variance work: a cost overrun reported as favourable reads as good news. The script decides direction from the line type and the sign convention, so you do not.

## 1. Settle the comparison before reading any figure

- **What against what**: actual against budget, actual against a forecast cycle, or current cycle against previous cycle. Name the scenario and, for a forecast, the cycle on each side.
- **Period**: a month, a quarter, year to date or full year. Both sides cover the same period.
- **Sign convention**: `natural` (revenue positive, costs negative, the usual connector sign) or `costs_positive` (costs shown as positive numbers, the usual management-accounts layout). Use the one the figures are actually in.
- **Materiality**: an absolute amount, a percentage, or both, and whether a line must pass `either` or `both`.

In a CFO OS folder, the sign convention and materiality are in `02 Rules and style/Rules.md`, the table layout in `02 Rules and style/Templates/Variance table.md`, and the scenario and cycle rules in `01 Context/Data.md`. Elsewhere, ask, and say what you assumed.

## 2. Read the figures

One query per scenario and cycle, by line, for the same period and the same dimension filters. End-of-period lines (cash, debt, headcount, customers) are read at the period end, never summed over months: give them type `balance`. If the user wants price, volume and mix, also read volume and average price per product, customer group or region, on both sides.

## 3. Run the script

Write the inputs to a JSON file in the working folder, then run the script from this skill's own folder, the base directory given when the skill loads (for example `/mnt/skills/user/variance-analysis` in the Claude apps), not from the working folder:

```
python "<skill folder>/scripts/variance.py" variance-input.json
```

Shape:

```json
{
  "current_label": "Actual", "comparator_label": "Budget",
  "currency": "GBP", "unit": "thousands",
  "sign_convention": "natural",
  "materiality": {"absolute": 25, "percent": 10, "rule": "either"},
  "lines": [
    {"line": "Revenue", "type": "revenue", "current": 0, "comparator": 0, "source": "metric, scenario, cycle, period"},
    {"line": "Payroll", "type": "cost", "current": 0, "comparator": 0, "source": "...", "comment": "driver, if known"},
    {"line": "Headcount", "type": "balance", "current": 0, "comparator": 0, "favourable_when": "lower"}
  ],
  "totals": [{"line": "Gross profit", "of": ["Revenue", "Cost of sales"], "current": 0, "comparator": 0}],
  "pvm": {"line": "Revenue", "items": [
    {"name": "Product A", "current_volume": 0, "current_price": 0, "comparator_volume": 0, "comparator_price": 0}
  ]}
}
```

Line types are `revenue`, `cost`, `balance` and `other`. A `balance` or `other` line gets no favourable or adverse call unless you set `favourable_when`. A total of cost lines alone is read like a cost. Any other total is favourable when higher. Set `favourable_when` on a total to override either. With `costs_positive`, a total that holds both revenue and cost lines subtracts the costs, and any other total adds its lines. Under `natural`, a positive cost is rejected as a sign error. `examples/input.example.json` is a complete fictional example. Exit code 1 means the input broke a rule: fix the input.

## 4. Read the checks, then write up

- **A total that does not tie** to its lines means a line is missing or a sign is wrong. Fix it or name what is left out. Never send a table whose totals do not add.
- **Material lines that need a driver comment** are listed. Each comment says what drove the difference (volume, price, mix, timing, a one-off, a change in assumption), with the figure that shows it, not that a difference exists. Slice by dimension to find where it sits.
- **Price, volume and mix**: the three effects add up exactly to the change in price times volume. Volume is the change in total units at the comparator's average price, mix is the shift between items at comparator prices, and price is the change in price on current volume. If price times volume does not equal the reported line, show the gap as "not in volume data" (discounts, credits, other income). Do not spread it across the effects.

The output uses the variance table layout, names both scenarios and cycles in the column headings, states the sign convention and what F means under the table, and keeps the script's figures as they are.
