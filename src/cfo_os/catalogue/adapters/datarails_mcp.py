"""The Datarails FinanceOS connector's metric list -> the neutral metric list.

Input is what the connector's metric-list tool returns, saved as JSON: either the list of
metrics itself or an object holding it under "metrics", "results" or "data". Each metric
carries id, name, kind (BASE or CALC), category, time_aggregation, dimensions, formula,
description and status_info.
"""

from __future__ import annotations

from typing import Any

KINDS = {"BASE": "base", "CALC": "calculated"}
ROLLUPS = {"SUM": "sum", "EOP": "end_of_period", "AVG": "average", "AVERAGE": "average"}


def looks_like(data: Any) -> bool:
    items = _items(data)
    return bool(items) and isinstance(items[0], dict) and "time_aggregation" in items[0]


def _items(data: Any) -> list[Any]:
    if isinstance(data, dict):
        for key in ("metrics", "results", "data"):
            if isinstance(data.get(key), list):
                return data[key]
        return []
    return data if isinstance(data, list) else []


def convert(data: Any, source: str = "Datarails FinanceOS connector") -> dict[str, Any]:
    metrics = []
    for m in _items(data):
        status = m.get("status_info") or {}
        agg = str(m.get("time_aggregation") or "").upper()
        metrics.append({
            "id": m["id"],
            "name": m["name"],
            "kind": KINDS.get(str(m.get("kind") or "").upper(), str(m.get("kind") or "").lower()),
            "rollup": ROLLUPS.get(agg, agg.lower() or "sum"),
            "category": m.get("category"),
            "dimensions": list(m.get("dimensions") or []),
            "formula": m.get("formula") or None,
            "description": m.get("description") or None,
            "warning": status.get("source_warning") or None,
            "error": status.get("error_message") or None,
        })
    core: list[str] = []
    if metrics:
        shared = set(metrics[0]["dimensions"]).intersection(*(m["dimensions"] for m in metrics[1:]))
        core = [d for d in metrics[0]["dimensions"] if d in shared]
    return {"source": source, "core_dimensions": core, "metrics": metrics}
