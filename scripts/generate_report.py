# scripts/generate_report.py
from pathlib import Path
import json, datetime
root = Path(".")
state = json.loads((root/"panel/state.json").read_text("utf-8"))
metrics = {}
for p in (root/"artifacts/dev/metrics").glob("*.json"):
    try: metrics[p.stem]=json.loads(p.read_text("utf-8"))
    except: pass
html = f"""<!doctype html><meta charset="utf-8">
<title>M17 Report</title>
<h1>M17 Status</h1>
<pre>{json.dumps(state, indent=2)}</pre>
<h2>Metrics</h2>
<pre>{json.dumps(metrics, indent=2)}</pre>
<small>Generated at {datetime.datetime.utcnow().isoformat()}Z</small>
"""
out = root/"report/index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("[ok] report generated ->", out)
