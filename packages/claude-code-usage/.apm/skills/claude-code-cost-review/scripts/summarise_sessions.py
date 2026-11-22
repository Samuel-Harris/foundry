#!/usr/bin/env python3
"""Summarise Claude Code spend from local session files: where the dollars went, by model, effort, agent and skill.

Usage:
    python3 summarise_sessions.py [--since 2026-11-15] [--until 2026-11-21] [--projects-dir ~/.claude/projects]
                                  [--top 10] [--json OUT.json]

The window defaults to the seven UTC days ending today. Dollar figures are API-price dollars: per-model token rates
are fitted to Claude Code's own `cost-state` session totals across all retained history, then applied to each
deduplicated request. Prints aggregates and subagent descriptions only, never transcript content. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import NamedTuple

CONTEXT_BUCKETS = ((0, 50_000), (50_000, 100_000), (100_000, 200_000), (200_000, 500_000), (500_000, 10**12))
STANDARD_RATIOS = (1.0, 5.0, 0.1, 1.25, 2.0)
FIT_TOLERANCE = 0.02
MAIN_CHAT = "main chat"

JsonObject = dict[str, object]


class TokenCounts(NamedTuple):
    fresh_input: int
    output: int
    cache_read: int
    cache_write_5m: int
    cache_write_1h: int


class TokenRates(NamedTuple):
    fresh_input: float
    output: float
    cache_read: float
    cache_write_5m: float
    cache_write_1h: float


class RecordedCost(NamedTuple):
    tokens: TokenCounts
    cost: float


class ModelRates(NamedTuple):
    rates: TokenRates
    fitted: bool
    sessions: int
    worst_session_error: float


@dataclass(frozen=True)
class SubagentInfo:
    agent_type: str
    pinned_model: str | None
    effort: str | None
    description: str


@dataclass(frozen=True)
class Request:
    request_id: str
    session_id: str
    project: str
    time: datetime
    model: str
    effort: str
    speed: str
    tokens: TokenCounts
    skill: str | None
    agent_id: str | None
    subagent: SubagentInfo | None

    @property
    def context_tokens(self) -> int:
        return self.tokens.fresh_input + self.tokens.cache_read + self.tokens.cache_write_5m + self.tokens.cache_write_1h


@dataclass
class Session:
    session_id: str
    project: str
    requests: list[Request]
    cost_state: dict[str, RecordedCost]


def as_object(value: object) -> JsonObject:
    return value if isinstance(value, dict) else {}


def as_int(value: object) -> int:
    return value if isinstance(value, int) else 0


def as_str(value: object) -> str | None:
    return value if isinstance(value, str) else None


def read_records(path: Path, /) -> list[JsonObject]:
    records = []
    with path.open(encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if '"type":"assistant"' not in line and '"type":"cost-state"' not in line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                records.append(record)
    return records


def read_subagent_info(meta_path: Path, /) -> SubagentInfo | None:
    try:
        meta = as_object(json.loads(meta_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return None
    model = as_str(meta.get("model"))
    inherited = meta.get("launchedWithDefaults") is True or model in (None, "inherit")
    return SubagentInfo(
        agent_type=as_str(meta.get("agentType")) or "unknown",
        pinned_model=None if inherited else model,
        effort=as_str(meta.get("effort")),
        description=(as_str(meta.get("description")) or "")[:80],
    )


def usage_tokens(usage: JsonObject, /) -> TokenCounts:
    creation = as_object(usage.get("cache_creation"))
    write_5m = as_int(creation.get("ephemeral_5m_input_tokens"))
    write_1h = as_int(creation.get("ephemeral_1h_input_tokens"))
    unsplit = as_int(usage.get("cache_creation_input_tokens")) - write_5m - write_1h
    return TokenCounts(
        fresh_input=as_int(usage.get("input_tokens")),
        output=as_int(usage.get("output_tokens")),
        cache_read=as_int(usage.get("cache_read_input_tokens")),
        cache_write_5m=write_5m + max(unsplit, 0),
        cache_write_1h=write_1h,
    )


def cost_state_tokens(usage: JsonObject, /) -> TokenCounts:
    write_5m = as_int(usage.get("cacheCreationEphemeral5mInputTokens"))
    write_1h = as_int(usage.get("cacheCreationEphemeral1hInputTokens"))
    unsplit = as_int(usage.get("cacheCreationInputTokens")) - write_5m - write_1h
    return TokenCounts(
        fresh_input=as_int(usage.get("inputTokens")),
        output=as_int(usage.get("outputTokens")),
        cache_read=as_int(usage.get("cacheReadInputTokens")),
        cache_write_5m=write_5m + max(unsplit, 0),
        cache_write_1h=write_1h,
    )


def parse_request(*, record: JsonObject, project: str, subagent: SubagentInfo | None) -> Request | None:
    message = as_object(record.get("message"))
    request_id = as_str(record.get("requestId"))
    model = as_str(message.get("model"))
    timestamp = as_str(record.get("timestamp"))
    if not request_id or not model or model.startswith("<") or not timestamp:
        return None
    usage = as_object(message.get("usage"))
    return Request(
        request_id=request_id,
        session_id=as_str(record.get("sessionId")) or "",
        project=project,
        time=datetime.fromisoformat(timestamp.replace("Z", "+00:00")),
        model=model,
        effort=as_str(record.get("effort")) or "unset",
        speed=as_str(usage.get("speed")) or "standard",
        tokens=usage_tokens(usage),
        skill=as_str(record.get("attributionSkill")),
        agent_id=as_str(record.get("agentId")),
        subagent=subagent,
    )


def load_session(main_path: Path, /) -> Session:
    project = main_path.parent.name
    requests: dict[str, Request] = {}
    cost_state: dict[str, RecordedCost] = {}
    for record in read_records(main_path):
        if record.get("type") == "cost-state":
            model_usage = as_object(record.get("modelUsage"))
            cost_state = {
                model: RecordedCost(cost_state_tokens(as_object(usage)), float(as_object(usage).get("costUSD") or 0.0))
                for model, usage in model_usage.items()
            }
        elif request := parse_request(record=record, project=project, subagent=None):
            requests[request.request_id] = request
    for agent_path in sorted((main_path.with_suffix("") / "subagents").glob("agent-*.jsonl")):
        subagent = read_subagent_info(agent_path.with_suffix(".meta.json")) or SubagentInfo("unknown", None, None, "")
        for record in read_records(agent_path):
            if request := parse_request(record=record, project=project, subagent=subagent):
                requests[request.request_id] = request
    return Session(main_path.stem, project, list(requests.values()), cost_state)


def load_sessions(projects_dir: Path, /) -> list[Session]:
    return [load_session(path) for path in sorted(projects_dir.glob("*/*.jsonl"))]


def solve(*, matrix: list[list[float]], vector: list[float]) -> list[float] | None:
    size = len(vector)
    rows = [row[:] + [value] for row, value in zip(matrix, vector, strict=True)]
    for col in range(size):
        pivot = max(range(col, size), key=lambda row: abs(rows[row][col]))
        if abs(rows[pivot][col]) < 1e-9:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for row in range(size):
            if row != col:
                factor = rows[row][col] / rows[col][col]
                rows[row] = [a - factor * b for a, b in zip(rows[row], rows[col], strict=True)]
    return [rows[i][size] / rows[i][i] for i in range(size)]


def fit_model_rates(observations: list[RecordedCost], /) -> ModelRates:
    features = [[count / 1e6 for count in observation.tokens] for observation in observations]
    costs = [observation.cost for observation in observations]
    used = [col for col in range(len(STANDARD_RATIOS)) if any(row[col] for row in features)]
    gram = [[sum(row[i] * row[j] for row in features) for j in used] for i in used]
    moment = [sum(row[i] * cost for row, cost in zip(features, costs, strict=True)) for i in used]
    solution = solve(matrix=gram, vector=moment) if len(observations) >= len(used) else None
    if solution is not None and all(rate >= 0 for rate in solution):
        input_rate = solution[used.index(0)] if 0 in used else 0.0
        rates = [ratio * input_rate for ratio in STANDARD_RATIOS]
        for col, rate in zip(used, solution, strict=True):
            rates[col] = rate
        candidate = TokenRates(*rates)
        worst = worst_error(observations=observations, rates=candidate)
        if worst <= FIT_TOLERANCE:
            return ModelRates(candidate, True, len(observations), worst)
    weighted = sum(sum(r * c for r, c in zip(STANDARD_RATIOS, row, strict=True)) for row in features)
    scale = sum(costs) / weighted if weighted else 0.0
    fallback = TokenRates(*(ratio * scale for ratio in STANDARD_RATIOS))
    return ModelRates(fallback, False, len(observations), worst_error(observations=observations, rates=fallback))


def worst_error(*, observations: list[RecordedCost], rates: TokenRates) -> float:
    errors = [
        abs(price(tokens=observation.tokens, rates=rates) - observation.cost) / observation.cost
        for observation in observations
        if observation.cost >= 0.5
    ]
    return max(errors, default=0.0)


def fit_rates(sessions: list[Session], /) -> dict[str, ModelRates]:
    observations: dict[str, list[RecordedCost]] = defaultdict(list)
    for session in sessions:
        for model, observation in session.cost_state.items():
            observations[model].append(observation)
    return {model: fit_model_rates(rows) for model, rows in observations.items()}


def price(*, tokens: TokenCounts, rates: TokenRates) -> float:
    return sum(count * rate for count, rate in zip(tokens, rates, strict=True)) / 1e6


def request_cost(*, request: Request, rates: dict[str, ModelRates]) -> float:
    model_rates = rates.get(request.model)
    return price(tokens=request.tokens, rates=model_rates.rates) if model_rates else 0.0


def agent_bucket(request: Request, /) -> str:
    subagent = request.subagent
    if subagent is None:
        return MAIN_CHAT
    routing = f"pinned {subagent.pinned_model}" if subagent.pinned_model else "inherited"
    effort = f", effort {subagent.effort}" if subagent.effort else ""
    return f"{subagent.agent_type} ({routing}{effort})"


def context_bucket(tokens: int, /) -> str:
    for low, high in CONTEXT_BUCKETS:
        if low <= tokens < high:
            return f"{low // 1000}k-{high // 1000}k" if high < 10**12 else f"{low // 1000}k+"
    return "unknown"


class Window(NamedTuple):
    start: datetime
    end: datetime


def parse_window(*, since: str | None, until: str | None) -> Window:
    last_day = date.fromisoformat(until) if until else datetime.now(timezone.utc).date()
    first_day = date.fromisoformat(since) if since else last_day - timedelta(days=6)
    start = datetime.combine(first_day, datetime.min.time(), tzinfo=timezone.utc)
    end = datetime.combine(last_day + timedelta(days=1), datetime.min.time(), tzinfo=timezone.utc)
    return Window(start, end)


def share_table(*, totals: dict[str, float], requests: dict[str, int], grand_total: float) -> list[JsonObject]:
    return [
        {"key": key, "cost": round(cost, 2), "share": round(cost / grand_total, 4) if grand_total else 0.0,
         "requests": requests[key]}
        for key, cost in sorted(totals.items(), key=lambda item: -item[1])
    ]


def summarise(*, sessions: list[Session], rates: dict[str, ModelRates], window: Window, top: int) -> JsonObject:
    dimensions = {
        "by_model": lambda r: r.model,
        "by_model_effort": lambda r: f"{r.model} / {r.effort}",
        "by_speed": lambda r: r.speed,
        "by_agent": agent_bucket,
        "by_skill": lambda r: r.skill or "(no skill)",
        "by_context": lambda r: context_bucket(r.context_tokens),
        "by_day": lambda r: r.time.date().isoformat(),
        "by_project": lambda r: r.project,
    }
    totals: dict[str, dict[str, float]] = {name: defaultdict(float) for name in dimensions}
    counts: dict[str, dict[str, int]] = {name: defaultdict(int) for name in dimensions}
    component_cost: dict[str, list[float]] = defaultdict(lambda: [0.0] * len(STANDARD_RATIOS))
    session_cost: dict[str, float] = defaultdict(float)
    session_requests: dict[str, int] = defaultdict(int)
    session_peak_context: dict[str, int] = defaultdict(int)
    subagent_cost: dict[str, float] = defaultdict(float)
    subagent_label: dict[str, str] = {}
    grand_total = 0.0
    for session in sessions:
        for request in session.requests:
            if not window.start <= request.time < window.end:
                continue
            cost = request_cost(request=request, rates=rates)
            grand_total += cost
            for name, key_of in dimensions.items():
                key = key_of(request)
                totals[name][key] += cost
                counts[name][key] += 1
            model_rates = rates.get(request.model)
            if model_rates:
                for index, (count, rate) in enumerate(zip(request.tokens, model_rates.rates, strict=True)):
                    component_cost[request.model][index] += count * rate / 1e6
            session_key = f"{request.project}/{session.session_id}"
            if request.subagent is None:
                session_cost[session_key] += cost
                session_requests[session_key] += 1
                session_peak_context[session_key] = max(session_peak_context[session_key], request.context_tokens)
            elif request.agent_id:
                subagent_cost[request.agent_id] += cost
                subagent_label[request.agent_id] = f"{agent_bucket(request)}: {request.subagent.description}"
    days = max((window.end - window.start).days, 1)
    summary: JsonObject = {
        "window": {"start": window.start.date().isoformat(), "end_exclusive": window.end.date().isoformat(), "days": days},
        "total_cost": round(grand_total, 2),
        "cost_per_week": round(grand_total * 7 / days, 2),
        "requests": sum(counts["by_model"].values()),
    }
    for name in dimensions:
        summary[name] = share_table(totals=totals[name], requests=counts[name], grand_total=grand_total)
    summary["cost_components"] = {
        model: {field: round(value, 2) for field, value in zip(TokenCounts._fields, parts, strict=True)}
        for model, parts in sorted(component_cost.items(), key=lambda item: -sum(item[1]))
    }
    summary["top_main_chats"] = [
        {"session": key, "cost": round(cost, 2), "requests": session_requests[key],
         "peak_context_tokens": session_peak_context[key]}
        for key, cost in sorted(session_cost.items(), key=lambda item: -item[1])[:top]
    ]
    summary["top_subagents"] = [
        {"agent": subagent_label[agent_id], "cost": round(cost, 2)}
        for agent_id, cost in sorted(subagent_cost.items(), key=lambda item: -item[1])[:top]
    ]
    summary["rates_per_million_tokens"] = {
        model: {"fitted": fit.fitted, "sessions": fit.sessions, "worst_session_error": round(fit.worst_session_error, 4),
                **{field: round(rate, 4) for field, rate in zip(TokenRates._fields, fit.rates, strict=True)}}
        for model, fit in sorted(rates.items())
    }
    summary["reconciliation"] = reconcile(sessions=sessions, rates=rates)
    return summary


def reconcile(*, sessions: list[Session], rates: dict[str, ModelRates]) -> JsonObject:
    recorded = priced = 0.0
    mismatched = 0
    without_cost_state = 0
    for session in sessions:
        if not session.cost_state:
            without_cost_state += bool(session.requests)
            continue
        session_recorded = sum(recorded.cost for recorded in session.cost_state.values())
        session_priced = sum(request_cost(request=request, rates=rates) for request in session.requests)
        recorded += session_recorded
        priced += session_priced
        if session_recorded >= 0.5 and abs(session_priced - session_recorded) / session_recorded > 0.05:
            mismatched += 1
    return {
        "cost_state_total": round(recorded, 2),
        "priced_requests_total": round(priced, 2),
        "sessions_off_by_more_than_5_percent": mismatched,
        "sessions_without_cost_state": without_cost_state,
    }


def print_table(*, title: str, rows: list[JsonObject], limit: int) -> None:
    print(f"\n{title}")
    for row in rows[:limit]:
        print(f"  {row['share']:>6.1%}  ${row['cost']:>10,.2f}  {row['requests']:>7} req  {row['key']}")


def print_summary(*, summary: JsonObject, top: int) -> None:
    window = as_object(summary["window"])
    print(f"Window {window['start']} to {window['end_exclusive']} (exclusive, UTC), {window['days']} days")
    print(f"Total ${summary['total_cost']:,.2f} over {summary['requests']} requests; ${summary['cost_per_week']:,.2f}/week")
    for name in ("by_model", "by_model_effort", "by_speed", "by_agent", "by_skill", "by_context", "by_day", "by_project"):
        rows = summary[name]
        if isinstance(rows, list):
            print_table(title=name.replace("_", " "), rows=rows, limit=top if name != "by_day" else 31)
    print("\ncost components ($)")
    for model, parts in as_object(summary["cost_components"]).items():
        print(f"  {model}: {parts}")
    print("\ntop main chats")
    for row in summary["top_main_chats"] if isinstance(summary["top_main_chats"], list) else []:
        print(f"  ${row['cost']:>9,.2f}  {row['requests']:>5} req  peak {row['peak_context_tokens']:>9,} tok  {row['session']}")
    print("\ntop subagents")
    for row in summary["top_subagents"] if isinstance(summary["top_subagents"], list) else []:
        print(f"  ${row['cost']:>9,.2f}  {row['agent']}")
    print("\nfitted rates ($ per million tokens)")
    for model, fit in as_object(summary["rates_per_million_tokens"]).items():
        print(f"  {model}: {fit}")
    print(f"\nreconciliation (all retained history): {summary['reconciliation']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--since", help="first UTC day, YYYY-MM-DD (default: six days before --until)")
    parser.add_argument("--until", help="last UTC day, inclusive, YYYY-MM-DD (default: today)")
    parser.add_argument("--projects-dir", type=Path, default=Path.home() / ".claude" / "projects")
    parser.add_argument("--top", type=int, default=10)
    parser.add_argument("--json", type=Path, help="also write the summary as JSON to this path")
    args = parser.parse_args()
    if not args.projects_dir.is_dir():
        print(f"error: no Claude Code projects directory at {args.projects_dir}", file=sys.stderr)
        return 2
    sessions = load_sessions(args.projects_dir)
    summary = summarise(
        sessions=sessions,
        rates=fit_rates(sessions),
        window=parse_window(since=args.since, until=args.until),
        top=args.top,
    )
    print_summary(summary=summary, top=args.top)
    if args.json:
        args.json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
