#!/usr/bin/env python3
# tests/test_cbtokens.py - cbT Token system tests

import json
import os
import unittest
from str import s_json_load, s_json_dump_atomic, ts_now_iso, cbt_posting_cost
import andrei

class TestCBTokens(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.test_ledger_path = "test_ledger.json"
        self.initial_balance = 100.0
    
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.test_ledger_path):
            os.remove(self.test_ledger_path)
    
    def test_ledger_creation(self):
        """Test token ledger creation."""
        ledger_data = {
            "unit": "cbT",
            "balance": self.initial_balance,
            "entries": [
                {
                    "ts": ts_now_iso(),
                    "ref": "initial_balance",
                    "delta": self.initial_balance,
                    "reason": "Initial balance",
                    "meta": {"source": "test"}
                }
            ]
        }
        
        s_json_dump_atomic(self.test_ledger_path, ledger_data)
        
        # Verify creation
        loaded_data = s_json_load(self.test_ledger_path)
        self.assertEqual(loaded_data["unit"], "cbT")
        self.assertEqual(loaded_data["balance"], self.initial_balance)
        self.assertEqual(len(loaded_data["entries"]), 1)
        
        print("✓ Ledger creation test passed")
    
    def test_transaction_processing(self):
        """Test transaction processing and balance calculation."""
        # Create initial ledger
        ledger_data = {
            "unit": "cbT",
            "balance": self.initial_balance,
            "entries": [
                {
                    "ts": ts_now_iso(),
                    "ref": "initial_balance",
                    "delta": self.initial_balance,
                    "reason": "Initial balance",
                    "meta": {"source": "test"}
                }
            ]
        }
        
        s_json_dump_atomic(self.test_ledger_path, ledger_data)
        
        # Process transactions
        transactions = [
            {"ref": "wall_post", "delta": cbt_posting_cost("WALL_POST"), "reason": "Wall post"},
            {"ref": "nha_invoke", "delta": cbt_posting_cost("NHA_INVOCATION"), "reason": "NHA invocation"},
            {"ref": "board_meeting", "delta": cbt_posting_cost("BOARD_MEETING"), "reason": "Board meeting"},
            {"ref": "bits_run", "delta": cbt_posting_cost("BITS_DRY_RUN"), "reason": "Bits dry run"}
        ]
        
        # Add transactions
        loaded_data = s_json_load(self.test_ledger_path)
        for tx in transactions:
            entry = {
                "ts": ts_now_iso(),
                "ref": tx["ref"],
                "delta": tx["delta"],
                "reason": tx["reason"],
                "meta": {"test": True}
            }
            loaded_data["entries"].append(entry)
        
        # Calculate new balance
        total_delta = sum(entry["delta"] for entry in loaded_data["entries"])
        loaded_data["balance"] = total_delta
        
        # Save updated ledger
        s_json_dump_atomic(self.test_ledger_path, loaded_data)
        
        # Verify balance calculation
        expected_balance = self.initial_balance + cbt_posting_cost("WALL_POST") + cbt_posting_cost("NHA_INVOCATION") + cbt_posting_cost("BOARD_MEETING") + cbt_posting_cost("BITS_DRY_RUN")
        self.assertEqual(loaded_data["balance"], expected_balance)
        self.assertEqual(len(loaded_data["entries"]), 5)  # 1 initial + 4 transactions
        
        print("✓ Transaction processing test passed")
    
    def test_idempotent_operations(self):
        """Test that double operations produce same result."""
        # Create initial ledger
        ledger_data = {
            "unit": "cbT",
            "balance": self.initial_balance,
            "entries": [
                {
                    "ts": ts_now_iso(),
                    "ref": "initial_balance",
                    "delta": self.initial_balance,
                    "reason": "Initial balance",
                    "meta": {"source": "test"}
                }
            ]
        }
        
        s_json_dump_atomic(self.test_ledger_path, ledger_data)
        
        # First operation
        loaded_data1 = s_json_load(self.test_ledger_path)
        entry1 = {
            "ts": ts_now_iso(),
            "ref": "test_operation",
            "delta": -5.0,
            "reason": "Test operation",
            "meta": {"test": True}
        }
        loaded_data1["entries"].append(entry1)
        loaded_data1["balance"] += entry1["delta"]
        s_json_dump_atomic(self.test_ledger_path, loaded_data1)
        
        # Second operation (should be idempotent)
        loaded_data2 = s_json_load(self.test_ledger_path)
        entry2 = {
            "ts": ts_now_iso(),
            "ref": "test_operation",
            "delta": -5.0,
            "reason": "Test operation",
            "meta": {"test": True}
        }
        loaded_data2["entries"].append(entry2)
        loaded_data2["balance"] += entry2["delta"]
        s_json_dump_atomic(self.test_ledger_path, loaded_data2)
        
        # Verify idempotency
        final_data = s_json_load(self.test_ledger_path)
        expected_balance = self.initial_balance - 10.0  # Two operations of -5.0 each
        self.assertEqual(final_data["balance"], expected_balance)
        
        print("✓ Idempotent operations test passed")
    
    def test_negative_balance_handling(self):
        """Test negative balance handling in dev mode."""
        # Create ledger with low balance
        ledger_data = {
            "unit": "cbT",
            "balance": 5.0,
            "entries": [
                {
                    "ts": ts_now_iso(),
                    "ref": "initial_balance",
                    "delta": 5.0,
                    "reason": "Initial balance",
                    "meta": {"source": "test"}
                }
            ]
        }
        
        s_json_dump_atomic(self.test_ledger_path, ledger_data)
        
        # Process expensive transaction
        loaded_data = s_json_load(self.test_ledger_path)
        expensive_entry = {
            "ts": ts_now_iso(),
            "ref": "expensive_operation",
            "delta": cbt_posting_cost("BOARD_MEETING"),  # -3.0
            "reason": "Expensive operation",
            "meta": {"test": True}
        }
        loaded_data["entries"].append(expensive_entry)
        loaded_data["balance"] += expensive_entry["delta"]
        
        # In dev mode, negative balance should be allowed
        self.assertEqual(loaded_data["balance"], 2.0)  # 5.0 - 3.0 = 2.0
        
        # Test going negative
        negative_entry = {
            "ts": ts_now_iso(),
            "ref": "negative_operation",
            "delta": -5.0,
            "reason": "Operation that goes negative",
            "meta": {"test": True}
        }
        loaded_data["entries"].append(negative_entry)
        loaded_data["balance"] += negative_entry["delta"]
        
        # Should be negative in dev mode
        self.assertEqual(loaded_data["balance"], -3.0)
        
        print("✓ Negative balance handling test passed")

def run_tests():
    """Run all cbT token tests."""
    print("cbT Tests: Running token system tests...")
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCBTokens)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success/failure
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
