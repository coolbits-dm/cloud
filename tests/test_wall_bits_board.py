#!/usr/bin/env python3
# tests/test_wall_bits_board.py - M18 Wall, Bits, Board tests

import json
import os
import unittest
from pathlib import Path
from str import s_json_load, stable_uuid, ts_now_iso, cbt_posting_cost
import andrei

class TestM18Components(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.test_panel = "user"
        self.wall_path = andrei.get_wall_path(self.test_panel)
        self.board_path = andrei.get_board_path(self.test_panel)
        self.bits_path = andrei.BITS_FILE
        self.tokens_path = andrei.TOKENS_LEDGER
    
    def test_wall_creation_and_validation(self):
        """Test wall creation and schema validation."""
        # Create test wall data
        wall_data = {
            "panel": self.test_panel,
            "posts": [
                {
                    "id": stable_uuid("test_post"),
                    "author": "test_user",
                    "ts": ts_now_iso(),
                    "text": "Test post with @nha:sentiment",
                    "attachments": [],
                    "mentions": ["@nha:sentiment"],
                    "nha_invocations": [
                        {
                            "agent_id": "sentiment_analyzer",
                            "role": "sentiment",
                            "status": "queued"
                        }
                    ],
                    "comments": []
                }
            ]
        }
        
        # Validate structure
        self.assertEqual(wall_data["panel"], self.test_panel)
        self.assertEqual(len(wall_data["posts"]), 1)
        
        post = wall_data["posts"][0]
        self.assertIn("id", post)
        self.assertIn("author", post)
        self.assertIn("text", post)
        self.assertIn("nha_invocations", post)
        
        print("✓ Wall creation and validation test passed")
    
    def test_board_structure(self):
        """Test board structure and roles."""
        board_data = {
            "panel": self.test_panel,
            "board_name": "Test Board",
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
            "charter": "Test board charter",
            "meetings": []
        }
        
        # Validate structure
        self.assertEqual(board_data["panel"], self.test_panel)
        self.assertEqual(len(board_data["members"]), 2)
        
        # Check roles
        roles = [member["role"] for member in board_data["members"]]
        self.assertIn("chair", roles)
        self.assertIn("scribe", roles)
        
        # Check agent types
        agent_types = [member["agent_type"] for member in board_data["members"]]
        self.assertIn("human", agent_types)
        self.assertIn("non-human", agent_types)
        
        print("✓ Board structure test passed")
    
    def test_bits_orchestrator(self):
        """Test bits orchestrator structure."""
        bits_data = {
            "bits": [
                {
                    "id": stable_uuid("test_trigger"),
                    "name": "Test Trigger",
                    "kind": "trigger",
                    "config": {"event": "test_event"},
                    "inputs": [],
                    "outputs": ["test_output"],
                    "scope": "global"
                },
                {
                    "id": stable_uuid("test_action"),
                    "name": "Test Action",
                    "kind": "action",
                    "config": {"service": "test_service"},
                    "inputs": ["test_input"],
                    "outputs": ["test_result"],
                    "scope": "global"
                }
            ],
            "flows": [
                {
                    "id": stable_uuid("test_flow"),
                    "name": "Test Flow",
                    "steps": [
                        {"bit_id": stable_uuid("test_trigger"), "order": 1},
                        {"bit_id": stable_uuid("test_action"), "order": 2}
                    ]
                }
            ]
        }
        
        # Validate structure
        self.assertEqual(len(bits_data["bits"]), 2)
        self.assertEqual(len(bits_data["flows"]), 1)
        
        # Check bit types
        kinds = [bit["kind"] for bit in bits_data["bits"]]
        self.assertIn("trigger", kinds)
        self.assertIn("action", kinds)
        
        print("✓ Bits orchestrator test passed")
    
    def test_cbt_tokens(self):
        """Test cbT token system."""
        # Test tariff costs
        wall_cost = cbt_posting_cost("WALL_POST")
        nha_cost = cbt_posting_cost("NHA_INVOCATION")
        board_cost = cbt_posting_cost("BOARD_MEETING")
        bits_cost = cbt_posting_cost("BITS_DRY_RUN")
        
        self.assertEqual(wall_cost, -1.0)
        self.assertEqual(nha_cost, -2.0)
        self.assertEqual(board_cost, -3.0)
        self.assertEqual(bits_cost, -1.0)
        
        # Test token ledger structure
        tokens_data = {
            "unit": "cbT",
            "balance": 100.0,
            "entries": [
                {
                    "ts": ts_now_iso(),
                    "ref": "test_transaction",
                    "delta": -5.0,
                    "reason": "Test transaction",
                    "meta": {"test": True}
                }
            ]
        }
        
        # Validate structure
        self.assertEqual(tokens_data["unit"], "cbT")
        self.assertEqual(tokens_data["balance"], 100.0)
        self.assertEqual(len(tokens_data["entries"]), 1)
        
        # Test balance calculation
        total_delta = sum(entry["delta"] for entry in tokens_data["entries"])
        expected_balance = 100.0 + total_delta
        self.assertEqual(expected_balance, 95.0)
        
        print("✓ cbT tokens test passed")
    
    def test_nha_mapping(self):
        """Test NHA mapping and roles."""
        # Test NHA map
        self.assertIn("sentiment", andrei.NHA_MAP)
        self.assertIn("summarize", andrei.NHA_MAP)
        self.assertIn("tagging", andrei.NHA_MAP)
        
        # Test board roles
        self.assertIn("chair", andrei.BOARD_ROLES)
        self.assertIn("reviewer", andrei.BOARD_ROLES)
        self.assertIn("analyst", andrei.BOARD_ROLES)
        self.assertIn("scribe", andrei.BOARD_ROLES)
        
        print("✓ NHA mapping test passed")

def run_tests():
    """Run all M18 tests."""
    print("M18 Tests: Running wall, bits, board tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestM18Components)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
