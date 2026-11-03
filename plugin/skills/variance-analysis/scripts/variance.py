#!/usr/bin/env python3
"""Variance table with favourable or adverse, materiality, total tie-outs and a price, volume
and mix bridge.

    python variance.py input.json [--json] [--decimals N]

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


def non_negative(value, where: str) -> Decimal:
    number = dec(value, where)
    if number < 0:
        raise InputError(f"{where}: must not be negative, got {value!r}")
    return number


def money(value: Decimal | None, decimals: int) -> str:
    if value is None:
        return ""
    text = f"{abs(value.quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)):,.{decimals}f}"
    return f"({text})" if value < 0 else text


def pct(value: Decimal | None) -> str:
    return "n/m" if value is None else f"{value * 100:.1f}%"


def direction(line_type: str, convention: str, variance: Decimal, favourable_when: str | None) -> str:
    """F, A or blank. A revenue line is favourable when higher. A cost line is favourable when
    the cost is smaller: higher under the natural convention (costs negative), lower when
    costs are shown positive."""
    if variance == 0:
        return ""
    if favourable_when in ("higher", "lower"):
        higher_is_good = favourable_when == "higher"
    elif line_type == "revenue":
        higher_is_good = True
    elif line_type == "cost":
        higher_is_good = convention == "natural"
    else:
        return ""
    return "F" if (variance > 0) == higher_is_good else "A"


def material(variance: Decimal, ratio: Decimal | None, rule: dict) -> bool:
    """A zero variance is never material. Against a zero comparator the percent test does not
    apply, so the absolute test decides, or, with no absolute test, any movement is material."""
    if variance == 0:
        return False
    absolute, percent, mode = rule.get("absolute"), rule.get("percent"), rule.get("rule", "either")
    tests = []
    if absolute is not None:
        tests.append(abs(variance) >= absolute)
    if percent is not None and ratio is not None:
        tests.append(abs(ratio) * 100 >= percent)
    if not tests:
        return True
    return all(tests) if mode == "both" else any(tests)


def pvm(spec: dict, convention: str, lines: dict) -> dict:
    """Price, volume and mix effects that add up exactly to the change in value.

    volume = (total current volume - total comparator volume) x comparator average price
    mix    = total current volume x sum((current share - comparator share) x comparator price)
    price  = sum((current price - comparator price) x current volume)
    """
    items = spec.get("items") or []
    if not items:
        raise InputError("pvm.items: at least one item is needed")
    rows = []
    for i, it in enumerate(items):
        rows.append({
            "name": str(it.get("name") or f"item {i + 1}"),
            "cv": dec(it.get("current_volume"), f"pvm.items[{i}].current_volume"),
            "cp": dec(it.get("current_price"), f"pvm.items[{i}].current_price"),
            "bv": dec(it.get("comparator_volume"), f"pvm.items[{i}].comparator_volume"),
            "bp": dec(it.get("comparator_price"), f"pvm.items[{i}].comparator_price"),
        })
    for i, r in enumerate(rows):
        if r["cv"] < 0 or r["bv"] < 0:
            raise InputError(f"pvm.items[{i}] {r['name']!r}: volumes must not be negative")
    cv_total = sum(r["cv"] for r in rows)
    bv_total = sum(r["bv"] for r in rows)
    if bv_total == 0:
        raise InputError("pvm: total comparator volume must be above zero")
    b_avg_price = sum(r["bv"] * r["bp"] for r in rows) / bv_total
    volume = (cv_total - bv_total) * b_avg_price
    formula_mix = Decimal(0)
    if cv_total:
        formula_mix = cv_total * sum((r["cv"] / cv_total - r["bv"] / bv_total) * r["bp"] for r in rows)
    price = sum((r["cp"] - r["bp"]) * r["cv"] for r in rows)
    current_value = sum(r["cv"] * r["cp"] for r in rows)
    comparator_value = sum(r["bv"] * r["bp"] for r in rows)
    change = current_value - comparator_value
    # Mix is taken as the remainder so division rounding never leaves the bridge a penny out;
    # the residual against the share formula proves the remainder is mix and nothing else.
    mix = change - volume - price
    residual = formula_mix - mix

    line_name = spec.get("line")
    line_type = spec.get("type", "revenue")
    if line_type not in ("revenue", "cost"):
        raise InputError(f"pvm.type: revenue or cost, got {line_type!r}")
    if line_name is not None and line_name not in lines:
        raise InputError(f"pvm.line: {line_name!r} is not a line in the table, so the bridge cannot be tied to it")
    gap = None
    if line_name is not None:
        ln = lines[line_name]
        line_type = ln["type"]
        sign = -1 if (convention == "natural" and line_type == "cost") else 1
        gap = {"current": ln["current"] - sign * current_value, "comparator": ln["comparator"] - sign * comparator_value}
    effects = [("Volume", volume), ("Mix", mix), ("Price", price)]
    if line_type == "cost" and convention == "natural":
        effects = [(n, -v) for n, v in effects]
        change, current_value, comparator_value = -change, -current_value, -comparator_value
    return {
        "line": line_name, "type": line_type, "comparator_value": comparator_value, "current_value": current_value,
        "change": change,
        "effects": [{"name": n, "value": v, "direction": direction(line_type, convention, v, None)} for n, v in effects],
        "residual": residual, "gap_to_line": gap,
    }


def run(doc: dict) -> dict:
    if not isinstance(doc, dict):
        raise InputError("the input must be a JSON object")
    convention = doc.get("sign_convention", "natural")
    if convention not in CONVENTIONS:
        raise InputError(f"sign_convention: one of {', '.join(CONVENTIONS)}, got {convention!r}")
    m = doc.get("materiality") or {}
    rule = {"absolute": non_negative(m["absolute"], "materiality.absolute") if m.get("absolute") is not None else None,
            "percent": non_negative(m["percent"], "materiality.percent") if m.get("percent") is not None else None,
            "rule": m.get("rule", "either")}
    if rule["rule"] not in ("either", "both"):
        raise InputError("materiality.rule: either or both")
    tolerance = non_negative(doc.get("tie_tolerance", 0.5), "tie_tolerance")

    lines: dict[str, dict] = {}
    for i, ln in enumerate(doc.get("lines") or []):
        name = ln.get("line")
        if not name:
            raise InputError(f"lines[{i}]: needs a line name")
        if name in lines:
            raise InputError(f"lines: {name!r} appears twice")
        t = ln.get("type", "other")
        if t not in LINE_TYPES:
            raise InputError(f"lines[{i}].type: one of {', '.join(LINE_TYPES)}, got {t!r}")
        fw = ln.get("favourable_when")
        if fw not in (None, "higher", "lower"):
            raise InputError(f"lines[{i}].favourable_when: higher or lower")
        cur, cmp_ = dec(ln.get("current"), f"lines[{i}].current"), dec(ln.get("comparator"), f"lines[{i}].comparator")
        if convention == "natural" and t == "cost" and (cur > 0 or cmp_ > 0):
            raise InputError(f"lines[{i}] {name!r}: a cost is positive under the natural convention, where costs are "
                             "negative. Fix the sign or set sign_convention to costs_positive.")
        var = cur - cmp_
        ratio = None if cmp_ == 0 else var / abs(cmp_)
        lines[name] = {"line": name, "type": t, "current": cur, "comparator": cmp_, "variance": var, "ratio": ratio,
                       "direction": direction(t, convention, var, fw), "material": material(var, ratio, rule),
                       "source": str(ln.get("source", "")), "comment": str(ln.get("comment", ""))}
    if not lines:
        raise InputError("lines: at least one line is needed")

    totals = []
    for i, tot in enumerate(doc.get("totals") or []):
        name = tot.get("line") or f"total {i + 1}"
        parts = tot.get("of") or []
        unknown = [p for p in parts if p not in lines]
        if unknown or not parts:
            raise InputError(f"totals[{i}] {name!r}: 'of' must name lines in the table; unknown {unknown}")

        # With costs shown positive, a total that nets revenue against cost subtracts the costs;
        # a total of costs, or of costs and other lines, just adds them.
        types = {lines[p]["type"] for p in parts}
        nets = convention == "costs_positive" and {"cost", "revenue"} <= types

        def signed(part: str, key: str) -> Decimal:
            ln = lines[part]
            return -ln[key] if (nets and ln["type"] == "cost") else ln[key]

        row = {"line": name}
        for key in ("current", "comparator"):
            stated = dec(tot.get(key), f"totals[{i}].{key}")
            summed = sum(signed(p, key) for p in parts)
            row[key] = stated
            row[f"{key}_sum"] = summed
            row[f"{key}_ties"] = abs(stated - summed) <= tolerance
        row["variance"] = row["current"] - row["comparator"]
        row["ratio"] = None if row["comparator"] == 0 else row["variance"] / abs(row["comparator"])
        fw = tot.get("favourable_when")
        if fw not in (None, "higher", "lower"):
            raise InputError(f"totals[{i}].favourable_when: higher or lower")
        if fw is None:
            # A total of costs alone reads like a cost; any other total is favourable when higher.
            row["direction"] = direction("cost" if types == {"cost"} else "revenue", convention, row["variance"], None)
        else:
            row["direction"] = direction("other", convention, row["variance"], fw)
        totals.append(row)

    bridge = pvm(doc["pvm"], convention, lines) if doc.get("pvm") else None
    return {"labels": (str(doc.get("current_label", "Current")), str(doc.get("comparator_label", "Comparator"))),
            "unit": " ".join(str(x) for x in (doc.get("currency", ""), doc.get("unit", "")) if x),
            "convention": convention, "rule": rule, "tolerance": tolerance,
            "lines": list(lines.values()), "totals": totals, "pvm": bridge}


def report(r: dict, decimals: int) -> str:
    cur_label, cmp_label = r["labels"]
    out = ["# Variance analysis", ""]
    conv = ("natural sign: revenue positive, costs negative" if r["convention"] == "natural"
            else "costs shown positive")
    out.append(f"{cur_label} against {cmp_label}. Variance is {cur_label} less {cmp_label}. "
               f"Sign convention: {conv}. F is favourable, A adverse." + (f" Figures in {r['unit']}." if r["unit"] else ""))
    rule = r["rule"]
    if rule["absolute"] is None and rule["percent"] is None:
        out.append("No materiality threshold given: every line is treated as material.")
    else:
        parts = []
        if rule["absolute"] is not None:
            parts.append(f"{money(rule['absolute'], decimals)} absolute")
        if rule["percent"] is not None:
            parts.append(f"{rule['percent']}%")
        out.append(f"Material when {' and '.join(parts) if rule['rule'] == 'both' else ' or '.join(parts)}.")
    out += ["", f"| Line | {cur_label} | {cmp_label} | Variance | Variance % | F/A | Material | Source |",
            "|---|---:|---:|---:|---:|---|---|---|"]
    for ln in r["lines"]:
        out.append(f"| {ln['line']} | {money(ln['current'], decimals)} | {money(ln['comparator'], decimals)} | "
                   f"{money(ln['variance'], decimals)} | {pct(ln['ratio'])} | {ln['direction']} | "
                   f"{'yes' if ln['material'] else ''} | {ln['source']} |")
    for t in r["totals"]:
        out.append(f"| **{t['line']}** | **{money(t['current'], decimals)}** | **{money(t['comparator'], decimals)}** | "
                   f"**{money(t['variance'], decimals)}** | {pct(t['ratio'])} | {t['direction']} |  |  |")

    broken = [t for t in r["totals"] if not (t["current_ties"] and t["comparator_ties"])]
    if r["totals"]:
        out.append("")
        if not broken:
            out.append(f"Every total ties to the sum of its lines within {r['tolerance']}.")
        for t in broken:
            out.append(f"**{t['line']} does not tie.** Stated {money(t['current'], decimals)} and "
                       f"{money(t['comparator'], decimals)}; lines sum to {money(t['current_sum'], decimals)} and "
                       f"{money(t['comparator_sum'], decimals)}. Name what is left out before sending.")

    need = [ln["line"] for ln in r["lines"] if ln["material"] and ln["direction"] and not ln["comment"]]
    if need:
        out += ["", "Material lines that need a driver comment: " + ", ".join(need) + "."]

    b = r["pvm"]
    if b:
        out += ["", f"## Price, volume and mix{': ' + b['line'] if b['line'] else ''} (worked out)", "",
                "| Step | Value | F/A |", "|---|---:|---|",
                f"| {cmp_label} | {money(b['comparator_value'], decimals)} |  |"]
        for e in b["effects"]:
            out.append(f"| {e['name']} effect | {money(e['value'], decimals)} | {e['direction']} |")
        out.append(f"| {cur_label} | {money(b['current_value'], decimals)} |  |")
        out.append("")
        out.append("The three effects add up to the change"
                   + ("." if abs(b["residual"]) <= r["tolerance"] else f", leaving {money(b['residual'], decimals)} unexplained."))
        if b["gap_to_line"]:
            g = b["gap_to_line"]
            if abs(g["current"]) > r["tolerance"] or abs(g["comparator"]) > r["tolerance"]:
                out.append(f"Price times volume differs from the {b['line']} line by {money(g['current'], decimals)} "
                           f"({cur_label}) and {money(g['comparator'], decimals)} ({cmp_label}). Show that as "
                           "'not in volume data' (discounts, credits, other income) rather than spreading it.")
            else:
                out.append(f"Price times volume ties to the {b['line']} line.")
    return "\n".join(out) + "\n"


def to_json(result: dict) -> str:
    def default(o):
        if isinstance(o, Decimal):
            return str(o)
        raise TypeError(type(o))
    return json.dumps(result, default=default, indent=2)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Variance table with F/A, materiality, tie-outs and a PVM bridge.")
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
