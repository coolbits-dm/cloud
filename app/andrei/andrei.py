# app/andrei/andrei.py
from __future__ import annotations
import os, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

# dependențe locale
try:
    from str import s_json_dump_atomic  # type: ignore
except Exception:
    # fallback minimal, just in case
    import json, io
    def s_json_dump_atomic(path: str, obj: Any, ensure_ascii: bool = False) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with io.open(path, "w", encoding="utf-8") as f:
            json.dump(obj, f, ensure_ascii=ensure_ascii, sort_keys=True, indent=2)
            f.write("\n")

# --- Config -----------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]  # ..\..\..
PANEL_DIR = ROOT / "panel"
STATE_JSON = PANEL_DIR / "state.json"
GATES_JSONL = PANEL_DIR / "gates.jsonl"

MILESTONE = os.getenv("CB_MILESTONE", "M16")
MODE = os.getenv("CB_BILLING_MODE", "dev")
ACTOR = os.getenv("USERNAME") or os.getenv("USER") or "andrei"

# --- oPipe heartbeat (stub minimal) ----------------------------------------

def opipe_heartbeat(actor: str, milestone: str, mode: str) -> Dict[str, Any]:
    # Înlocuiește ulterior cu implementarea reală a @oPipe® (envelope+HMAC)
    now = datetime.now(timezone.utc).isoformat()
    return {
        "ver": "opipe-0.1",
        "type": "heartbeat",
        "ts": now,
        "actor": actor,
        "milestone": milestone,
        "mode": mode,
        "status": "green",
    }

# --- State update -----------------------------------------------------------

def write_state(sha: str | None = None) -> None:
    now = datetime.now(timezone.utc).isoformat()
    state = {
        "milestone": MILESTONE,
        "overall": "HEALTHY",
        "mode": MODE,
        "actor": ACTOR,
        "updated_at": now,
    }
    if sha:
        state["sha"] = sha
    s_json_dump_atomic(str(STATE_JSON), state)

def gate_open(note: str) -> None:
    os.makedirs(PANEL_DIR, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    line = {"ts": now, "milestone": MILESTONE, "note": note}
    with open(GATES_JSONL, "a", encoding="utf-8") as f:
        f.write(__import__("json").dumps(line, sort_keys=True) + "\n")

def git_head_sha() -> str | None:
    try:
        import subprocess
        out = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT))
        return out.decode("utf-8").strip()
    except Exception:
        return None

def main() -> int:
    # sanity
    if MODE not in ("dev", "prod"):
        print(f"[warn] CB_BILLING_MODE invalid: {MODE}, defaulting to dev")
    sha = git_head_sha()
    write_state(sha=sha)
    hb = opipe_heartbeat(ACTOR, MILESTONE, MODE)
    # poți scrie un raport local pentru debugging
    out = ROOT / "artifacts" / "local" / "heartbeat.json"
    os.makedirs(out.parent, exist_ok=True)
    s_json_dump_atomic(str(out), hb)
    print(f"[ok] M16 local update: state.json + heartbeat (sha={sha})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
