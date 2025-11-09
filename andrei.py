# andrei.py - Constants & Conventions M18
# Authoritative source for M18 configuration

from pathlib import Path
from typing import Dict, List

# --- Panel Configuration ---
PANELS = ["user", "business", "agency", "dev"]

# --- File Paths ---
WALL_FILE_FMT = "artifacts/dev/walls/{panel}.json"
BOARD_FILE_FMT = "artifacts/dev/boards/{panel}.json"
BITS_FILE = "artifacts/dev/bits/graph.json"
TOKENS_LEDGER = "artifacts/dev/tokens/ledger.json"
RAG_STORE_FMT = "cblm/rag/store/{panel}.json"

# --- Schema Paths ---
SCHEMAS = {
    "wall": "panel/schemas/wall.schema.json",
    "board": "panel/schemas/board.schema.json", 
    "bit": "panel/schemas/bit.schema.json",
    "token": "panel/schemas/token.schema.json"
}

# --- Tariff Configuration ---
TARIFF = {
    "WALL_POST": -1.0,
    "NHA_INVOCATION": -2.0,
    "BOARD_MEETING": -3.0,
    "BITS_DRY_RUN": -1.0
}

# --- Board Roles ---
BOARD_ROLES = ["chair", "reviewer", "analyst", "scribe"]

# --- NHA Mapping ---
NHA_MAP = {
    "sentiment": "analyze_sentiment",
    "summarize": "generate_summary", 
    "tagging": "extract_tags"
}

# --- M18 Answers (to be populated by @oRunner) ---
M18_ANSWERS = {
    "walls_scope": "per panel: u-wall/b-wall/a-wall/d-wall map to user/business/agency/dev",
    "bits_scope": "global graph in artifacts/dev/bits/graph.json with scope field",
    "board_roles": BOARD_ROLES,
    "nha_map": list(NHA_MAP.keys()),
    "tokens_dev_gate": "dev mode allows negative balance with alerts only"
}

def get_wall_path(panel: str) -> str:
    """Get wall file path for panel."""
    return WALL_FILE_FMT.format(panel=panel)

def get_board_path(panel: str) -> str:
    """Get board file path for panel."""
    return BOARD_FILE_FMT.format(panel=panel)

def get_rag_path(panel: str) -> str:
    """Get RAG store path for panel."""
    return RAG_STORE_FMT.format(panel=panel)

def validate_panel(panel: str) -> bool:
    """Validate panel name."""
    return panel in PANELS

def get_tariff_cost(action: str) -> float:
    """Get cost for action."""
    return TARIFF.get(action, 0.0)
