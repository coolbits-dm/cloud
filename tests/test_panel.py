# tests/test_panel.py
from pathlib import Path
import json

def test_panel_state_exists():
    p = Path("panel/state.json")
    assert p.exists(), "panel/state.json missing"
    s = json.loads(p.read_text(encoding="utf-8"))
    assert s.get("milestone") == "M17"

def test_panel_panels_tripwire():
    """Tripwire pentru verificarea panel-urilor user/business/agency/dev."""
    p = Path("panel/state.json")
    assert p.exists(), "panel/state.json missing"
    s = json.loads(p.read_text(encoding="utf-8"))
    
    # Verifică că există câmpul panels
    assert "panels" in s, "panels field missing from state.json"
    
    # Verifică că sunt exact 4 panel-uri
    panels = s["panels"]
    assert isinstance(panels, list), "panels must be a list"
    assert len(panels) == 4, f"Expected 4 panels, got {len(panels)}"
    
    # Verifică că sunt panel-urile corecte
    expected_panels = ["user", "business", "agency", "dev"]
    assert set(panels) == set(expected_panels), f"Expected {expected_panels}, got {panels}"
    
    print(f"✅ Panel tripwire passed: {panels}")
