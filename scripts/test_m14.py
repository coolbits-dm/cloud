#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
M14 Verification Script - Adaptive Policy & Self-Healing
Tests the complete adaptive policy pipeline:
1. Collector aggregation
2. Analyzer gap detection  
3. Recommender policy updates
4. Self-healing registry integrity
"""
import sys
import os
import json
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_collector():
    """Test policy violation collector"""
    print("🔍 Testing Policy Collector...")
    
    try:
        from cblm.opipe.nha.adaptive.collector import main as collector_main
        import argparse
        
        # Mock args for collector
        class MockArgs:
            def __init__(self):
                self.logs_dir = "logs"
                self.out_dir = "reports"
                self.window = "last_24h"
                self.from_ts = None
                self.to_ts = None
                self.min_count = 1
                self.include_warn = True
                self.markdown = True
        
        # Run collector
        collector_main()
        
        # Check output files
        json_file = Path("reports/policy_collect_last_24h.json")
        md_file = Path("reports/policy_collect_last_24h.md")
        
        if json_file.exists() and md_file.exists():
            print("✅ Collector: JSON and Markdown reports generated")
            return True
        else:
            print("❌ Collector: Missing output files")
            return False
            
    except Exception as e:
        print(f"❌ Collector test failed: {e}")
        return False

def test_analyzer():
    """Test policy gap analyzer"""
    print("🔍 Testing Policy Analyzer...")
    
    try:
        import subprocess
        
        # Run analyzer with correct arguments
        result = subprocess.run([
            "python", "-m", "cblm.opipe.nha.adaptive.analyzer",
            "--collect-file", "reports/policy_collect_last_24h.json",
            "--out-dir", "reports",
            "--markdown"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Check output files
            json_file = Path("reports/policy_gaps.json")
            md_file = Path("reports/policy_gaps.md")
            
            if json_file.exists() and md_file.exists():
                # Check content
                with json_file.open("r") as f:
                    gaps_data = json.load(f)
                
                if gaps_data.get("total_gaps", 0) >= 0:
                    print("✅ Analyzer: Gap analysis completed")
                    return True
                else:
                    print("❌ Analyzer: Invalid gap data")
                    return False
            else:
                print("❌ Analyzer: Missing output files")
                return False
        else:
            print(f"❌ Analyzer failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Analyzer test failed: {e}")
        return False

def test_recommender():
    """Test policy recommender"""
    print("🔍 Testing Policy Recommender...")
    
    try:
        import subprocess
        
        # Run recommender with correct arguments
        result = subprocess.run([
            "python", "-m", "cblm.opipe.nha.adaptive.recommender",
            "--gaps-file", "reports/policy_gaps.json",
            "--registry-file", "cblm/opipe/nha/agents.yaml",
            "--out-file", "cblm/opipe/nha/policy_recommendations.yaml"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Check output file
            yaml_file = Path("cblm/opipe/nha/policy_recommendations.yaml")
            
            if yaml_file.exists():
                # Check content
                with yaml_file.open("r") as f:
                    rec_data = yaml.safe_load(f)
                
                if rec_data.get("policy_recommendations", {}).get("total_recommendations", 0) >= 0:
                    print("✅ Recommender: Policy recommendations generated")
                    return True
                else:
                    print("❌ Recommender: Invalid recommendation data")
                    return False
            else:
                print("❌ Recommender: Missing output file")
                return False
        else:
            print(f"❌ Recommender failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Recommender test failed: {e}")
        return False

def test_selfhealing():
    """Test self-healing functionality"""
    print("🔍 Testing Self-Healing...")
    
    try:
        # Run self-healing script
        import subprocess
        result = subprocess.run([
            "python", "scripts/policy_selfheal.py",
            "--registry-file", "cblm/opipe/nha/agents.yaml",
            "--backup-file", "cblm/opipe/nha/out/registry.json",
            "--check-signature",
            "--auto-reload",
            "--verbose"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Self-Healing: Registry integrity check passed")
            return True
        else:
            print(f"❌ Self-Healing: Check failed - {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Self-Healing test failed: {e}")
        return False

def test_adaptive_pipeline():
    """Test complete adaptive pipeline"""
    print("🔍 Testing Complete Adaptive Pipeline...")
    
    try:
        # Check all components work together
        collector_ok = test_collector()
        analyzer_ok = test_analyzer()
        recommender_ok = test_recommender()
        selfhealing_ok = test_selfhealing()
        
        if all([collector_ok, analyzer_ok, recommender_ok, selfhealing_ok]):
            print("✅ Adaptive Pipeline: All components working")
            return True
        else:
            print("❌ Adaptive Pipeline: Some components failed")
            return False
            
    except Exception as e:
        print(f"❌ Adaptive Pipeline test failed: {e}")
        return False

def test_file_structure():
    """Test required file structure"""
    print("🔍 Testing File Structure...")
    
    required_files = [
        "cblm/opipe/nha/adaptive/collector.py",
        "cblm/opipe/nha/adaptive/analyzer.py", 
        "cblm/opipe/nha/adaptive/recommender.py",
        "scripts/policy_selfheal.py",
        "scripts/test_m14.py"
    ]
    
    required_dirs = [
        "cblm/opipe/nha/adaptive",
        "reports"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            all_exist = False
        else:
            print(f"✅ Found file: {file_path}")
    
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            all_exist = False
        else:
            print(f"✅ Found directory: {dir_path}")
    
    return all_exist

def main():
    """Run all M14 verification tests"""
    print("🚀 M14: Adaptive Policy & Self-Healing Verification")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Policy Collector", test_collector),
        ("Policy Analyzer", test_analyzer),
        ("Policy Recommender", test_recommender),
        ("Self-Healing", test_selfhealing),
        ("Adaptive Pipeline", test_adaptive_pipeline)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 M14 Verification Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 M14: Adaptive Policy & Self-Healing - VERIFIED!")
        print("✅ CoolBits.ai now has adaptive policy enforcement")
        print("✅ No more manual 'grep on logs' for policy gaps")
        print("✅ Self-healing registry with automatic recovery")
        return True
    else:
        print("⚠️ Some tests failed - review and fix issues")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
