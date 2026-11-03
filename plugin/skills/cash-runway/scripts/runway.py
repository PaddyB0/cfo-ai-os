#!/usr/bin/env python3
"""Project closing cash month by month and find the runway.

    python runway.py input.json [--json] [--decimals N]

The input is described in the skill's SKILL.md. The script reads one JSON file and prints a
Markdown report, or the same results as JSON with --json. Standard library only.

Exit codes: 0 report produced, 1 the input breaks a rule (the message says which), 2 usage.
"""

from __future__ import annotations

import argparse
import json
import sys
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation
from pathlib import Path


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


def non_negative(value, where: str) -> Decimal:
    number = dec(value, where)
    if number < 0:
        raise InputError(f"{where}: must not be negative, got {value!r}")
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


def project(opening: Decimal, start: int, movements: dict[int, Decimal], floor: Decimal) -> dict:
    """Closing cash for each month after start, the first month below the floor, and the low.
    An opening balance already below the floor is a breach in the opening month."""
    rows, balance = [], opening
    breach = start if opening < floor else None
    low_month, low = None, None
    for m in sorted(movements):
        balance += movements[m]
        rows.append({"month": month_text(m), "movement": movements[m], "closing": balance,
                     "below_floor": balance < floor})
        if breach is None and balance < floor:
            breach = m
        if low is None or balance < low:
            low_month, low = m, balance
    return {
        "rows": rows,
        "runway_month": month_text(breach) if breach is not None else None,
        "months_covered": max(breach - start - 1, 0) if breach is not None else len(rows),
        "beyond_horizon": breach is None,
        "opening_below_floor": opening < floor,
        "lowest_month": month_text(low_month),
        "lowest_balance": low,
    }


def parse(doc: dict) -> dict:
    if not isinstance(doc, dict):
        raise InputError("the input must be a JSON object")
    opening = doc.get("opening") or {}
    start = month_index(opening.get("month"), "opening.month")
    balance = dec(opening.get("balance"), "opening.balance")
    floor = dec(doc.get("minimum_cash", 0), "minimum_cash")

    movements: dict[int, Decimal] = {}
    sources: dict[int, str] = {}
    for i, item in enumerate(doc.get("movements") or []):
        m = month_index(item.get("month"), f"movements[{i}].month")
        if m in movements:
            raise InputError(f"movements: {month_text(m)} appears twice. Each month comes from one source.")
        if m <= start:
            raise InputError(f"movements: {month_text(m)} is not after the opening month {month_text(start)}. "
                             "The opening balance already includes it.")
        movements[m] = dec(item.get("amount"), f"movements[{i}].amount")
        sources[m] = str(item.get("source", ""))
    if not movements:
        raise InputError("movements: at least one forecast month is needed")
    if sorted(movements) != list(range(start + 1, start + 1 + len(movements))):
        missing = sorted(set(range(start + 1, max(movements) + 1)) - set(movements))
        raise InputError("movements: months must run without a gap from the month after the opening; "
                         f"missing {', '.join(month_text(m) for m in missing)}")
    kinds = set(sources.values())
    if len(kinds) > 1:
        raise InputError("movements: more than one source (" + "; ".join(sorted(k or "none given" for k in kinds))
                         + "). Every forecast month comes from one cycle, named on every month or on none.")

    trailing: dict[int, Decimal] = {}
    for i, item in enumerate(doc.get("trailing_actual_movements") or []):
        m = month_index(item.get("month"), f"trailing_actual_movements[{i}].month")
        if m > start:
            raise InputError(f"trailing_actual_movements: {month_text(m)} is after the opening month. "
                             "Trailing burn uses closed months only.")
        if m in trailing:
            raise InputError(f"trailing_actual_movements: {month_text(m)} appears twice")
        trailing[m] = dec(item.get("amount"), f"trailing_actual_movements[{i}].amount")
    if trailing and sorted(trailing) != list(range(start - len(trailing) + 1, start + 1)):
        raise InputError("trailing_actual_movements: months must run without a gap up to and including the "
                         f"opening month {month_text(start)}")

    forecast_closing: dict[int, Decimal] = {}
    for i, item in enumerate(doc.get("forecast_closing") or []):
        m = month_index(item.get("month"), f"forecast_closing[{i}].month")
        if m not in movements:
            raise InputError(f"forecast_closing: {month_text(m)} is outside the forecast months, so it cannot be tied")
        if m in forecast_closing:
            raise InputError(f"forecast_closing: {month_text(m)} appears twice")
        forecast_closing[m] = dec(item.get("balance"), f"forecast_closing[{i}].balance")

    sensitivities = []
    for i, s in enumerate(doc.get("sensitivities") or []):
        adj: dict[int, Decimal] = {}
        if "monthly" in s:
            step = dec(s["monthly"], f"sensitivities[{i}].monthly")
            adj = {m: step for m in movements}
        for j, a in enumerate(s.get("adjustments") or []):
            m = month_index(a.get("month"), f"sensitivities[{i}].adjustments[{j}].month")
            if m not in movements:
                raise InputError(f"sensitivities[{i}]: {month_text(m)} is outside the forecast months")
            adj[m] = adj.get(m, Decimal(0)) + dec(a.get("amount"), f"sensitivities[{i}].adjustments[{j}].amount")
        if not adj:
            raise InputError(f"sensitivities[{i}]: give 'monthly' or 'adjustments'")
        sensitivities.append((str(s.get("name") or f"sensitivity {i + 1}"), adj))

    previous = doc.get("previous") or {}
    if previous.get("runway_month") not in (None, "beyond horizon"):
        month_index(previous["runway_month"], "previous.runway_month")

    return {
        "currency": str(doc.get("currency", "")), "unit": str(doc.get("unit", "")),
        "start": start, "opening": balance, "opening_source": str(opening.get("source", "")),
        "floor": floor, "movements": movements, "source": next(iter(kinds), ""),
        "trailing": trailing, "forecast_closing": forecast_closing,
        "tolerance": non_negative(doc.get("tie_tolerance", 0.5), "tie_tolerance"),
        "sensitivities": sensitivities, "previous": previous,
    }


def run(doc: dict) -> dict:
    p = parse(doc)
    base = project(p["opening"], p["start"], p["movements"], p["floor"])

    ties = []
    closing_by_month = {month_index(r["month"], "row"): r["closing"] for r in base["rows"]}
    for m, fc in sorted(p["forecast_closing"].items()):
        if m in closing_by_month:
            diff = closing_by_month[m] - fc
            ties.append({"month": month_text(m), "projected": closing_by_month[m], "forecast": fc,
                         "difference": diff, "ties": abs(diff) <= p["tolerance"]})

    burn = None
    if p["trailing"]:
        months = sorted(p["trailing"])
        average = sum(p["trailing"].values()) / len(months)
        burn = {"months": [month_text(m) for m in months], "average_movement": average,
                "months_of_cash": ((p["opening"] - p["floor"]) / -average)
                          if average < 0 and p["opening"] >= p["floor"] else None}

    sens = []
    for name, adj in p["sensitivities"]:
        moved = {m: v + adj.get(m, Decimal(0)) for m, v in p["movements"].items()}
        r = project(p["opening"], p["start"], moved, p["floor"])
        sens.append({"name": name, **{k: r[k] for k in ("runway_month", "months_covered", "beyond_horizon",
                                                        "lowest_month", "lowest_balance")}})

    return {"input": p, "base": base, "ties": ties, "burn": burn, "sensitivities": sens}


def runway_phrase(r: dict, horizon_end: str) -> str:
    if r["opening_below_floor"]:
        return f"is already below the floor at the opening month, {r['runway_month']}"
    if r["beyond_horizon"]:
        return f"stays above the floor to the end of the forecast ({horizon_end})"
    return f"falls below the floor in {r['runway_month']}, {r['months_covered']} full month(s) covered"


def report(result: dict, decimals: int) -> str:
    p, base = result["input"], result["base"]
    unit = " ".join(x for x in (p["currency"], p["unit"]) if x)
    horizon_end = base["rows"][-1]["month"]
    out = ["# Cash runway", ""]
    out.append(f"Opening closing cash {money(p['opening'], decimals)} at {month_text(p['start'])}"
               + (f" ({p['opening_source']})" if p["opening_source"] else "") + "."
               + (f" Forecast movements from {p['source']}." if p["source"] else "")
               + (f" Figures in {unit}." if unit else ""))
    out.append(f"Floor {money(p['floor'], decimals)}. Sign convention: cash inflows positive, outflows negative.")
    out += ["", "| Month | Movement | Closing cash | Below floor |", "|---|---:|---:|---|"]
    for r in base["rows"]:
        out.append(f"| {r['month']} | {money(r['movement'], decimals)} | {money(r['closing'], decimals)} | "
                   f"{'yes' if r['below_floor'] else ''} |")
    out += ["", f"**Runway:** cash {runway_phrase(base, horizon_end)}. "
                f"Lowest projected balance {money(base['lowest_balance'], decimals)} in {base['lowest_month']}."]

    prev = p["previous"]
    if prev.get("runway_month"):
        now = base["runway_month"] or "beyond horizon"
        label = prev.get("cycle", "the previous cycle")
        if now == prev["runway_month"]:
            out.append(f"Unchanged from {label}.")
        elif "beyond horizon" in (now, prev["runway_month"]):
            out.append(f"Was {prev['runway_month']} in {label}; now {now}.")
        else:
            delta = month_index(now, "now") - month_index(prev["runway_month"], "previous")
            out.append(f"Was {prev['runway_month']} in {label}; now {now}, "
                       f"{abs(delta)} month(s) {'later' if delta > 0 else 'earlier'}.")

    burn = result["burn"]
    if burn:
        line = (f"Trailing burn check (worked out): average actual movement "
                f"{money(burn['average_movement'], decimals)} a month over {burn['months'][0]} to {burn['months'][-1]}.")
        if base["opening_below_floor"]:
            line += " Cash is already below the floor, so a burn-based runway does not apply."
        elif burn["months_of_cash"] is None:
            line += " Cash grew on average over those months, so a burn-based runway does not apply."
        else:
            line += (f" At that rate cash above the floor lasts {burn['months_of_cash']:.1f} months, against "
                     f"{base['months_covered']}{' or more' if base['beyond_horizon'] else ''} on the forecast. "
                     "A large gap means the forecast assumes a change in burn; name it.")
        out += ["", line]

    if result["ties"]:
        bad = [t for t in result["ties"] if not t["ties"]]
        out += ["", "## Tie to the forecast's own closing cash", ""]
        if not bad:
            out.append(f"All {len(result['ties'])} month(s) tie within {p['tolerance']}.")
        else:
            out += ["| Month | Projected | Forecast closing | Difference |", "|---|---:|---:|---:|"]
            for t in bad:
                out.append(f"| {t['month']} | {money(t['projected'], decimals)} | {money(t['forecast'], decimals)} | "
                           f"{money(t['difference'], decimals)} |")
            out += ["", f"{len(bad)} of {len(result['ties'])} month(s) do not tie. Explain each difference "
                        "(a non-cash item, a balance-sheet movement left out, timing) before relying on the runway."]

    if result["sensitivities"]:
        out += ["", "## Sensitivities (worked out)", "", "| Sensitivity | Runway | Lowest point |", "|---|---|---:|"]
        for s in result["sensitivities"]:
            runway = "beyond horizon" if s["beyond_horizon"] else f"{s['runway_month']} ({s['months_covered']} months)"
            out.append(f"| {s['name']} | {runway} | {money(s['lowest_balance'], decimals)} in {s['lowest_month']} |")
    return "\n".join(out) + "\n"


def to_json(result: dict) -> str:
    def default(o):
        if isinstance(o, Decimal):
            return str(o)
        raise TypeError(type(o))
    return json.dumps({k: v for k, v in result.items() if k != "input"}, default=default, indent=2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Project closing cash and find the runway.")
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
