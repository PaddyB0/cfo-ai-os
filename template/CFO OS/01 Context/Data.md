# Data

What is connected, what each scenario is called, where actuals end, and which metric plays which role.

## Connector

Claude reads figures from {{connector.name}}, read-only. Connector guide in the template's docs: {{connector.guide}}.

## Scenarios

| Role | Name in the connector |
|---|---|
| Actuals | {{scenario.actuals}} |
| Budget | {{scenario.budget}} |
| Forecast | {{scenario.forecast}} |
| Current forecast cycle | {{scenario.current_forecast_cycle}} |

How a forecast cycle is chosen in a query: {{scenario.cycle_rule}}

## Reference month

The last closed month is {{data.reference_month}}.

Actuals run up to and including this month. The current forecast cycle runs after it. When a month closes and a new cycle is loaded, update this line and the current forecast cycle above, and log the change in `03 Memory/Decisions.md`.

## Metric roles

| Role | Metric |
|---|---|
| Board revenue | {{metric.board_revenue}} |
| Gross revenue | {{metric.gross_revenue}} |
| Closing cash | {{metric.closing_cash}} |
| Cash movement | {{metric.cash_movement}} |
| Operating expenses | {{metric.operating_expenses}} |
| Headcount | {{metric.headcount}} |

A role marked "not mapped" has no metric yet. Claude declines questions that need it.

## Limits

What the connected data cannot answer:

{{data.limits}}

## Metric catalogue

`Metric catalogue.md` in this folder is generated from the connector's metric list. It is never edited by hand. To refresh it, regenerate it from a new metric list.
