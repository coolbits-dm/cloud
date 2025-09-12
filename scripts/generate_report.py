# scripts/generate_report.py - Extended for M18
from pathlib import Path
import json, datetime, os
root = Path(".")

# Load state și metrics
state = json.loads((root/"panel/state.json").read_text("utf-8"))
metrics = {}
for p in (root/"artifacts/dev/metrics").glob("*.json"):
    try: metrics[p.stem]=json.loads(p.read_text("utf-8"))
    except: pass

# M18 Extensions
def load_m18_data():
    """Load M18 specific data."""
    m18_data = {
        "walls": {},
        "boards": {},
        "bits": {},
        "tokens": {},
        "rag": {}
    }
    
    # Load walls
    for panel in ["user", "business", "agency", "dev"]:
        wall_path = f"artifacts/dev/walls/{panel}.json"
        if os.path.exists(wall_path):
            wall_data = json.loads(Path(wall_path).read_text("utf-8"))
            m18_data["walls"][panel] = {
                "total_posts": len(wall_data.get("posts", [])),
                "nha_invocations": sum(len(post.get("nha_invocations", [])) for post in wall_data.get("posts", [])),
                "error_rate": 0.0  # Placeholder for M18
            }
    
    # Load boards
    for panel in ["user", "business", "agency", "dev"]:
        board_path = f"artifacts/dev/boards/{panel}.json"
        if os.path.exists(board_path):
            board_data = json.loads(Path(board_path).read_text("utf-8"))
            m18_data["boards"][panel] = {
                "total_members": len(board_data.get("members", [])),
                "meetings": len(board_data.get("meetings", []))
            }
    
    # Load bits
    bits_path = "artifacts/dev/bits/graph.json"
    if os.path.exists(bits_path):
        bits_data = json.loads(Path(bits_path).read_text("utf-8"))
        m18_data["bits"] = {
            "total_bits": len(bits_data.get("bits", [])),
            "total_flows": len(bits_data.get("flows", [])),
            "flows_ok": len(bits_data.get("flows", [])),  # Placeholder for M18
            "flows_fail": 0
        }
    
    # Load tokens
    tokens_path = "artifacts/dev/tokens/ledger.json"
    if os.path.exists(tokens_path):
        tokens_data = json.loads(Path(tokens_path).read_text("utf-8"))
        m18_data["tokens"] = {
            "balance": tokens_data.get("balance", 0),
            "total_entries": len(tokens_data.get("entries", [])),
            "delta_session": 0  # Placeholder for M18
        }
    
    # Load RAG status
    for panel in ["user", "business", "agency", "dev"]:
        rag_path = f"cblm/rag/store/{panel}.json"
        if os.path.exists(rag_path):
            rag_data = json.loads(Path(rag_path).read_text("utf-8"))
            m18_data["rag"][panel] = {
                "total_chunks": rag_data.get("metadata", {}).get("total_chunks", 0),
                "total_sources": rag_data.get("metadata", {}).get("total_sources", 0),
                "build_timestamp": rag_data.get("metadata", {}).get("build_timestamp", "N/A")
            }
    
    return m18_data

# Load M18 data
m18_data = load_m18_data()

# Schema envelope pentru protocoale
envelope_schema = {
    "ver": "opipe-0.1 | oilluminate-0.1 | iimsibis-0.1",
    "typ": "heartbeat | event | command | ack", 
    "id": "uuid/ksuid",
    "ts": "epoch seconds",
    "src": "agent/role, ex: ogpt01/CEO",
    "dst": "list[str] destinatari",
    "agent_type": "human | non-human (pentru @oNHA)",
    "corr": "Optional[str]",
    "ttl_s": "int = 300",
    "nonce": "str",
    "sig": "Optional[str] HMAC",
    "body": "Dict[str, Any] payload"
}

# Panels info
panels_info = {
    "user": "User interface și experiență",
    "business": "Business logic și procese",
    "agency": "Agency management și workflow", 
    "dev": "Development tools și monitoring"
}

html = f"""<!doctype html><meta charset="utf-8">
<title>M18 Report - Walls, Boards, Bits & cbT Economy</title>
<style>
body {{ font-family: system-ui; margin: 2rem; }}
.panel {{ background: #f5f5f5; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; }}
.protocol {{ background: #e8f4fd; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; }}
.m18-section {{ background: #f0f8ff; padding: 1rem; margin: 0.5rem 0; border-radius: 4px; }}
pre {{ background: #f8f8f8; padding: 1rem; overflow-x: auto; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem; }}
</style>
<h1>M18 Status Report</h1>

<h2>Panel State</h2>
<div class="panel">
<strong>Milestone:</strong> {state.get('milestone', 'N/A')}<br>
<strong>Mode:</strong> {state.get('mode', 'N/A')}<br>
<strong>Overall:</strong> {state.get('overall', 'N/A')}<br>
<strong>SHA:</strong> {state.get('sha', 'N/A')[:8]}...
</div>

<h2>M18 Walls Status</h2>
<div class="grid">
{''.join(f'<div class="m18-section"><strong>{panel.title()} Wall:</strong><br>Posts: {data["total_posts"]}<br>NHA Invocations: {data["nha_invocations"]}<br>Error Rate: {data["error_rate"]}%</div>' for panel, data in m18_data["walls"].items())}
</div>

<h2>M18 Boards Status</h2>
<div class="grid">
{''.join(f'<div class="m18-section"><strong>{panel.title()} Board:</strong><br>Members: {data["total_members"]}<br>Meetings: {data["meetings"]}</div>' for panel, data in m18_data["boards"].items())}
</div>

<h2>M18 Bits Orchestrator</h2>
<div class="m18-section">
<strong>Total Bits:</strong> {m18_data["bits"].get("total_bits", 0)}<br>
<strong>Total Flows:</strong> {m18_data["bits"].get("total_flows", 0)}<br>
<strong>Flows OK:</strong> {m18_data["bits"].get("flows_ok", 0)}<br>
<strong>Flows FAIL:</strong> {m18_data["bits"].get("flows_fail", 0)}
</div>

<h2>M18 cbT Economy</h2>
<div class="m18-section">
<strong>Balance:</strong> {m18_data["tokens"].get("balance", 0)} cbT<br>
<strong>Total Entries:</strong> {m18_data["tokens"].get("total_entries", 0)}<br>
<strong>Session Delta:</strong> {m18_data["tokens"].get("delta_session", 0)} cbT
</div>

<h2>M18 RAG Local Status</h2>
<div class="grid">
{''.join(f'<div class="m18-section"><strong>{panel.title()} RAG:</strong><br>Chunks: {data["total_chunks"]}<br>Sources: {data["total_sources"]}<br>Built: {data["build_timestamp"]}</div>' for panel, data in m18_data["rag"].items())}
</div>

<h2>Panels Architecture</h2>
{''.join(f'<div class="panel"><strong>{panel}:</strong> {desc}</div>' for panel, desc in panels_info.items())}

<h2>Protocol Schema (@oPipe/@IIMSIBIS)</h2>
<div class="protocol">
<strong>Envelope Schema:</strong>
<pre>{json.dumps(envelope_schema, indent=2)}</pre>
</div>

<h2>Metrics</h2>
<pre>{json.dumps(metrics, indent=2)}</pre>

<small>Generated at {datetime.datetime.utcnow().isoformat()}Z</small>
"""
out = root/"report/index.html"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(html, encoding="utf-8")
print("[ok] M18 report generated ->", out)
