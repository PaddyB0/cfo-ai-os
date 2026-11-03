# Board pack

<!-- cfo-os:template begin body -->
## Trigger

The board meeting date in `01 Context/Calendar.md`, counting back by the time the board needs the pack. The last month of the quarter must be closed first.

## Inputs

- The management accounts for each month of the quarter, from their `Outputs/` folders.
- {{scenario.actuals}} to the quarter end, {{scenario.budget}}, and the current and previous forecast cycles.
- {{metric.board_revenue}}, {{metric.closing_cash}}, {{metric.cash_movement}} and {{metric.headcount}}.
- The latest cash runway and forecast critique.
- The last board pack, its minutes and actions, from the previous quarter's `Outputs/` or `07 Library`.
- `03 Memory/Key findings.md` and open questions that the board should hear about.

## Steps

1. Create the quarter folder `05 Periods/<year>/<yyyy-Qn>/` with its four parts, if it does not exist.
2. Build each section of the board pack template in order, using the same layout as the last pack.
3. Read quarter values correctly: flow metrics are the sum of the three months; end-of-period metrics, such as cash and headcount, are the value at the last month of the quarter.
4. Compare with budget and the previous cycle in the variance table format, and explain each material variance.
5. Show the full-year outlook as actuals to the quarter end plus the current cycle after it.
6. Check every figure in the pack against the management accounts for the same months. Any difference is explained or fixed.
7. Report progress on each action from the last board.
8. Draft the decisions the board is asked to take, each with a recommendation.
9. Save the draft in `Working/` and list what the CFO needs to review.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- Board revenue is {{metric.board_revenue}} throughout, with no other revenue measure shown as revenue.

## Output

The finance section of the board pack in the board pack template.

## Where it is filed

Drafts in `05 Periods/<year>/<yyyy-Qn>/Working/`, the pack as sent in `Outputs/`, a line in `Log.md`. Decisions the board takes go to `03 Memory/Decisions.md` after the meeting.
<!-- cfo-os:template end body -->

## Your notes

