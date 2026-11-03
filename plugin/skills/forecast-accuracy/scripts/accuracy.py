#!/usr/bin/env python3
"""How good was the last forecast, does the new one join on to actuals, and what is the full
year when actuals and the current cycle are spliced at the reference month.

    python accuracy.py input.json [--json] [--decimals N]

The input is described in the skill's SKILL.md. Standard library only.

Exit codes: 0 report produced, 1 the input breaks a rule (the message says which), 2 usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path

LINE_TYPES = ("revenue", "cost", "balance", "other")
CONVENTIONS = ("natural", "costs_positive")


class InputError(Exception):
    pass


def dec(value, where: str) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise InputError(f"{where}: expected a number, got {value!r}")
    try:
        number = Decimal(str(value))
    except InvalidOperation:
        raise InputError(f"{where}: expected a number, got {value!r}") from None
    if not number.is_finite():
        raise InputError(f"{where}: expected a finite number, got {value!r}")
    return number


def month_index(text, where: str) -> int:
    try:
        year, month = (int(p) for p in str(text).split("-"))
    except ValueError:
        raise InputError(f"{where}: month must be yyyy-mm, got {text!r}") from None
    if not 1 <= month <= 12 or len(str(text)) != 7:
        raise InputError(f"{where}: month must be yyyy-mm, got {text!r}")
    return year * 12 + month - 1


def month_text(index: int) -> str:
    return f"{index // 12:04d}-{index % 12 + 1:02d}"


def money(value: Decimal | None, decimals: int) -> str:
    if value is None:
        return ""
    text = f"{abs(value.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)):,.{decimals}f}"
    return f"({text})" if value < 0 else text


def pct(value: Decimal | None) -> str:
    return "n/m" if value is None else f"{value * 100:.1f}%"


def series(raw, where: str) -> dict[int, Decimal]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise InputError(f"{where}: give an object of yyyy-mm to value")
    return {month_index(k, f"{where} key"): dec(v, f"{where}[{k}]") for k, v in raw.items()}


def optimistic(line_type: str, convention: str, bias: Decimal) -> str:
    """Whether a forecast above actuals flattered the result."""
    if bias == 0 or line_type not in ("revenue", "cost"):
        return ""
    higher_flatters = line_type == "revenue" or convention == "natural"
    return "optimistic" if (bias > 0) == higher_flatters else "cautious"


def run(doc: dict) -> dict:
    if not isinstance(doc, dict):
        raise InputError("the input must be a JSON object")
    convention = doc.get("sign_convention", "natural")
    if convention not in CONVENTIONS:
        raise InputError(f"sign_convention: one of {', '.join(CONVENTIONS)}, got {convention!r}")
    ref = month_index(doc.get("reference_month"), "reference_month")
    threshold = dec(doc.get("step_change_percent", 15), "step_change_percent") / 100
    window = doc.get("run_rate_months", 3)
    if isinstance(window, bool) or not isinstance(window, int) or window < 1:
        raise InputError(f"run_rate_months: a whole number of months, at least 1, got {window!r}")
    year = sorted(month_index(m, "full_year_months") for m in (doc.get("full_year_months") or []))
    if year and year != list(range(year[0], year[0] + len(year))):
        raise InputError("full_year_months: consecutive months without a gap or a repeat")

    out_lines = []
    for i, ln in enumerate(doc.get("lines") or []):
        name = ln.get("line") or f"line {i + 1}"
        t = ln.get("type", "other")
        if t not in LINE_TYPES:
            raise InputError(f"lines[{i}].type: one of {', '.join(LINE_TYPES)}, got {t!r}")
        flow = t != "balance"
        actuals = series(ln.get("actuals"), f"lines[{i}].actuals")
        prior = series(ln.get("prior_forecast"), f"lines[{i}].prior_forecast")
        current = series(ln.get("current_forecast"), f"lines[{i}].current_forecast")
        if convention == "natural" and t == "cost":
            positive = sorted({month_text(m) for s in (actuals, prior, current) for m, v in s.items() if v > 0})
            if positive:
                raise InputError(f"lines[{i}] {name!r}: a cost is positive under the natural convention, where costs "
                                 f"are negative ({', '.join(positive)}). Fix the sign or set sign_convention to "
                                 "costs_positive.")
        late = [m for m in actuals if m > ref]
        if late:
            raise InputError(f"lines[{i}] {name!r}: actuals after the reference month "
                             f"({', '.join(month_text(m) for m in sorted(late))}). Move the reference month or drop them.")

        # Accuracy of the prior cycle on the months that have since closed.
        months = sorted(m for m in prior if m in actuals)
        acc = None
        if months:
            rows = [{"month": month_text(m), "actual": actuals[m], "forecast": prior[m],
                     "error": prior[m] - actuals[m]} for m in months]
            denom = sum(abs(actuals[m]) for m in months)
            total_err = sum(r["error"] for r in rows)
            acc = {"rows": rows,
                   "wape": None if denom == 0 else sum(abs(r["error"]) for r in rows) / denom,
                   "bias": None if denom == 0 else total_err / denom,
                   "total_error": total_err, "reading": optimistic(t, convention, total_err)}

        # Run rate: the last closed months against the first forecast months after them. For a
        # flow, the average monthly value; for a balance, the average monthly movement, so a
        # planned steady burn is not mistaken for a step.
        rr = None
        last = [m for m in range(ref - window + 1, ref + 1) if m in actuals]
        nxt = [m for m in range(ref + 1, ref + 1 + window) if m in current]
        if len(last) == window and len(nxt) == window and (flow or ref - window in actuals):
            if flow:
                a_avg = sum(actuals[m] for m in last) / window
                f_avg = sum(current[m] for m in nxt) / window
            else:
                a_avg = (actuals[ref] - actuals[ref - window]) / window
                f_avg = (current[ref + window] - actuals[ref]) / window
            if f_avg == a_avg:
                change = Decimal(0)
            else:
                change = None if a_avg == 0 else (f_avg - a_avg) / abs(a_avg)
            rr = {"actual_months": [month_text(m) for m in last], "forecast_months": [month_text(m) for m in nxt],
                  "actual": a_avg, "forecast": f_avg, "change": change,
                  "step": change is None or abs(change) >= threshold}

        # Full year spliced at the reference month: each month from exactly one source.
        fy = None
        if year:
            missing = [m for m in year if (m <= ref and m not in actuals) or (m > ref and m not in current)]
            if missing:
                raise InputError(f"lines[{i}] {name!r}: no value for {', '.join(month_text(m) for m in missing)} "
                                 "(actuals up to the reference month, the current forecast after it)")
            pick = {m: (actuals[m] if m <= ref else current[m]) for m in year}
            value = sum(pick.values()) if flow else pick[year[-1]]
            fy = {"value": value, "actual_months": sum(1 for m in year if m <= ref),
                  "forecast_months": sum(1 for m in year if m > ref),
                  "basis": "sum of months" if flow else f"balance at {month_text(year[-1])}"}
            if "budget_full_year" in ln:
                fy["budget"] = dec(ln["budget_full_year"], f"lines[{i}].budget_full_year")
            if "prior_full_year" in ln:
                fy["prior"] = dec(ln["prior_full_year"], f"lines[{i}].prior_full_year")
        out_lines.append({"line": name, "type": t, "accuracy": acc, "run_rate": rr, "full_year": fy})
    if not out_lines:
        raise InputError("lines: at least one line is needed")

    return {"reference_month": month_text(ref), "convention": convention, "threshold": threshold,
            "labels": {k: str(doc.get(k, d)) for k, d in (("actual_label", "Actuals"),
                                                          ("prior_label", "Previous forecast"),
                                                          ("current_label", "Current forecast"),
                                                          ("budget_label", "Budget"))},
            "unit": " ".join(str(x) for x in (doc.get("currency", ""), doc.get("unit", "")) if x),
            "lines": out_lines}


def report(r: dict, decimals: int) -> str:
    lb = r["labels"]
    conv = "natural sign: revenue positive, costs negative" if r["convention"] == "natural" else "costs shown positive"
    out = ["# Forecast accuracy and run rate", "",
           f"Reference month {r['reference_month']}: {lb['actual_label']} up to and including it, "
           f"{lb['current_label']} after it. Sign convention: {conv}."
           + (f" Figures in {r['unit']}." if r["unit"] else "")]

    acc = [ln for ln in r["lines"] if ln["accuracy"]]
    if acc:
        out += ["", f"## How good was {lb['prior_label']} (worked out)", "",
                "Error is forecast less actual. WAPE is the sum of absolute errors over the sum of absolute actuals. "
                "Bias is the net error over the same base: a forecast that is right on average but wrong each "
                "month has a low bias and a high WAPE.", "",
                "| Line | Months | Net error | WAPE | Bias | Reading |", "|---|---|---:|---:|---:|---|"]
        for ln in acc:
            a = ln["accuracy"]
            span = f"{a['rows'][0]['month']} to {a['rows'][-1]['month']}" if len(a["rows"]) > 1 else a["rows"][0]["month"]
            out.append(f"| {ln['line']} | {span} | {money(a['total_error'], decimals)} | {pct(a['wape'])} | "
                       f"{pct(a['bias'])} | {a['reading']} |")

    rr = [ln for ln in r["lines"] if ln["run_rate"]]
    if rr:
        out += ["", "## Run rate into the forecast (worked out)", "",
                f"Flows compare the average of the last closed months with the first forecast months. Balances compare "
                f"the average monthly movement over the same windows. A change of "
                f"{r['threshold'] * 100:.0f}% or more is a step the forecast must explain.", "",
                "| Line | Last actual | First forecast | Change | Step |", "|---|---:|---:|---:|---|"]
        for ln in rr:
            x = ln["run_rate"]
            out.append(f"| {ln['line']} | {money(x['actual'], decimals)} | {money(x['forecast'], decimals)} | "
                       f"{pct(x['change'])} | {'yes' if x['step'] else ''} |")
        steps = [ln["line"] for ln in rr if ln["run_rate"]["step"]]
        if steps:
            out += ["", "Steps to explain with the assumption owner: " + ", ".join(steps) + "."]

    fy = [ln for ln in r["lines"] if ln["full_year"]]
    if fy:
        has_b = any("budget" in ln["full_year"] for ln in fy)
        has_p = any("prior" in ln["full_year"] for ln in fy)
        head = f"| Line | Full year ({lb['actual_label']} + {lb['current_label']}) | Basis |"
        rule = "|---|---:|---|"
        if has_b:
            head += f" {lb['budget_label']} | vs {lb['budget_label']} |"
            rule += "---:|---:|"
        if has_p:
            head += f" {lb['prior_label']} | vs {lb['prior_label']} |"
            rule += "---:|---:|"
        out += ["", "## Full year, spliced at the reference month", "", head, rule]
        for ln in fy:
            f = ln["full_year"]
            row = f"| {ln['line']} | {money(f['value'], decimals)} | {f['actual_months']}+{f['forecast_months']}, {f['basis']} |"
            for key, on in (("budget", has_b), ("prior", has_p)):
                if on:
                    row += (f" {money(f[key], decimals)} | {money(f['value'] - f[key], decimals)} |" if key in f else "  |  |")
            out.append(row)
        out += ["", "Every month in the full year comes from one source only. Variances are full year less the comparator."]
    return "\n".join(out) + "\n"


def to_json(result: dict) -> str:
    def default(o):
        if isinstance(o, Decimal):
            return str(o)
        raise TypeError(type(o))
    return json.dumps(result, default=default, indent=2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Forecast accuracy, run-rate steps and the spliced full year.")
    ap.add_argument("input", type=Path)
    ap.add_argument("--json", action="store_true", help="print results as JSON")
    ap.add_argument("--decimals", type=int, default=0)
    args = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    try:
        result = run(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    except InputError as e:
        print(f"input error: {e}", file=sys.stderr)
        return 1
    print(to_json(result) if args.json else report(result, args.decimals), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
