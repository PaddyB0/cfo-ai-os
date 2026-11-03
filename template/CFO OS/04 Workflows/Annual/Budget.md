# Budget

<!-- cfo-os:template begin body -->
## Trigger

The budget timetable in `01 Context/Calendar.md`, usually in the last quarter of the fiscal year, for the year that follows.

## Inputs

- The current forecast cycle for the year now ending, as the base: actuals to the reference month plus the forecast after it.
- {{scenario.budget}} for the year now ending, for comparison.
- Assumptions from each budget holder, saved in `Inputs/` as received.
- The hypotheses and standard analyses in the instructions.
- The strategy or targets the board has set, from `07 Library` or `03 Memory/Decisions.md`.

## Steps

1. Create the year folder `05 Periods/<FYyyyy>/` for the year being budgeted, with its four parts, if it does not exist.
2. Set out the timetable: assumptions due, first draft, review rounds, board approval. Agree it with the CFO.
3. Build the base from the current year's outlook, taking out one-off items named in `02 Rules and style/Rules.md`.
4. Collect the assumptions from each budget holder and check each one against the current run rate. Flag any that step up or down without a reason.
5. Build the budget by month: revenue, cost of sales, operating expenses by department, headcount, capital spend and cash.
6. Build the cash flow and check the runway and any covenant through the budget year.
7. Compare the draft with the current year outlook and with the board's targets, in the variance table format.
8. Record each review round's changes and who asked for them.
9. When the board approves, propose the update to the budget name in `01 Context/Data.md` once the budget is loaded in the connector.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- Every assumption has an owner and a date.

## Output

The budget pack for the board, the assumptions book, and the monthly phasing ready to load.

## Where it is filed

Drafts and assumptions in `05 Periods/<FYyyyy>/Working/`, the approved budget in `Outputs/`, a line in `Log.md`. The approval goes to `03 Memory/Decisions.md`.
<!-- cfo-os:template end body -->

## Your notes

