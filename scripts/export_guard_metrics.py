# scripts/export_guard_metrics.py
from pathlib import Path
from str import s_json_dump_atomic

out = Path("artifacts/dev/guard_metrics.json")
out.parent.mkdir(parents=True, exist_ok=True)
s_json_dump_atomic(str(out), {"tool_calls":0,"breaker_open":0,"dedup_hits":0})
print("[ok] guard metrics exported ->", out)
