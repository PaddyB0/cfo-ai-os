# Forecast critique

<!-- cfo-os:template begin body -->
## Trigger

A new forecast cycle is loaded, or a month closes and the CFO wants to know whether the current forecast still holds.

## Inputs

- {{metric.board_revenue}}, {{metric.operating_expenses}} and {{metric.closing_cash}}, plus any other lines named in the standard analyses in the instructions.
- {{scenario.actuals}} up to and including the reference month in `01 Context/Data.md`.
- The current forecast cycle, {{scenario.current_forecast_cycle}} at deploy, and the previous cycle, chosen by the cycle rule in `Data.md`.
- {{scenario.budget}}.
- The hypotheses in the instructions, and `03 Memory/Key findings.md`.

## Steps

1. Confirm the reference month and the current and previous cycles. Name them before showing any figure.
2. For the months just closed, compare actuals with what the previous cycle forecast for them. This shows how good the last forecast was.
3. For the full year, compare the current cycle with the previous cycle and with the budget, in the variance table format. The full year is actuals to the reference month plus the current cycle after it.
4. For each material variance, find what drove it: volume, price, timing, one-off items, or a change in assumption. Slice by dimension to find where it sits.
5. Look at the run rate. Compare the forecast for the next three months with the average of the last three months of actuals, and flag any step change the forecast does not explain.
6. Test each standing hypothesis against the figures and say whether it still holds.
7. List the assumptions in the forecast that look weak, each with the figure that makes it look so, and a question for its owner.
8. Draft the critique as a management memo and save it in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- No month adds actuals and forecast together.

## Output

A management memo with a variance table, addressed as the instructions say, that ends with the questions for each assumption owner.

## Where it is filed

Drafts in `05 Periods/<year>/<month>/Working/`, the final in `Outputs/`, a line in that month's `Log.md`. Weak assumptions go to `03 Memory/Open questions.md` at session close.
<!-- cfo-os:template end body -->

## Your notes

