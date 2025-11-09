#!/usr/bin/env python3
"""
M-gate Status Assembler
=======================

Compiles status from tripwires, registry, proofpack, policy shadow, and SLO
into a single canonical JSON for M-gate validation.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone


def load_json_safe(path: Path, default: dict = None) -> dict:
    """Load JSON file safely with default fallback"""
    try:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load {path}: {e}")
    return default or {}


def parse_tripwires(tripwire_dir: Path) -> dict:
    """Parse tripwire results"""
    tripwires_log = tripwire_dir / "tripwires.log"
    critical = 0
    warnings = 0

    if tripwires_log.exists():
        content = tripwires_log.read_text(encoding="utf-8")
        if "No alerts triggered" in content:
            critical = 0
            warnings = 0
        elif "critical alerts" in content:
            # Extract number from "X critical alerts"
            import re

            match = re.search(r"(\d+) critical alerts", content)
            if match:
                critical = int(match.group(1))

    return {
        "critical": critical,
        "warnings": warnings,
        "status": "HEALTHY" if critical == 0 else "CRITICAL",
    }


def parse_registry(registry_log: Path) -> dict:
    """Parse registry verification results"""
    cosign_verified = False

    if registry_log.exists():
        content = registry_log.read_text(encoding="utf-8")
        cosign_verified = "verified" in content.lower()

    return {
        "cosign_verified": cosign_verified,
        "status": "VERIFIED" if cosign_verified else "UNVERIFIED",
    }


def assemble_status(
    tripwire_dir: Path,
    registry_log: Path,
    proofpack_status: Path,
    policy_shadow: Path,
    slo_latest: Path,
    output: Path,
    strict: bool = False,
) -> dict:
    """Assemble canonical status JSON"""

    # Get current commit SHA
    try:
        import subprocess

        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True
        )
        commit_sha = result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        commit_sha = "unknown"

    # Parse all components
    tripwires = parse_tripwires(tripwire_dir)
    registry = parse_registry(registry_log)
    proofpack = load_json_safe(proofpack_status, {"hash": "unknown", "fresh": False})
    policy_shadow_data = load_json_safe(
        policy_shadow, {"drift_pct": 100.0, "deny_rate_pct": 100.0}
    )
    slo_data = load_json_safe(
        slo_latest,
        {
            "availability_pct": 0.0,
            "latency_p95_ms": 999999,
            "error_budget_remaining_pct": 0.0,
        },
    )

    # Determine overall status
    overall = "HEALTHY"
    if strict:
        if (
            tripwires["critical"] > 0
            or not registry["cosign_verified"]
            or not proofpack.get("fresh", False)
            or policy_shadow_data.get("drift_pct", 0) > 0.5
            or policy_shadow_data.get("deny_rate_pct", 0) > 1.0
            or slo_data.get("availability_pct", 0) < 99.0
        ):
            overall = "CRITICAL"

    # Assemble canonical status
    status = {
        "milestone": "M15",
        "commit_sha": commit_sha,
        "proofpack": {
            "hash": proofpack.get("hash", "unknown"),
            "generated_at": proofpack.get("generated_at", "unknown"),
            "fresh": proofpack.get("fresh", False),
        },
        "tripwires": tripwires,
        "registry": registry,
        "policy_shadow": policy_shadow_data,
        "slo": slo_data,
        "overall": overall,
        "assembled_at": datetime.now(timezone.utc).isoformat(),
    }

    # Write output
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

    return status


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Assemble M-gate status")
    parser.add_argument(
        "--tripwires", required=True, help="Tripwire artifacts directory"
    )
    parser.add_argument("--registry", required=True, help="Registry verification log")
    parser.add_argument("--proofpack", required=True, help="Proof Pack status JSON")
    parser.add_argument("--policy", required=True, help="Policy shadow report JSON")
    parser.add_argument("--slo", required=True, help="SLO latest report JSON")
    parser.add_argument("--out", required=True, help="Output status JSON")
    parser.add_argument("--strict", action="store_true", help="Strict validation mode")

    args = parser.parse_args()

    status = assemble_status(
        Path(args.tripwires),
        Path(args.registry),
        Path(args.proofpack),
        Path(args.policy),
        Path(args.slo),
        Path(args.out),
        args.strict,
    )

    print(f"Status assembled: {status['overall']}")
    print(f"Output: {args.out}")

    # Exit with error code if not healthy
    if status["overall"] != "HEALTHY":
        sys.exit(1)


if __name__ == "__main__":
    main()
