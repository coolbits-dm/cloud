#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Recommendation Generator
- Citește reports/policy_gaps.json
- Transformă gap-urile în propuneri concrete pentru registry
- Produce: cblm/opipe/nha/policy_recommendations.yaml

Usage:
  python -m cblm.opipe.nha.adaptive.recommender \
    --gaps-file reports/policy_gaps.json \
    --registry-file cblm/opipe/nha/agents.yaml \
    --out-file cblm/opipe/nha/policy_recommendations.yaml
"""

from __future__ import annotations
import argparse
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

ISO = "%Y-%m-%dT%H:%M:%SZ"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate policy recommendations from gap analysis"
    )
    p.add_argument("--gaps-file", required=True, help="Path to policy_gaps.json")
    p.add_argument(
        "--registry-file",
        default="cblm/opipe/nha/agents.yaml",
        help="Path to agents.yaml",
    )
    p.add_argument(
        "--out-file",
        default="cblm/opipe/nha/policy_recommendations.yaml",
        help="Output file",
    )
    p.add_argument(
        "--min-priority",
        default="medium",
        choices=["low", "medium", "high"],
        help="Minimum priority to include",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print recommendations without writing file",
    )
    return p.parse_args()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def load_gaps_data(file_path: Path) -> Dict[str, Any]:
    """Load policy gaps data"""
    with file_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_registry_data(file_path: Path) -> Dict[str, Any]:
    """Load registry data"""
    with file_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def priority_to_int(priority: str) -> int:
    """Convert priority to integer for comparison"""
    priority_map = {"low": 1, "medium": 2, "high": 3}
    return priority_map.get(priority, 0)


def generate_scope_recommendations(
    gaps: List[Dict[str, Any]], registry: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate recommendations for missing scopes"""
    recommendations = []

    # Create agent lookup
    agents_by_id = {agent["id"]: agent for agent in registry.get("nhas", [])}

    for gap in gaps:
        if gap.get("type") in ["missing_scope", "frequent_scope_violation"]:
            scope = gap.get("scope")
            if not scope:
                continue

            # Find agents that might need this scope
            # This is a heuristic - in practice you'd need more context
            scope_parts = scope.split(":")
            if len(scope_parts) >= 2:
                scope_type = scope_parts[0]  # e.g., "write", "read"
                scope_resource = scope_parts[1]  # e.g., "rag", "vectors"

                # Find agents that might be related to this resource
                for agent_id, agent in agents_by_id.items():
                    agent_name = agent.get("name", "")
                    agent_category = agent.get("category", "")

                    # Heuristic matching
                    should_add = False
                    if scope_resource in agent_name.lower():
                        should_add = True
                    elif scope_resource == "rag" and agent_category in [
                        "mlops",
                        "infra",
                    ]:
                        should_add = True
                    elif scope_resource == "vectors" and agent_category == "mlops":
                        should_add = True
                    elif scope_resource == "cost" and agent_category == "ops":
                        should_add = True

                    if should_add:
                        # Check if agent already has this scope
                        has_scope = False
                        for capability in agent.get("capabilities", []):
                            if scope in capability.get("scopes", []):
                                has_scope = True
                                break

                        if not has_scope:
                            recommendations.append(
                                {
                                    "agent_id": agent_id,
                                    "agent_name": agent_name,
                                    "action": "add_scope",
                                    "scope": scope,
                                    "rationale": gap.get("rationale", ""),
                                    "priority": gap.get("priority", "medium"),
                                    "gap_type": gap.get("type"),
                                    "violation_count": gap.get(
                                        "deny_count", gap.get("violation_count", 0)
                                    ),
                                }
                            )

    return recommendations


def generate_secret_recommendations(
    gaps: List[Dict[str, Any]], registry: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate recommendations for missing secrets"""
    recommendations = []

    agents_by_id = {agent["id"]: agent for agent in registry.get("nhas", [])}

    for gap in gaps:
        if gap.get("type") == "missing_secret":
            secret = gap.get("secret")
            if not secret:
                continue

            # Extract agent from secret name (format: nha/agent-id/secret-type)
            secret_parts = secret.split("/")
            if len(secret_parts) >= 3 and secret_parts[0] == "nha":
                agent_id = f"nha:{secret_parts[1]}"

                if agent_id in agents_by_id:
                    agent = agents_by_id[agent_id]

                    # Check if agent already has this secret
                    if secret not in agent.get("secrets", []):
                        recommendations.append(
                            {
                                "agent_id": agent_id,
                                "agent_name": agent.get("name", ""),
                                "action": "add_secret",
                                "secret": secret,
                                "rationale": gap.get("rationale", ""),
                                "priority": gap.get("priority", "medium"),
                                "gap_type": gap.get("type"),
                                "violation_count": gap.get("deny_count", 0),
                            }
                        )

    return recommendations


def generate_permission_recommendations(
    gaps: List[Dict[str, Any]], registry: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate recommendations for missing permissions"""
    recommendations = []

    agents_by_id = {agent["id"]: agent for agent in registry.get("nhas", [])}

    for gap in gaps:
        if gap.get("type") == "permission_gap":
            # This is a general permission gap - we need to infer what permissions might be missing
            # Based on the violation patterns, we can suggest common permissions

            # Common permissions that might be missing
            common_permissions = [
                "run.invoker",
                "storage.objectViewer",
                "storage.objectCreator",
                "logging.logWriter",
                "monitoring.viewer",
            ]

            # Find agents with high violation counts
            agent_gaps = [g for g in gaps if g.get("type") == "agent_policy_gap"]
            for agent_gap in agent_gaps:
                agent_id = agent_gap.get("agent_id")
                if agent_id in agents_by_id:
                    agent = agents_by_id[agent_id]
                    current_permissions = agent.get("permissions", [])

                    # Suggest missing common permissions
                    for perm in common_permissions:
                        if perm not in current_permissions:
                            recommendations.append(
                                {
                                    "agent_id": agent_id,
                                    "agent_name": agent.get("name", ""),
                                    "action": "add_permission",
                                    "permission": perm,
                                    "rationale": f"Agent has permission violations, may need {perm}",
                                    "priority": "medium",
                                    "gap_type": gap.get("type"),
                                    "violation_count": agent_gap.get(
                                        "violation_count", 0
                                    ),
                                }
                            )
                            break  # Only suggest one permission per agent

    return recommendations


def generate_agent_recommendations(
    gaps: List[Dict[str, Any]], registry: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Generate recommendations for agent-specific issues"""
    recommendations = []

    for gap in gaps:
        if gap.get("type") == "unknown_agent":
            recommendations.append(
                {
                    "agent_id": "unknown",
                    "agent_name": "Unknown Agent",
                    "action": "investigate_agent",
                    "rationale": gap.get("rationale", ""),
                    "priority": gap.get("priority", "high"),
                    "gap_type": gap.get("type"),
                    "violation_count": gap.get("violation_count", 0),
                    "recommendation": "Check agent configuration and ensure proper X-NHA-ID headers",
                }
            )
        elif gap.get("type") == "agent_policy_gap":
            agent_id = gap.get("agent_id")
            recommendations.append(
                {
                    "agent_id": agent_id,
                    "agent_name": f"Agent {agent_id}",
                    "action": "review_agent_policy",
                    "rationale": gap.get("rationale", ""),
                    "priority": gap.get("priority", "medium"),
                    "gap_type": gap.get("type"),
                    "violation_count": gap.get("violation_count", 0),
                    "top_actions": gap.get("top_actions", []),
                    "top_scopes": gap.get("top_scopes", []),
                }
            )

    return recommendations


def generate_all_recommendations(
    gaps_data: Dict[str, Any], registry_data: Dict[str, Any], min_priority: str
) -> Dict[str, Any]:
    """Generate all policy recommendations"""
    gaps = gaps_data.get("all_gaps", [])

    # Filter by priority
    min_priority_int = priority_to_int(min_priority)
    filtered_gaps = [
        gap
        for gap in gaps
        if priority_to_int(gap.get("priority", "low")) >= min_priority_int
    ]

    # Generate recommendations
    all_recommendations = []
    all_recommendations.extend(
        generate_scope_recommendations(filtered_gaps, registry_data)
    )
    all_recommendations.extend(
        generate_secret_recommendations(filtered_gaps, registry_data)
    )
    all_recommendations.extend(
        generate_permission_recommendations(filtered_gaps, registry_data)
    )
    all_recommendations.extend(
        generate_agent_recommendations(filtered_gaps, registry_data)
    )

    # Group by agent
    recommendations_by_agent = {}
    for rec in all_recommendations:
        agent_id = rec.get("agent_id", "unknown")
        if agent_id not in recommendations_by_agent:
            recommendations_by_agent[agent_id] = []
        recommendations_by_agent[agent_id].append(rec)

    # Create final structure
    result = {
        "generated_at": _utcnow().strftime(ISO),
        "source_gaps_file": gaps_data.get("source_file", ""),
        "total_recommendations": len(all_recommendations),
        "recommendations_by_agent": recommendations_by_agent,
        "all_recommendations": all_recommendations,
        "summary": {
            "scope_recommendations": len(
                [r for r in all_recommendations if r.get("action") == "add_scope"]
            ),
            "secret_recommendations": len(
                [r for r in all_recommendations if r.get("action") == "add_secret"]
            ),
            "permission_recommendations": len(
                [r for r in all_recommendations if r.get("action") == "add_permission"]
            ),
            "agent_recommendations": len(
                [
                    r
                    for r in all_recommendations
                    if r.get("action") in ["investigate_agent", "review_agent_policy"]
                ]
            ),
        },
    }

    return result


def write_yaml(file_path: Path, data: Dict[str, Any]) -> None:
    """Write recommendations to YAML file"""
    # Create YAML-ready structure
    yaml_data = {
        "policy_recommendations": {
            "generated_at": data["generated_at"],
            "total_recommendations": data["total_recommendations"],
            "summary": data["summary"],
            "agents": [],
        }
    }

    # Convert recommendations to YAML format
    for agent_id, recommendations in data["recommendations_by_agent"].items():
        agent_data = {"id": agent_id, "recommendations": []}

        for rec in recommendations:
            rec_data = {
                "action": rec["action"],
                "rationale": rec["rationale"],
                "priority": rec["priority"],
                "violation_count": rec.get("violation_count", 0),
            }

            # Add action-specific data
            if rec["action"] == "add_scope":
                rec_data["scope"] = rec["scope"]
            elif rec["action"] == "add_secret":
                rec_data["secret"] = rec["secret"]
            elif rec["action"] == "add_permission":
                rec_data["permission"] = rec["permission"]
            elif rec["action"] in ["investigate_agent", "review_agent_policy"]:
                if "top_actions" in rec:
                    rec_data["top_actions"] = rec["top_actions"]
                if "top_scopes" in rec:
                    rec_data["top_scopes"] = rec["top_scopes"]

            agent_data["recommendations"].append(rec_data)

        yaml_data["policy_recommendations"]["agents"].append(agent_data)

    # Write to file
    with file_path.open("w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2)


def main() -> None:
    args = parse_args()
    gaps_file = Path(args.gaps_file)
    registry_file = Path(args.registry_file)
    out_file = Path(args.out_file)

    if not gaps_file.exists():
        print(f"Error: Gaps file not found: {gaps_file}")
        return

    if not registry_file.exists():
        print(f"Error: Registry file not found: {registry_file}")
        return

    # Load data
    gaps_data = load_gaps_data(gaps_file)
    registry_data = load_registry_data(registry_file)

    # Generate recommendations
    recommendations = generate_all_recommendations(
        gaps_data, registry_data, args.min_priority
    )

    if args.dry_run:
        print("Recommendations (dry run):")
        print(json.dumps(recommendations, indent=2, ensure_ascii=False))
    else:
        # Write to file
        write_yaml(out_file, recommendations)
        print(f"wrote {out_file}")

    # Print summary
    print("\nRecommendation Summary:")
    print(f"- Total recommendations: {recommendations['total_recommendations']}")
    print(
        f"- Scope recommendations: {recommendations['summary']['scope_recommendations']}"
    )
    print(
        f"- Secret recommendations: {recommendations['summary']['secret_recommendations']}"
    )
    print(
        f"- Permission recommendations: {recommendations['summary']['permission_recommendations']}"
    )
    print(
        f"- Agent recommendations: {recommendations['summary']['agent_recommendations']}"
    )


if __name__ == "__main__":
    main()
