#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai Local Endpoint - Quick Test Script
Tests all endpoints to ensure they're working properly
"""

import requests
import json
from datetime import datetime


def test_endpoint(url, description):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {description}: Error - {e}")
        return False


def test_endpoints():
    """Test all endpoints"""
    base_url = "http://localhost:3001"

    print("🚀 CoolBits.ai Local Endpoint - Quick Test")
    print("=" * 50)
    print(f"Testing at: {datetime.now().strftime('%H:%M:%S')}")
    print()

    endpoints = [
        (f"{base_url}/api/status", "API Status"),
        (f"{base_url}/api/board/members", "Board Members"),
        (f"{base_url}/api/logs", "Logs"),
        (f"{base_url}/api/history", "History"),
        (f"{base_url}/", "Admin Console"),
    ]

    passed = 0
    total = len(endpoints)

    for url, description in endpoints:
        if test_endpoint(url, description):
            passed += 1

    print()
    print("=" * 50)
    print(f"Results: {passed}/{total} endpoints working")

    if passed == total:
        print("🎉 All endpoints are working perfectly!")
    else:
        print(f"⚠️  {total - passed} endpoints need attention")

    print()
    print("📊 Endpoint Summary:")
    print(f"• API Status: http://localhost:3001/api/status")
    print(f"• Board Members: http://localhost:3001/api/board/members")
    print(f"• Admin Console: http://localhost:3001/")


if __name__ == "__main__":
    test_endpoints()
