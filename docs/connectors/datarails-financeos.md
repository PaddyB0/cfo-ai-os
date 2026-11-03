# Connector guide: Datarails FinanceOS

How to use the CFO OS with the Datarails FinanceOS connector for Claude. This guide is written from public knowledge of the connector and the descriptions of its own tools. It is general advice, not a description of any company's setup. Tool names change between connector versions; if one named here is missing, ask Claude to list the connector's tools and use the nearest match.

This is a personal project. It is not an official Datarails product and is not supported by Datarails. For help with the connector itself, use the Datarails support site.

## What the connector exposes

- **Business metrics.** Named measures, each with a numeric id, a name, a category, and often a description. Some are base metrics read from the data; others are calculated from other metrics with a formula.
- **Time aggregation.** Each metric says how it rolls up over time. Most sum over months. Balances and counts roll up as end of period, so a quarter returns the last month's value. Read this before answering for a quarter or a year.
- **Scenarios and scenario cycles.** Actuals, budgets and forecasts are scenarios. A forecast is re-cut in cycles, usually named for months of actuals plus months of forecast. The connector reports default scenarios for each fiscal year; a query without a scenario filter gets the default.
- **Dimensions.** Metrics can be filtered and split by dimensions such as entity, department or account. Each metric lists the dimensions it supports.
- **Aggregation tools.** For questions the business metrics do not cover, the connector can aggregate the underlying tables directly. These are slower and closer to the raw data, so prefer a business metric where one exists.
- **Organisation context.** A summary of the fiscal year, currencies and default scenarios.

## Setting up Data.md

1. Ask Claude to read the organisation context and report the fiscal year, the currencies and the default scenarios. Use these for `company.fiscal_year`, `company.reporting_currency` and the `scenario` answers.
2. Ask Claude to list the business metrics and find the ones that play each role: board revenue, gross revenue, closing cash, cash movement, operating expenses, headcount. Write each role as the metric's name with its id, for example `Net Revenue (id 101)`, in the answers file.
3. Check each role's time roll-up. Closing cash and headcount should be end of period. If they are not, record it under `data.limits`.
4. Ask a few of the test questions before deploying, to see how scenario cycles are named. Write the rule as `scenario.cycle_rule`.

## Getting the metric list for the catalogue

The metric catalogue is generated from the connector's own metric list.

1. In Claude, with the connector on, ask: "Call the connector's metric-list tool, list_business_metrics, for all metrics, and give me the full JSON it returns, unchanged."
2. Save that JSON as `metrics.json`, somewhere private.
3. Deploy with `--metrics metrics.json --metrics-from datarails`, or regenerate the catalogue in an existing folder:

```
cfo-os catalogue metrics.json --from datarails > "Metric catalogue.md"
```

The adapter reads the connector's output into the template's neutral metric list, then the catalogue is built from that. Move the result into `01 Context/` and do not edit it by hand.

## Reading figures well

- **Name the scenario and cycle in every query.** Do not rely on the default unless the answer says which default it used.
- **Actuals to the reference month, then the current cycle.** Query actuals for the closed months and the forecast cycle for the rest, as two queries.
- **Ask for metric details when in doubt.** The metric details tool returns the formula, the dimensions and the time roll-up. Use it before relying on a calculated metric.
- **Filter, do not fetch everything.** Use dimension filters to slice. The drill-down tool can cut long results short, so use it to see what sits under a figure, never to build a total; for totals, filter by dimension.
- **Watch calculated metrics over end-of-period inputs.** A ratio such as revenue per head that sums over months gives a wrong quarter value. The catalogue lists these on its watch list.
- **Prefer described metrics.** A metric with no description or with a warning is used only with a caveat. Retired metrics are not used.
- **Currencies.** If the connector offers more than one currency, name the one used and how it was translated.

## When the connector cannot answer

Check the connector's status tool first: a sync still running can make a recent month look empty. If the data simply is not there, decline and name the fallback, and add the gap to `data.limits` on the CFO's yes.
