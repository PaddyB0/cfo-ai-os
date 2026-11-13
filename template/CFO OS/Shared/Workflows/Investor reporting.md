# Investor reporting

<!-- cfo-os:template begin body -->
## Trigger

Quarterly. The investor or lender reporting date in `Shared/Claude/Calendar.md`, usually after the quarter's board pack.

## Inputs

- The board pack for the same quarter, from its `Outputs/` folder.
- The last investor update, so this one keeps the same figures in the same order.
- Any reporting covenant or information right in the documents in `Shared/Library`.
- {{metric.board_revenue}}, {{metric.closing_cash}} and the runway.

## Steps

1. Check which figures were promised to investors or lenders and in what form. Use the same definitions as last time, and say if any has changed.
2. Take every figure from the board pack or the management accounts already sent. Do not read new figures from the connector unless the CFO asks, so investors and the board see the same numbers.
3. If a covenant applies, work out each covenant measure, show the calculation, and state the headroom. Mark it as worked out.
4. Draft the update in the investor update template.
5. List what the update leaves out compared with the board pack, so the CFO can confirm it is intended.
6. Save the draft in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- Every figure agrees with the board pack for the same period.

## Output

The investor update and, where it applies, the covenant calculation.

## Where it is filed

Drafts in `Periods/<year>/<yyyy-Qn>/Working/` in your tier, the update as sent in `Outputs/`, a line in its log.
<!-- cfo-os:template end body -->

## Your notes

