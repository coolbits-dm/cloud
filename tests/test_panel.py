# tests/test_panel.py
from pathlib import Path
import json

def test_panel_state_exists():
    p = Path("panel/state.json")
    assert p.exists(), "panel/state.json missing"
    s = json.loads(p.read_text(encoding="utf-8"))
    assert s.get("milestone") == "M16"
