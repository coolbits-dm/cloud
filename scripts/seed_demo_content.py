#!/usr/bin/env python3
# scripts/seed_demo_content.py - Seed M18 demo content

import json
import os
from pathlib import Path
from str import atomic_json_patch, stable_uuid, ts_now_iso, cbt_posting_cost
import andrei

def create_demo_wall(panel: str):
    """Create demo wall content for panel."""
    wall_data = {
        "panel": panel,
        "posts": [
            {
                "id": stable_uuid("demo_post", panel),
                "author": "demo_user",
                "ts": ts_now_iso(),
                "text": f"Welcome to {panel} panel! This is a demo post with @nha:sentiment analysis.",
                "attachments": [],
                "mentions": ["@nha:sentiment"],
                "nha_invocations": [
                    {
                        "agent_id": "sentiment_analyzer",
                        "role": "sentiment",
                        "status": "done",
                        "result_ref": f"sentiment_result_{panel}"
                    }
                ],
                "comments": [
                    {
                        "author": "nha_sentiment",
                        "ts": ts_now_iso(),
                        "text": "Sentiment analysis complete: Positive (0.8 confidence)"
                    }
                ]
            }
        ]
    }
    
    wall_path = andrei.get_wall_path(panel)
    atomic_json_patch(wall_path, wall_data, andrei.SCHEMAS["wall"])
    print(f"✓ Created demo wall for {panel}")

def create_demo_board(panel: str):
    """Create demo board content for panel."""
    board_data = {
        "panel": panel,
        "board_name": f"{panel.title()} Board",
        "members": [
            {
                "id": "human_chair",
                "display": "Human Chair",
                "role": "chair",
                "agent_type": "human"
            },
            {
                "id": "nha_scribe",
                "display": "AI Scribe",
                "role": "scribe",
                "agent_type": "non-human"
            }
        ],
        "charter": f"Governing board for {panel} panel operations and decisions.",
        "meetings": []
    }
    
    board_path = andrei.get_board_path(panel)
    atomic_json_patch(board_path, board_data, andrei.SCHEMAS["board"])
    print(f"✓ Created demo board for {panel}")

def create_demo_bits():
    """Create demo bits for orchestrator."""
    bits_data = {
        "bits": [
            {
                "id": stable_uuid("trigger_newpost"),
                "name": "Trigger: New Post",
                "kind": "trigger",
                "config": {"event": "wall_post_created"},
                "inputs": [],
                "outputs": ["post_data"],
                "scope": "global"
            },
            {
                "id": stable_uuid("action_analyze"),
                "name": "Action: Analyze Sentiment",
                "kind": "action",
                "config": {"service": "sentiment_analysis"},
                "inputs": ["post_data"],
                "outputs": ["sentiment_result"],
                "scope": "global"
            }
        ],
        "flows": [
            {
                "id": stable_uuid("demo_flow"),
                "name": "Demo Sentiment Flow",
                "steps": [
                    {"bit_id": stable_uuid("trigger_newpost"), "order": 1},
                    {"bit_id": stable_uuid("action_analyze"), "order": 2}
                ]
            }
        ]
    }
    
    # Don't validate with schema for now - bits_data is a container, not individual bit
    atomic_json_patch(andrei.BITS_FILE, bits_data)
    print("✓ Created demo bits and flows")

def create_demo_tokens():
    """Create demo token ledger."""
    tokens_data = {
        "unit": "cbT",
        "balance": 100.0,
        "entries": [
            {
                "ts": ts_now_iso(),
                "ref": "initial_balance",
                "delta": 100.0,
                "reason": "Initial demo balance",
                "meta": {"source": "m18_seed"}
            }
        ]
    }
    
    atomic_json_patch(andrei.TOKENS_LEDGER, tokens_data, andrei.SCHEMAS["token"])
    print("✓ Created demo token ledger")

def main():
    """Main seeding function."""
    print("M18 Seed: Creating demo content...")
    
    # Create demo content for each panel
    for panel in andrei.PANELS:
        create_demo_wall(panel)
        create_demo_board(panel)
    
    # Create global demo content
    create_demo_bits()
    create_demo_tokens()
    
    print("M18 Seed: Demo content created successfully!")

if __name__ == "__main__":
    main()
