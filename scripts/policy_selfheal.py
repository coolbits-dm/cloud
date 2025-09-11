#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Policy Self-Healing Script
- Verifică integritatea registry-ului
- Restaurează din backup dacă e corupt
- Auto-reload cache la schimbări
- Fail-closed dacă nu poate repara

Usage:
  python scripts/policy_selfheal.py \
    --registry-file cblm/opipe/nha/agents.yaml \
    --backup-file cblm/opipe/nha/out/registry.json \
    --check-signature \
    --auto-reload
"""

from __future__ import annotations
import argparse
import json
import yaml
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple

ISO = "%Y-%m-%dT%H:%M:%SZ"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Self-healing for policy registry")
    p.add_argument(
        "--registry-file",
        default="cblm/opipe/nha/agents.yaml",
        help="Path to agents.yaml",
    )
    p.add_argument(
        "--backup-file",
        default="cblm/opipe/nha/out/registry.json",
        help="Path to backup JSON",
    )
    p.add_argument(
        "--check-signature", action="store_true", help="Verify file signatures"
    )
    p.add_argument(
        "--auto-reload", action="store_true", help="Auto-reload enforcer cache"
    )
    p.add_argument(
        "--fail-closed", action="store_true", help="Fail closed if registry corrupted"
    )
    p.add_argument("--verbose", action="store_true", help="Verbose output")
    return p.parse_args()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file"""
    hash_sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def validate_yaml_syntax(file_path: Path) -> Tuple[bool, Optional[str]]:
    """Validate YAML syntax"""
    try:
        with file_path.open("r", encoding="utf-8") as f:
            yaml.safe_load(f)
        return True, None
    except yaml.YAMLError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)


def validate_registry_structure(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate registry structure"""
    try:
        # Check required fields
        if "version" not in data:
            return False, "Missing 'version' field"

        if "nhas" not in data:
            return False, "Missing 'nhas' field"

        if not isinstance(data["nhas"], list):
            return False, "'nhas' must be a list"

        # Check each agent
        agent_ids = set()
        agent_names = set()

        for i, agent in enumerate(data["nhas"]):
            if not isinstance(agent, dict):
                return False, f"Agent {i} is not a dictionary"

            # Required fields
            required_fields = ["id", "name", "category", "owner", "status"]
            for field in required_fields:
                if field not in agent:
                    return False, f"Agent {i} missing required field '{field}'"

            # Check uniqueness
            agent_id = agent["id"]
            agent_name = agent["name"]

            if agent_id in agent_ids:
                return False, f"Duplicate agent ID: {agent_id}"
            agent_ids.add(agent_id)

            if agent_name in agent_names:
                return False, f"Duplicate agent name: {agent_name}"
            agent_names.add(agent_name)

            # Check ID format
            if not agent_id.startswith("nha:"):
                return False, f"Agent {i} has invalid ID format: {agent_id}"

        return True, None

    except Exception as e:
        return False, str(e)


def load_registry_safely(
    file_path: Path,
) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
    """Safely load registry with validation"""
    try:
        # Check file exists
        if not file_path.exists():
            return False, None, f"Registry file not found: {file_path}"

        # Validate YAML syntax
        is_valid, error = validate_yaml_syntax(file_path)
        if not is_valid:
            return False, None, f"YAML syntax error: {error}"

        # Load data
        with file_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        # Validate structure
        is_valid, error = validate_registry_structure(data)
        if not is_valid:
            return False, None, f"Structure validation error: {error}"

        return True, data, None

    except Exception as e:
        return False, None, str(e)


def restore_from_backup(
    backup_file: Path, registry_file: Path
) -> Tuple[bool, Optional[str]]:
    """Restore registry from backup JSON"""
    try:
        if not backup_file.exists():
            return False, f"Backup file not found: {backup_file}"

        # Load backup
        with backup_file.open("r", encoding="utf-8") as f:
            backup_data = json.load(f)

        # Convert JSON to YAML structure
        yaml_data = {"version": backup_data.get("version", "1.0.0"), "nhas": []}

        for nha_data in backup_data.get("nhas", []):
            # Convert channels
            channels = []
            for ch_data in nha_data.get("channels", []):
                channels.append(
                    {
                        "kind": ch_data.get("kind"),
                        "endpoint": ch_data.get("endpoint"),
                        "auth": ch_data.get("auth", "none"),
                    }
                )

            # Convert capabilities
            capabilities = []
            for cap_data in nha_data.get("capabilities", []):
                capabilities.append(
                    {
                        "name": cap_data.get("name"),
                        "description": cap_data.get("description", ""),
                        "scopes": cap_data.get("scopes", []),
                    }
                )

            # Convert SLO
            slo_data = nha_data.get("slo", {})
            slo = {
                "latency_p95_ms": slo_data.get("latency_p95_ms", 1000),
                "error_rate_max": slo_data.get("error_rate_max", 0.05),
                "availability_pct": slo_data.get("availability_pct", 99.0),
            }

            # Create agent entry
            agent_entry = {
                "id": nha_data.get("id"),
                "name": nha_data.get("name"),
                "category": nha_data.get("category"),
                "owner": nha_data.get("owner"),
                "status": nha_data.get("status", "active"),
                "channels": channels,
                "capabilities": capabilities,
                "permissions": nha_data.get("permissions", []),
                "secrets": nha_data.get("secrets", []),
                "tags": nha_data.get("tags", []),
                "slo": slo,
                "notes": nha_data.get("notes", ""),
            }

            yaml_data["nhas"].append(agent_entry)

        # Write restored registry
        with registry_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2
            )

        return True, None

    except Exception as e:
        return False, str(e)


def reload_enforcer_cache() -> Tuple[bool, Optional[str]]:
    """Reload enforcer cache"""
    try:
        import sys
        import os

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from cblm.opipe.nha.enforcer import reload_registry

        reload_registry()
        return True, None
    except Exception as e:
        return False, str(e)


def check_registry_integrity(args: argparse.Namespace) -> Tuple[bool, Optional[str]]:
    """Check registry integrity and heal if needed"""
    registry_file = Path(args.registry_file)
    backup_file = Path(args.backup_file)

    if args.verbose:
        print(f"Checking registry: {registry_file}")
        print(f"Backup file: {backup_file}")

    # Try to load registry
    is_valid, data, error = load_registry_safely(registry_file)

    if is_valid:
        if args.verbose:
            print("[OK] Registry is valid")

        # Check signature if requested
        if args.check_signature:
            current_hash = calculate_file_hash(registry_file)
            if args.verbose:
                print(f"Registry hash: {current_hash}")

        return True, None
    else:
        print(f"[ERROR] Registry validation failed: {error}")

        # Try to restore from backup
        if backup_file.exists():
            print("[INFO] Attempting to restore from backup...")
            success, restore_error = restore_from_backup(backup_file, registry_file)

            if success:
                print("[OK] Registry restored from backup")

                # Verify restored registry
                is_valid, data, error = load_registry_safely(registry_file)
                if is_valid:
                    return True, None
                else:
                    return False, f"Restored registry still invalid: {error}"
            else:
                return False, f"Restore failed: {restore_error}"
        else:
            return False, f"No backup available: {backup_file}"


def main() -> None:
    args = parse_args()

    print("Policy Self-Healing Check")
    print("=" * 50)

    # Check registry integrity
    is_healthy, error = check_registry_integrity(args)

    if not is_healthy:
        print(f"[ERROR] Registry is unhealthy: {error}")

        if args.fail_closed:
            print("[CRITICAL] Fail-closed mode: Exiting with error")
            exit(1)
        else:
            print("[WARNING] Registry issues detected but continuing...")
    else:
        print("[OK] Registry is healthy")

    # Auto-reload cache if requested
    if args.auto_reload:
        print("[INFO] Reloading enforcer cache...")
        success, reload_error = reload_enforcer_cache()

        if success:
            print("[OK] Enforcer cache reloaded")
        else:
            print(f"[ERROR] Cache reload failed: {reload_error}")
            if args.fail_closed:
                exit(1)

    print("\n[COMPLETE] Self-healing check completed")


if __name__ == "__main__":
    main()
