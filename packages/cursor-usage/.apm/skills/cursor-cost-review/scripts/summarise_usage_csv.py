#!/usr/bin/env python3
"""Summarise a Cursor usage-events CSV export: spend by model, day, and context size.

Usage:
    python3 summarise_usage_csv.py USAGE.csv [--top 10] [--json OUT.json]

Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date

REQUIRED_COLUMNS = (
    "Date",
    "Model",
    "Max Mode",
    "Input (w/ Cache Write)",
    "Input (w/o Cache Write)",
    "Cache Read",
    "Output Tokens",
    "Cost",
)
COMPONENTS = ("cache_write", "input", "cache_read", "output")
CONTEXT_BUCKETS_M = ((0, 1), (1, 3), (3, 6), (6, 15), (15, float("inf")))
MIN_ROWS_FOR_FIT = 20
EFFORT_TIERS = ("max", "xhigh", "high", "medium", "low")


@dataclass(frozen=True)
class Request:
    timestamp: str
    model: str
    max_mode: bool
    cost: float | None
    tokens: tuple[int, int, int, int]

    @property
    def day(self) -> str:
        return self.timestamp[:10]

    @property
    def label(self) -> str:
        return f"{self.model} (MAX)" if self.max_mode else self.model

    @property
    def effort(self) -> str:
        tokens = self.model.split("-")
        if tokens and tokens[-1] == "fast":
            tokens = tokens[:-1]
        return tokens[-1] if tokens and tokens[-1] in EFFORT_TIERS else "unspecified"

    @property
    def context_tokens(self) -> int:
        cache_write, fresh_input, cache_read, _ = self.tokens
        return cache_write + fresh_input + cache_read


def parse_int(value: str) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def parse_cost(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None


def load_requests(path: str) -> list[Request]:
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            sys.exit(f"error: {path} is missing columns {missing}; found {reader.fieldnames}")
        return [
            Request(
                timestamp=row["Date"],
                model=row["Model"],
                max_mode=row["Max Mode"].strip().lower() == "yes",
                cost=parse_cost(row["Cost"]),
                tokens=(
                    parse_int(row["Input (w/ Cache Write)"]),
                    parse_int(row["Input (w/o Cache Write)"]),
                    parse_int(row["Cache Read"]),
                    parse_int(row["Output Tokens"]),
                ),
            )
            for row in reader
        ]


def solve(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    size = len(vector)
    augmented = [row[:] + [vector[i]] for i, row in enumerate(matrix)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda r: abs(augmented[r][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            return None
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        for r in range(size):
            if r != col:
                factor = augmented[r][col] / augmented[col][col]
                augmented[r] = [a - factor * b for a, b in zip(augmented[r], augmented[col])]
    return [augmented[i][size] / augmented[i][i] for i in range(size)]


def fit_component_prices(requests: list[Request]) -> dict[str, float] | None:
    """Least-squares $/M-token per component, dropping components that fit negative."""
    rows = [([t / 1e6 for t in r.tokens], r.cost) for r in requests if r.cost is not None]
    if len(rows) < MIN_ROWS_FOR_FIT:
        return None
    active = [i for i in range(len(COMPONENTS)) if any(x[i] for x, _ in rows)]
    while active:
        matrix = [[sum(x[i] * x[j] for x, _ in rows) for j in active] for i in active]
        vector = [sum(x[i] * y for x, y in rows) for i in active]
        coefficients = solve(matrix, vector)
        if coefficients is None:
            return None
        negative = [active[k] for k, c in enumerate(coefficients) if c < 0]
        if not negative:
            prices = {name: 0.0 for name in COMPONENTS}
            for k, idx in enumerate(active):
                prices[COMPONENTS[idx]] = coefficients[k]
            return prices
        active = [i for i in active if i not in negative]
    return None


def component_shares(requests: list[Request], prices: dict[str, float]) -> dict[str, float]:
    totals = [sum(r.tokens[i] for r in requests if r.cost is not None) / 1e6 for i in range(4)]
    dollars = {name: totals[i] * prices[name] for i, name in enumerate(COMPONENTS)}
    fitted = sum(dollars.values()) or 1.0
    return {name: value / fitted for name, value in dollars.items()}


def summarise(requests: list[Request], top: int) -> dict:
    billable = [r for r in requests if r.cost is not None]
    total = sum(r.cost for r in billable)
    days = sorted({r.day for r in requests})
    span_days = (date.fromisoformat(days[-1]) - date.fromisoformat(days[0])).days + 1 if days else 0

    by_model: dict[str, list[Request]] = defaultdict(list)
    for r in requests:
        by_model[r.label].append(r)

    models = []
    for label, rows in by_model.items():
        costs = [r.cost for r in rows if r.cost is not None]
        spend = sum(costs)
        prices = fit_component_prices(rows)
        models.append(
            {
                "model": label,
                "requests": len(rows),
                "billable_requests": len(costs),
                "cost": round(spend, 2),
                "share": round(spend / total, 4) if total else 0.0,
                "cost_per_request": round(spend / len(costs), 2) if costs else 0.0,
                "tokens_m": {
                    name: round(sum(r.tokens[i] for r in rows) / 1e6, 2) for i, name in enumerate(COMPONENTS)
                },
                "fitted_price_per_m": {k: round(v, 2) for k, v in prices.items()} if prices else None,
                "fitted_cost_shares": (
                    {k: round(v, 3) for k, v in component_shares(rows, prices).items()} if prices else None
                ),
            }
        )
    models.sort(key=lambda m: -m["cost"])

    daily = []
    for day in days:
        rows = [r for r in billable if r.day == day]
        per_model: dict[str, float] = defaultdict(float)
        for r in rows:
            per_model[r.label] += r.cost
        daily.append(
            {
                "day": day,
                "cost": round(sum(per_model.values()), 2),
                "by_model": {k: round(v, 2) for k, v in sorted(per_model.items(), key=lambda x: -x[1])},
            }
        )

    buckets = []
    for low, high in CONTEXT_BUCKETS_M:
        rows = [r for r in billable if low <= r.context_tokens / 1e6 < high]
        spend = sum(r.cost for r in rows)
        buckets.append(
            {
                "context_m": f"{low}-{high if high != float('inf') else '+'}",
                "requests": len(rows),
                "cost": round(spend, 2),
                "share": round(spend / total, 4) if total else 0.0,
            }
        )

    effort_spend: dict[str, list[float]] = defaultdict(list)
    for r in billable:
        effort_spend[r.effort].append(r.cost)
    efforts = [
        {
            "effort": tier,
            "requests": len(costs),
            "cost": round(sum(costs), 2),
            "share": round(sum(costs) / total, 4) if total else 0.0,
        }
        for tier, costs in sorted(effort_spend.items(), key=lambda x: -sum(x[1]))
    ]

    max_rows = [r for r in billable if r.max_mode]
    top_requests = sorted(billable, key=lambda r: -r.cost)[:top]

    return {
        "period": {"first_day": days[0] if days else None, "last_day": days[-1] if days else None},
        "span_days": span_days,
        "active_days": len(days),
        "requests": len(requests),
        "billable_requests": len(billable),
        "total_cost": round(total, 2),
        "cost_per_active_day": round(total / len(days), 2) if days else 0.0,
        "max_mode": {
            "requests": len(max_rows),
            "cost": round(sum(r.cost for r in max_rows), 2),
        },
        "models": models,
        "effort_tiers": efforts,
        "daily": daily,
        "context_buckets": buckets,
        "top_requests": [
            {
                "timestamp": r.timestamp,
                "model": r.label,
                "cost": r.cost,
                "context_m": round(r.context_tokens / 1e6, 2),
                "output_m": round(r.tokens[3] / 1e6, 3),
            }
            for r in top_requests
        ],
    }


def print_report(summary: dict) -> None:
    period = summary["period"]
    print(
        f"Period {period['first_day']}..{period['last_day']} "
        f"({summary['active_days']} active of {summary['span_days']} days)"
    )
    print(
        f"Total ${summary['total_cost']:.2f} over {summary['billable_requests']} billable requests "
        f"(${summary['cost_per_active_day']:.2f}/active day)"
    )
    print(
        f"Max Mode column (large-context mode): {summary['max_mode']['requests']} requests, "
        f"${summary['max_mode']['cost']:.2f}"
    )

    print("\nSpend by reasoning-effort tier (parsed from the model slug)")
    for e in summary["effort_tiers"]:
        print(f"  {e['effort']:12s} n={e['requests']:4d} ${e['cost']:9.2f} {e['share']:6.1%}")

    print("\nSpend by model")
    for m in summary["models"]:
        if m["cost"] <= 0:
            continue
        line = (
            f"  {m['model']:38s} n={m['billable_requests']:4d} ${m['cost']:9.2f} "
            f"{m['share']:6.1%} ${m['cost_per_request']:.2f}/req"
        )
        if m["fitted_cost_shares"]:
            shares = m["fitted_cost_shares"]
            line += (
                f"  est. split cw={shares['cache_write']:.0%} cr={shares['cache_read']:.0%} "
                f"in={shares['input']:.0%} out={shares['output']:.0%}"
            )
        print(line)

    print("\nSpend by day")
    for d in summary["daily"]:
        top_models = ", ".join(f"{k} ${v:.0f}" for k, v in list(d["by_model"].items())[:3])
        print(f"  {d['day']} ${d['cost']:8.2f}  {top_models}")

    print("\nSpend by cumulative context per request (M tokens)")
    for b in summary["context_buckets"]:
        print(f"  {b['context_m']:>6s}M n={b['requests']:4d} ${b['cost']:9.2f} {b['share']:6.1%}")

    print("\nMost expensive requests")
    for r in summary["top_requests"]:
        print(f"  {r['timestamp']} {r['model']:32s} ${r['cost']:7.2f} ctx={r['context_m']}M out={r['output_m']}M")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_path")
    parser.add_argument("--top", type=int, default=10, help="number of most expensive requests to list")
    parser.add_argument("--json", dest="json_path", help="also write the full summary as JSON")
    args = parser.parse_args()

    summary = summarise(load_requests(args.csv_path), args.top)
    print_report(summary)
    if args.json_path:
        with open(args.json_path, "w") as handle:
            json.dump(summary, handle, indent=2)
        print(f"\nWrote {args.json_path}")


if __name__ == "__main__":
    main()
