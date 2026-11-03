# Cash runway

<!-- cfo-os:template begin body -->
## Trigger

A month closes, a new forecast cycle is loaded, or the CFO, the board or a lender asks how long the cash lasts.

## Inputs

- {{metric.closing_cash}} from {{scenario.actuals}} at the reference month in `01 Context/Data.md`.
- {{metric.cash_movement}} from the current forecast cycle for each month after the reference month.
- The minimum cash level or covenant headroom in `02 Rules and style/Rules.md`, if one is set.
- Any facility or funding not yet in the forecast, from `07 Library` or `03 Memory/Decisions.md`.

## Steps

If the cash-runway skill is installed, use it for steps 3 to 6, so the arithmetic is done by its script and is the same every time.

1. Read closing cash at the reference month from actuals. It is an end-of-period figure: take the balance at that month, never a sum.
2. Read the forecast cash movement for each month after the reference month from the current cycle. Name the cycle.
3. Build the projection month by month: each month's closing cash is the previous month's closing cash plus that month's forecast movement.
4. Check the projection against the forecast's own closing cash for the same months, if the forecast has one. Explain any difference.
5. Find the runway: the first month in which projected cash falls below zero, or below the minimum level if one is set. If it does not fall below within the forecast horizon, say so and give the lowest point.
6. Show the effect of the main sensitivities the CFO cares about, such as revenue lower by a stated share or a hire plan delayed, as separate lines, marked as worked out.
7. Compare with the runway in the previous cycle and explain the change.
8. Draft the output and save it in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- The opening balance is actuals at the reference month, and every later month comes from one cycle only.

## Output

A short memo with a month-by-month cash table and the runway stated as a month, plus the change since the previous cycle.

## Where it is filed

Drafts in `05 Periods/<year>/<month>/Working/`, the final in `Outputs/`, a line in that month's `Log.md`. The runway month goes to `03 Memory/Key findings.md` at session close.
<!-- cfo-os:template end body -->

## Your notes

