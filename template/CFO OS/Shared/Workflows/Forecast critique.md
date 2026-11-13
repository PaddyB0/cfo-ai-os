# Forecast critique

<!-- cfo-os:template begin body -->
## Trigger

Monthly. A new forecast cycle is loaded, or a month closes and the person wants to know whether the current forecast still holds.

## Inputs

- {{metric.board_revenue}}, {{metric.operating_expenses}} and {{metric.closing_cash}}, plus any other lines named in the standard analyses in the instructions.
- {{scenario.actuals}} up to and including the reference month in `Shared/Claude/Data.md`.
- The current forecast cycle, {{scenario.current_forecast_cycle}} at deploy, and the previous cycle, chosen by the cycle rule in `Data.md`.
- {{scenario.budget}}.
- The hypotheses in the instructions, and `Memory/Now.md` in your tier.

## Steps

If the forecast-accuracy skill is installed, use it for steps 2, 3 and 5, and the variance-analysis skill for the variance table, so the arithmetic is done by their scripts.

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

Drafts in `Periods/<year>/<month>/Working/` in your tier, the final in `Outputs/`, a line in that month's log. When the work is done, propose the weak assumptions as Question lines for `Memory/Log.md` in your tier.
<!-- cfo-os:template end body -->

## Your notes

