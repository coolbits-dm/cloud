#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Gap Analyzer
- Citește reports/policy_collect_*.json
- Aplică reguli pentru identificarea gap-urilor de policy
- Produce rapoarte: reports/policy_gaps.json + .md

Usage:
  python -m cblm.opipe.nha.adaptive.analyzer \
    --collect-file reports/policy_collect_last_24h.json \
    --out-dir reports \
    --min-scope-count 5 \
    --min-secret-count 3
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

ISO = "%Y-%m-%dT%H:%M:%SZ"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Analyze policy violations for gaps")
    p.add_argument(
        "--collect-file", required=True, help="Path to policy_collect_*.json"
    )
    p.add_argument("--out-dir", default="reports", help="Directory for output reports")
    p.add_argument(
        "--min-scope-count", type=int, default=5, help="Min denies for scope gap"
    )
    p.add_argument(
        "--min-secret-count", type=int, default=3, help="Min denies for secret gap"
    )
    p.add_argument(
        "--min-agent-count", type=int, default=2, help="Min agents for agent gap"
    )
    p.add_argument(
        "--markdown", action="store_true", help="Also write Markdown summary"
    )
    return p.parse_args()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_collect_data(file_path: Path) -> Dict[str, Any]:
    """Load policy collection data"""
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def analyze_scope_gaps(data: Dict[str, Any], min_count: int) -> List[Dict[str, Any]]:
    """Analyze missing scopes that should be added to policies"""
    gaps = []

    # Check missing_scopes from collector
    missing_scopes = data.get("missing_scopes", [])
    for scope_item in missing_scopes:
        scope = scope_item["key"]
        count = scope_item["count"]

        if count >= min_count:
            gaps.append(
                {
                    "type": "missing_scope",
                    "scope": scope,
                    "deny_count": count,
                    "rationale": f"Observed {count} denies for scope '{scope}' in analysis window",
                    "priority": "high" if count >= 10 else "medium",
                    "recommendation": f"Add scope '{scope}' to relevant agent capabilities",
                }
            )

    # Check top_scopes that might indicate missing permissions
    top_scopes = data.get("top_scopes", [])
    for scope_item in top_scopes:
        scope = scope_item["key"]
        count = scope_item["count"]

        # If a scope appears frequently in violations, it might be missing
        if count >= min_count:
            gaps.append(
                {
                    "type": "frequent_scope_violation",
                    "scope": scope,
                    "violation_count": count,
                    "rationale": f"Scope '{scope}' appears in {count} violations",
                    "priority": "medium",
                    "recommendation": f"Review scope '{scope}' permissions across agents",
                }
            )

    return gaps


def analyze_secret_gaps(data: Dict[str, Any], min_count: int) -> List[Dict[str, Any]]:
    """Analyze missing secrets that should be added to policies"""
    gaps = []

    missing_secrets = data.get("missing_secrets", [])
    for secret_item in missing_secrets:
        secret = secret_item["key"]
        count = secret_item["count"]

        if count >= min_count:
            gaps.append(
                {
                    "type": "missing_secret",
                    "secret": secret,
                    "deny_count": count,
                    "rationale": f"Observed {count} denies for secret '{secret}' in analysis window",
                    "priority": "high" if count >= 5 else "medium",
                    "recommendation": f"Add secret '{secret}' to relevant agent secrets list",
                }
            )

    return gaps


def analyze_agent_gaps(data: Dict[str, Any], min_count: int) -> List[Dict[str, Any]]:
    """Analyze agent-specific policy gaps"""
    gaps = []

    # Check top agents with violations
    top_agents = data.get("top_agents", [])
    for agent_item in top_agents:
        agent_id = agent_item["key"]
        count = agent_item["count"]

        if count >= min_count:
            # Get agent-specific data
            agent_actions = data.get("agent_action_matrix", {}).get(agent_id, [])
            agent_scopes = data.get("agent_scope_matrix", {}).get(agent_id, [])

            gaps.append(
                {
                    "type": "agent_policy_gap",
                    "agent_id": agent_id,
                    "violation_count": count,
                    "top_actions": [a["action"] for a in agent_actions[:3]],
                    "top_scopes": [s["scope"] for s in agent_scopes[:3]],
                    "rationale": f"Agent '{agent_id}' has {count} policy violations",
                    "priority": "high" if count >= 10 else "medium",
                    "recommendation": f"Review and update policy for agent '{agent_id}'",
                }
            )

    return gaps


def analyze_deprecated_agents(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze deprecated agents that are still active"""
    gaps = []

    # Check for unknown agents (might be deprecated or misconfigured)
    top_agents = data.get("top_agents", [])
    for agent_item in top_agents:
        agent_id = agent_item["key"]
        count = agent_item["count"]

        if agent_id == "nha:unknown":
            gaps.append(
                {
                    "type": "unknown_agent",
                    "agent_id": agent_id,
                    "violation_count": count,
                    "rationale": f"Unknown agent has {count} violations - check agent configuration",
                    "priority": "high",
                    "recommendation": "Verify agent ID configuration and registry entries",
                }
            )

    return gaps


def analyze_permission_gaps(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Analyze permission-related gaps"""
    gaps = []

    # Check top reasons for violations
    top_reasons = data.get("top_reasons", [])
    for reason_item in top_reasons:
        reason = reason_item["key"]
        count = reason_item["count"]

        if reason == "permission_not_allowed":
            gaps.append(
                {
                    "type": "permission_gap",
                    "reason": reason,
                    "violation_count": count,
                    "rationale": f"Permission denied {count} times - check IAM policies",
                    "priority": "high",
                    "recommendation": "Review and update IAM permissions in registry",
                }
            )
        elif reason == "scope_not_allowed":
            gaps.append(
                {
                    "type": "scope_permission_gap",
                    "reason": reason,
                    "violation_count": count,
                    "rationale": f"Scope denied {count} times - check capability scopes",
                    "priority": "medium",
                    "recommendation": "Review capability scopes in agent definitions",
                }
            )

    return gaps


def analyze_all_gaps(data: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """Run all gap analysis"""
    gaps = []

    # Run different analyzers
    gaps.extend(analyze_scope_gaps(data, args.min_scope_count))
    gaps.extend(analyze_secret_gaps(data, args.min_secret_count))
    gaps.extend(analyze_agent_gaps(data, args.min_agent_count))
    gaps.extend(analyze_deprecated_agents(data))
    gaps.extend(analyze_permission_gaps(data))

    # Categorize by priority
    high_priority = [g for g in gaps if g.get("priority") == "high"]
    medium_priority = [g for g in gaps if g.get("priority") == "medium"]
    low_priority = [g for g in gaps if g.get("priority") == "low"]

    # Generate summary
    summary = {
        "generated_at": _utcnow().strftime(ISO),
        "source_file": str(args.collect_file),
        "analysis_window": data.get("generated_at"),
        "total_violations": data.get("violations_total", 0),
        "total_gaps": len(gaps),
        "gaps_by_priority": {
            "high": len(high_priority),
            "medium": len(medium_priority),
            "low": len(low_priority),
        },
        "gaps_by_type": {},
        "all_gaps": gaps,
        "high_priority_gaps": high_priority,
        "medium_priority_gaps": medium_priority,
        "low_priority_gaps": low_priority,
    }

    # Count by type
    for gap in gaps:
        gap_type = gap.get("type", "unknown")
        summary["gaps_by_type"][gap_type] = summary["gaps_by_type"].get(gap_type, 0) + 1

    return summary


def write_json(out_dir: Path, data: Dict[str, Any]) -> Path:
    """Write analysis results to JSON"""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "policy_gaps.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def write_md(out_dir: Path, data: Dict[str, Any]) -> Path:
    """Write analysis results to Markdown"""
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "policy_gaps.md"

    md = []
    md.append("# Policy Gap Analysis Report")
    md.append(f"- Generated at: {data['generated_at']}")
    md.append(f"- Source: {data['source_file']}")
    md.append(f"- Analysis window: {data['analysis_window']}")
    md.append(f"- Total violations: **{data['total_violations']}**")
    md.append(f"- Total gaps found: **{data['total_gaps']}**")

    # Priority summary
    md.append("\n## Priority Summary")
    md.append(f"- High priority: **{data['gaps_by_priority']['high']}**")
    md.append(f"- Medium priority: **{data['gaps_by_priority']['medium']}**")
    md.append(f"- Low priority: **{data['gaps_by_priority']['low']}**")

    # Type summary
    md.append("\n## Gaps by Type")
    for gap_type, count in data["gaps_by_type"].items():
        md.append(f"- {gap_type}: {count}")

    # High priority gaps
    if data["high_priority_gaps"]:
        md.append("\n## High Priority Gaps")
        for gap in data["high_priority_gaps"]:
            md.append(f"\n### {gap.get('type', 'Unknown')}")
            md.append(
                f"- **Agent/Scope**: {gap.get('agent_id', gap.get('scope', gap.get('secret', 'N/A')))}"
            )
            md.append(
                f"- **Count**: {gap.get('violation_count', gap.get('deny_count', gap.get('count', 'N/A')))}"
            )
            md.append(f"- **Rationale**: {gap.get('rationale', 'N/A')}")
            md.append(f"- **Recommendation**: {gap.get('recommendation', 'N/A')}")

    # Medium priority gaps
    if data["medium_priority_gaps"]:
        md.append("\n## Medium Priority Gaps")
        for gap in data["medium_priority_gaps"]:
            md.append(f"\n### {gap.get('type', 'Unknown')}")
            md.append(
                f"- **Agent/Scope**: {gap.get('agent_id', gap.get('scope', gap.get('secret', 'N/A')))}"
            )
            md.append(
                f"- **Count**: {gap.get('violation_count', gap.get('deny_count', gap.get('count', 'N/A')))}"
            )
            md.append(f"- **Rationale**: {gap.get('rationale', 'N/A')}")
            md.append(f"- **Recommendation**: {gap.get('recommendation', 'N/A')}")

    with path.open("w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")

    return path


def main() -> None:
    args = parse_args()
    collect_file = Path(args.collect_file)
    out_dir = Path(args.out_dir)

    if not collect_file.exists():
        print(f"Error: Collection file not found: {collect_file}")
        return

    # Load and analyze
    data = load_collect_data(collect_file)
    analysis = analyze_all_gaps(data, args)

    # Write results
    out_json = write_json(out_dir, analysis)
    print(f"wrote {out_json}")

    if args.markdown:
        out_md = write_md(out_dir, analysis)
        print(f"wrote {out_md}")

    # Print summary
    print("\nAnalysis Summary:")
    print(f"- Total gaps: {analysis['total_gaps']}")
    print(f"- High priority: {analysis['gaps_by_priority']['high']}")
    print(f"- Medium priority: {analysis['gaps_by_priority']['medium']}")
    print(f"- Low priority: {analysis['gaps_by_priority']['low']}")


if __name__ == "__main__":
    main()
