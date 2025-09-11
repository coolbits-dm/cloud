# CoolBits.ai @oPipe - NHA Runtime Governance & Policy Enforcement
# Paznic cu baston: orice NHA care iese din linii e oprit pe loc, logat și raportat

from __future__ import annotations
import json
import os
import time
import uuid
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .registry import load_yaml, Registry, NHA

# -------------------------
# Config (override via env)
# -------------------------
REGISTRY_PATH = os.getenv("NHA_REGISTRY_PATH", "cblm/opipe/nha/agents.yaml")
POLICY_VERSION = os.getenv("NHA_POLICY_VERSION", time.strftime("%Y-%m-%d"))
MODE = os.getenv("NHA_ENFORCEMENT_MODE", "deny")  # "deny" | "warn" | "fail-closed"
AUDIT_DIR = Path(os.getenv("NHA_AUDIT_DIR", "logs"))
AUDIT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_FILE = AUDIT_DIR / f"policy-enforcement-{time.strftime('%Y%m')}.jsonl"

FAIL_CLOSED = MODE == "fail-closed"
ALLOW_WARN = MODE == "warn"
DENY_BY_DEFAULT = True  # nu schimba; platformă guvernată, nu cabană


# -------------------------
# Tipuri rezultate + erori
# -------------------------
@dataclass
class EnforcementResult:
    allowed: bool
    decision: str  # "ALLOW" | "DENY" | "WARN"
    reason: str  # "ok" sau motiv blocare
    policy_version: str
    trace_id: str
    nha_id: str
    action: str
    scope: Optional[str] = None
    extra: dict = None


class PolicyError(RuntimeError):
    pass


# -------------------------
# Cache registry + reload
# -------------------------
_lock = threading.RLock()
_cache: Dict[str, NHA] = {}
_cache_version = "unknown"


def _hydrate_cache(reg: Registry) -> None:
    global _cache, _cache_version
    with _lock:
        _cache = {n.id: n for n in reg.nhas}
        _cache_version = reg.version


def reload_registry(path: str = REGISTRY_PATH) -> None:
    """Reload registry from YAML file"""
    reg = load_yaml(path)
    # aici poți rula validate.py dacă vrei fail mai dur
    _hydrate_cache(reg)


# încarcă la import; dacă pică și suntem fail-closed, ridică
try:
    reload_registry()
except Exception as e:
    if FAIL_CLOSED:
        raise PolicyError(f"Registry load failed in fail-closed mode: {e}")
    else:
        # mod deny/warn: continuă, dar cu cache gol -> deny
        pass


# -------------------------
# Utilitare audit JSONL
# -------------------------
def _audit_write(record: dict) -> None:
    try:
        with _lock:
            with AUDIT_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # nu spamăm aplicația dacă logul cade
        pass


def _audit(
    nha_id: str,
    action: str,
    result: str,
    reason: str,
    *,
    scope: Optional[str],
    extra: Optional[dict],
) -> None:
    rec = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "nha_id": nha_id,
        "action": action,
        "result": result,  # ALLOW / DENY / WARN
        "reason": reason,
        "policy_version": POLICY_VERSION,
        "registry_version": _cache_version,
        "trace_id": str(uuid.uuid4()),
        "scope": scope,
        "extra": extra or {},
    }
    _audit_write(rec)


# -------------------------
# Controale de politică
# -------------------------
def _get_agent(nha_id: str) -> Optional[NHA]:
    with _lock:
        return _cache.get(nha_id)


def _has_scope(agent: NHA, scope: str) -> bool:
    for cap in agent.capabilities or []:
        if scope in (cap.scopes or []):
            return True
    return False


def _has_secret(agent: NHA, secret_name: str) -> bool:
    return secret_name in (agent.secrets or [])


def _permits_action(agent: NHA, action: str) -> bool:
    # map simplu: action-ul trebuie să existe în permissions
    # ex: "run.invoker" sau "write:rag"
    return action in (agent.permissions or [])


def _status_allows(agent: NHA, action: str) -> Tuple[bool, str]:
    st = agent.status or "active"
    if st == "deprecated":
        return False, "agent_deprecated"
    if st == "paused":
        # policy: doar read:* permise dacă paused
        if action.startswith("read:"):
            return True, "ok"
        return False, "agent_paused_readonly"
    return True, "ok"


# -------------------------
# Interfața publică
# -------------------------
def check_capability(nha_id: str, scope: str) -> bool:
    """Check if NHA has capability for given scope"""
    ag = _get_agent(nha_id)
    if not ag:
        return False
    ok, _ = _status_allows(ag, f"use:{scope}")
    return ok and _has_scope(ag, scope)


def check_secret(nha_id: str, secret: str) -> bool:
    """Check if NHA has access to given secret"""
    ag = _get_agent(nha_id)
    if not ag:
        return False
    ok, _ = _status_allows(ag, f"secret:{secret}")
    return ok and _has_secret(ag, secret)


def check_permission(nha_id: str, action: str) -> bool:
    """Check if NHA has permission for given action"""
    ag = _get_agent(nha_id)
    if not ag:
        return False
    ok, _ = _status_allows(ag, action)
    return ok and _permits_action(ag, action)


def enforce_request(
    nha_id: str,
    action: str,
    payload: dict,
    *,
    scope: Optional[str] = None,
    require_secret: Optional[str] = None,
    extras: Optional[dict] = None,
) -> EnforcementResult:
    """
    Gate unic pentru orice acțiune.
    - action: ex "rag:ingest" sau "run.invoker"
    - scope: dacă acțiunea are și scope (ex write:rag)
    - require_secret: dacă acțiunea cere secret (ex HMAC key)
    """
    ag = _get_agent(nha_id)
    if ag is None:
        # agent necunoscut
        if FAIL_CLOSED or DENY_BY_DEFAULT:
            _audit(nha_id, action, "DENY", "unknown_agent", scope=scope, extra=extras)
            return EnforcementResult(
                False,
                "DENY",
                "unknown_agent",
                POLICY_VERSION,
                str(uuid.uuid4()),
                nha_id,
                action,
                scope,
                extras,
            )
        if ALLOW_WARN:
            _audit(nha_id, action, "WARN", "unknown_agent", scope=scope, extra=extras)
            return EnforcementResult(
                True,
                "WARN",
                "unknown_agent",
                POLICY_VERSION,
                str(uuid.uuid4()),
                nha_id,
                action,
                scope,
                extras,
            )

    # status
    ok, reason = _status_allows(ag, action)
    if not ok:
        _audit(nha_id, action, "DENY", reason, scope=scope, extra=extras)
        return EnforcementResult(
            False,
            "DENY",
            reason,
            POLICY_VERSION,
            str(uuid.uuid4()),
            nha_id,
            action,
            scope,
            extras,
        )

    # permission-level action
    if not _permits_action(ag, action):
        if ALLOW_WARN:
            _audit(
                nha_id,
                action,
                "WARN",
                "permission_not_allowed",
                scope=scope,
                extra=extras,
            )
            return EnforcementResult(
                True,
                "WARN",
                "permission_not_allowed",
                POLICY_VERSION,
                str(uuid.uuid4()),
                nha_id,
                action,
                scope,
                extras,
            )
        _audit(
            nha_id, action, "DENY", "permission_not_allowed", scope=scope, extra=extras
        )
        return EnforcementResult(
            False,
            "DENY",
            "permission_not_allowed",
            POLICY_VERSION,
            str(uuid.uuid4()),
            nha_id,
            action,
            scope,
            extras,
        )

    # optional scope
    if scope and not _has_scope(ag, scope):
        if ALLOW_WARN:
            _audit(
                nha_id, action, "WARN", "scope_not_allowed", scope=scope, extra=extras
            )
            return EnforcementResult(
                True,
                "WARN",
                "scope_not_allowed",
                POLICY_VERSION,
                str(uuid.uuid4()),
                nha_id,
                action,
                scope,
                extras,
            )
        _audit(nha_id, action, "DENY", "scope_not_allowed", scope=scope, extra=extras)
        return EnforcementResult(
            False,
            "DENY",
            "scope_not_allowed",
            POLICY_VERSION,
            str(uuid.uuid4()),
            nha_id,
            action,
            scope,
            extras,
        )

    # optional secret
    if require_secret and not _has_secret(ag, require_secret):
        _audit(nha_id, action, "DENY", "secret_not_allowed", scope=scope, extra=extras)
        return EnforcementResult(
            False,
            "DENY",
            "secret_not_allowed",
            POLICY_VERSION,
            str(uuid.uuid4()),
            nha_id,
            action,
            scope,
            extras,
        )

    # all good
    _audit(nha_id, action, "ALLOW", "ok", scope=scope, extra=extras)
    return EnforcementResult(
        True,
        "ALLOW",
        "ok",
        POLICY_VERSION,
        str(uuid.uuid4()),
        nha_id,
        action,
        scope,
        extras,
    )


# -------------------------
# Health pentru enforcer
# -------------------------
def health() -> dict:
    """Get enforcer health status"""
    return {
        "mode": MODE,
        "fail_closed": FAIL_CLOSED,
        "registry_version": _cache_version,
        "agents_cached": len(_cache),
        "policy_version": POLICY_VERSION,
        "audit_file": str(AUDIT_FILE),
    }


# -------------------------
# Utility functions
# -------------------------
def get_agent_info(nha_id: str) -> Optional[dict]:
    """Get agent information for debugging"""
    ag = _get_agent(nha_id)
    if not ag:
        return None
    return {
        "id": ag.id,
        "name": ag.name,
        "category": ag.category,
        "status": ag.status,
        "permissions": ag.permissions,
        "secrets": ag.secrets,
        "capabilities": [{"name": c.name, "scopes": c.scopes} for c in ag.capabilities],
    }


def list_active_agents() -> List[str]:
    """List all active agent IDs"""
    with _lock:
        return [nha_id for nha_id, agent in _cache.items() if agent.status == "active"]


def get_audit_stats() -> dict:
    """Get audit statistics"""
    try:
        if not AUDIT_FILE.exists():
            return {
                "total_records": 0,
                "deny_count": 0,
                "allow_count": 0,
                "warn_count": 0,
            }

        deny_count = 0
        allow_count = 0
        warn_count = 0
        total_records = 0

        with AUDIT_FILE.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        total_records += 1
                        if record.get("result") == "DENY":
                            deny_count += 1
                        elif record.get("result") == "ALLOW":
                            allow_count += 1
                        elif record.get("result") == "WARN":
                            warn_count += 1
                    except json.JSONDecodeError:
                        continue

        return {
            "total_records": total_records,
            "deny_count": deny_count,
            "allow_count": allow_count,
            "warn_count": warn_count,
            "deny_rate": deny_count / total_records if total_records > 0 else 0,
        }
    except Exception:
        return {"error": "Failed to read audit stats"}
