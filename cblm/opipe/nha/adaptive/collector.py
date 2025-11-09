#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Violation Collector
- Citește logs/policy-enforcement-YYYYMM.jsonl (sau o cale custom)
- Filtrează DENY/WARN
- Agregă pe fereastră (last_24h, last_7d sau interval absolut)
- Produce rapoarte: reports/policy_collect.json (+ .md opțional)

Usage:
  python -m cblm.opipe.nha.adaptive.collector \
    --logs-dir logs \
    --window last_24h \
    --out-dir reports \
    --min-count 1
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from collections import Counter, defaultdict
from typing import Dict, List, Any, Iterable, Tuple

ISO = "%Y-%m-%dT%H:%M:%SZ"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Collect policy violations from JSONL audit logs"
    )
    p.add_argument(
        "--logs-dir", default="logs", help="Directory with policy-enforcement-*.jsonl"
    )
    p.add_argument("--out-dir", default="reports", help="Directory for output reports")
    p.add_argument(
        "--window",
        default="last_24h",
        choices=["last_24h", "last_7d", "all", "absolute"],
        help="Time window filter",
    )
    p.add_argument("--from-ts", help="Absolute start (UTC, e.g. 2025-09-11T00:00:00Z)")
    p.add_argument("--to-ts", help="Absolute end   (UTC, e.g. 2025-09-12T00:00:00Z)")
    p.add_argument(
        "--min-count",
        type=int,
        default=1,
        help="Only include items with count >= min-count",
    )
    p.add_argument(
        "--include-warn",
        action="store_true",
        help="Include WARN alongside DENY (default: only DENY)",
    )
    p.add_argument(
        "--markdown", action="store_true", help="Also write a Markdown summary"
    )
    return p.parse_args()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_ts(ts: str) -> datetime:
    # expected ISO Zulu
    return datetime.strptime(ts, ISO).replace(tzinfo=timezone.utc)


def resolve_window(args: argparse.Namespace) -> Tuple[datetime, datetime]:
    now = _utcnow()
    if args.window == "last_24h":
        return now - timedelta(hours=24), now
    if args.window == "last_7d":
        return now - timedelta(days=7), now
    if args.window == "all":
        return datetime(1970, 1, 1, tzinfo=timezone.utc), now
    if args.window == "absolute":
        if not args.from_ts or not args.to_ts:
            raise SystemExit("--window absolute requires --from-ts and --to-ts")
        return _parse_ts(args.from_ts), _parse_ts(args.to_ts)
    raise SystemExit("invalid window")


def iter_audit_files(logs_dir: Path) -> Iterable[Path]:
    # policy-enforcement-YYYYMM.jsonl
    yield from sorted(logs_dir.glob("policy-enforcement-*.jsonl"))


def iter_records(files: Iterable[Path]) -> Iterable[Dict[str, Any]]:
    for f in files:
        try:
            with f.open("r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = json.loads(line)
                        yield rec
                    except Exception:
                        # ignoră linii corupte
                        continue
        except FileNotFoundError:
            continue


def in_window(rec: Dict[str, Any], start: datetime, end: datetime) -> bool:
    try:
        ts = _parse_ts(rec.get("ts"))
        return start <= ts <= end
    except Exception:
        return False


def normalize(rec: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "ts": rec.get("ts"),
        "nha_id": rec.get("nha_id", "nha:unknown"),
        "action": rec.get("action", "unknown"),
        "scope": rec.get("scope"),
        "result": rec.get("result", "DENY"),
        "reason": rec.get("reason", "unknown"),
        "trace_id": rec.get("trace_id"),
        "extra": rec.get("extra") or {},
    }


def aggregate(
    records: Iterable[Dict[str, Any]], include_warn: bool, min_count: int
) -> Dict[str, Any]:
    # Counters
    total = 0
    denies = 0
    warns = 0
    by_agent = Counter()
    by_action = Counter()
    by_scope = Counter()
    by_reason = Counter()
    agent_action = defaultdict(Counter)  # agent -> action -> count
    agent_scope = defaultdict(Counter)  # agent -> scope  -> count
    missing_scopes = Counter()  # scope missing
    missing_secrets = Counter()  # secret missing (from reason/extra)

    for rec in records:
        r = normalize(rec)
        total += 1
        res = r["result"].upper()
        if res == "DENY":
            denies += 1
        elif res == "WARN":
            warns += 1
            if not include_warn:
                # dacă nu includem WARN în agregări, continuăm cu următorul
                continue
        else:
            # ALLOW – nu contează pentru violations
            continue

        agent = r["nha_id"]
        action = r["action"]
        scope = r.get("scope")
        reason = r.get("reason", "unknown")

        by_agent[agent] += 1
        by_action[action] += 1
        by_reason[reason] += 1
        if scope:
            by_scope[scope] += 1
            agent_scope[agent][scope] += 1
        agent_action[agent][action] += 1

        # heuristici pentru lipsă scope/secret
        if reason in ("scope_not_allowed", "permission_not_allowed"):
            if scope:
                missing_scopes[scope] += 1
        if reason in ("secret_not_allowed",):
            # încearcă să extragi din extra
            sec = None
            extra = r.get("extra") or {}
            if isinstance(extra, dict):
                sec = extra.get("secret") or extra.get("require_secret")
            if not sec:
                # fallback: ghicește din action/scope
                sec = "unknown"
            missing_secrets[sec] += 1

    def filter_min(c: Counter) -> List[Dict[str, Any]]:
        return [{"key": k, "count": v} for k, v in c.most_common() if v >= min_count]

    summary = {
        "generated_at": _utcnow().strftime(ISO),
        "total_records": total,
        "violations_total": denies + (warns if include_warn else 0),
        "denies": denies,
        "warns_included": warns if include_warn else 0,
        "top_agents": filter_min(by_agent),
        "top_actions": filter_min(by_action),
        "top_scopes": filter_min(by_scope),
        "top_reasons": filter_min(by_reason),
        "missing_scopes": filter_min(missing_scopes),
        "missing_secrets": filter_min(missing_secrets),
        "agent_action_matrix": {
            agent: [
                {"action": a, "count": c}
                for a, c in cnt.most_common()
                if c >= min_count
            ]
            for agent, cnt in agent_action.items()
        },
        "agent_scope_matrix": {
            agent: [
                {"scope": s, "count": c} for s, c in cnt.most_common() if c >= min_count
            ]
            for agent, cnt in agent_scope.items()
        },
    }
    return summary


def write_json(out_dir: Path, data: Dict[str, Any], window: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"policy_collect_{window}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def write_md(out_dir: Path, data: Dict[str, Any], window: str) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"policy_collect_{window}.md"

    def bullet(section: str, key_field: str = "key"):
        items = data.get(section) or []
        return "\n".join([f"- {i[key_field]}: {i['count']}" for i in items]) or "_none_"

    md = []
    md.append(f"# Policy Violations Summary ({window})")
    md.append(f"- Generated at: {data['generated_at']}")
    md.append(f"- Total audit records: **{data['total_records']}**")
    md.append(
        f"- Violations (counted): **{data['violations_total']}** (denies: {data['denies']}, warns: {data['warns_included']})"
    )
    md.append("\n## Top Agents\n" + bullet("top_agents"))
    md.append("\n## Top Actions\n" + bullet("top_actions"))
    md.append("\n## Top Scopes (missing)\n" + bullet("top_scopes"))
    md.append("\n## Reasons\n" + bullet("top_reasons"))
    md.append("\n## Missing Scopes (candidates)\n" + bullet("missing_scopes"))
    md.append("\n## Missing Secrets (candidates)\n" + bullet("missing_secrets"))
    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    return path


def main() -> None:
    args = parse_args()
    logs_dir = Path(args.logs_dir)
    out_dir = Path(args.out_dir)
    start, end = resolve_window(args)

    files = list(iter_audit_files(logs_dir))
    if not files:
        print("no audit files found")
        write_json(
            out_dir,
            {
                "generated_at": _utcnow().strftime(ISO),
                "total_records": 0,
                "violations_total": 0,
                "denies": 0,
                "warns_included": 0,
            },
            args.window,
        )
        return

    # citește și filtrează
    records = (
        r
        for r in iter_records(files)
        if r.get("result") in (["DENY", "WARN"] if args.include_warn else ["DENY"])
        and in_window(r, start, end)
    )
    summary = aggregate(
        records, include_warn=args.include_warn, min_count=args.min_count
    )
    out_json = write_json(out_dir, summary, args.window)
    print(f"wrote {out_json}")
    if args.markdown:
        out_md = write_md(out_dir, summary, args.window)
        print(f"wrote {out_md}")


if __name__ == "__main__":
    main()
