# Management accounts

<!-- cfo-os:template begin body -->
## Trigger

Monthly. The month-end close is signed off and the reference month in `Shared/Claude/Data.md` has moved on.

## Inputs

- {{scenario.actuals}} for the month and the year to date.
- {{scenario.budget}} and the current forecast cycle for the same periods.
- {{metric.board_revenue}}, {{metric.operating_expenses}}, {{metric.closing_cash}}, {{metric.headcount}}, and the other lines in the management accounts template.
- The close tie-out in the month's `Outputs/` folder.
- Last month's management accounts, for comparison.

## Steps

1. Confirm the month is closed and the reference month matches it.
2. Build the income statement for the month, the year to date and the full-year outlook, against budget and the current cycle, in the variance table format.
3. Build the balance sheet at the month end and the previous month end. Read every balance at the period end; never sum balances over months.
4. Build the cash flow from opening to closing cash, and check that closing cash ties to the balance sheet.
5. Work out the key measures. Mark each one that is worked out rather than read, and show the formula.
6. Write the commentary: only variances above materiality, each with its driver.
7. Compare with last month's accounts and explain any figure for an earlier month that has changed.
8. Draft the pack in the management accounts template and save it in `Working/`.

## Checks every output carries

- Each figure ties to its source, or the output says it does not and why.
- The scenario and, for a forecast, the cycle are stated.
- Each figure has a source: metric, scenario, cycle and period, or the file it came from.
- The sign convention is named for every table.
- The balance sheet balances and closing cash agrees between the balance sheet and the cash flow.

## Output

The management accounts in the template, as {{output.default_format}} unless the person asks otherwise.

## Where it is filed

Drafts in `Periods/<year>/<yyyy-mm>/Working/` in your tier, the final as sent in `Outputs/`, a line in its log.
<!-- cfo-os:template end body -->

## Your notes

