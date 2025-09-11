#!/usr/bin/env python3
"""Update M15 milestone status"""

import json
import sys
from pathlib import Path

# Add str.py to path
sys.path.append(str(Path("app/andrei/secure")))

from str import set_milestone_status

# Load current state
with open("panel/state.json", "r", encoding="utf-8") as f:
    state = json.load(f)

# Set M15 status
set_milestone_status("M15", state)

print("✅ M15 milestone status updated successfully")
