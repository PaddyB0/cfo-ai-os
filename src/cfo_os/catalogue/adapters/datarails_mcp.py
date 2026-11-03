"""The Datarails FinanceOS connector's metric list -> the neutral metric list.

Input is what the connector's metric-list tool returns, saved as JSON: either the list of
metrics itself or an object holding it under "metrics", "results" or "data". Each metric
carries id, name, kind (BASE, CALC, USER or DRIVER), category, time_aggregation, dimensions, formula,
description and status_info.
"""

from __future__ import annotations

from typing import Any

KINDS = {"BASE": "base", "CALC": "calculated", "USER": "input", "DRIVER": "driver"}
ROLLUPS = {"SUM": "sum", "EOP": "end_of_period", "AVG": "average", "AVERAGE": "average"}


def looks_like(data: Any) -> bool:
    items = _items(data)
    return any(isinstance(m, dict) and ("time_aggregation" in m or "status_info" in m) for m in items)


def _items(data: Any) -> list[Any]:
    if isinstance(data, dict):
        for key in ("metrics", "results", "data"):
            if isinstance(data.get(key), list):
                return data[key]
        return []
    return data if isinstance(data, list) else []


def convert(data: Any, source: str = "Datarails FinanceOS connector") -> dict[str, Any]:
    metrics = []
    for i, m in enumerate(_items(data)):
        if not isinstance(m, dict):
            raise ValueError(f"metric list item {i} is not an object")
        status = m.get("status_info") or {}
        agg = str(m.get("time_aggregation") or "").upper()
        warning = status.get("source_warning") or None
        state = str(status.get("status") or "").upper()
        if state and state != "ACTIVE":
            warning = f"status {state}" + (f"; {warning}" if warning else "")
        metrics.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "kind": KINDS.get(str(m.get("kind") or "").upper(), "other"),
            # A roll-up the connector does not give is unknown, never assumed to be a sum.
            "rollup": ROLLUPS.get(agg, "unknown"),
            "category": m.get("category"),
            "dimensions": list(m.get("dimensions") or []),
            "formula": m.get("formula") or None,
            "description": m.get("description") or None,
            "warning": warning,
            "error": status.get("error_message") or None,
        })
    core: list[str] = []
    if metrics:
        shared = set(metrics[0]["dimensions"]).intersection(*(m["dimensions"] for m in metrics[1:]))
        core = [d for d in metrics[0]["dimensions"] if d in shared]
    return {"source": source, "core_dimensions": core, "metrics": metrics}
