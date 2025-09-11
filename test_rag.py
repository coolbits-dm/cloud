#!/usr/bin/env python3
"""
🤖 Simple RAG Test Script
Test RAG system endpoints

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import requests
import json


def test_rag_system():
    """Test RAG system endpoints"""
    base_url = "http://localhost:8097"

    print("🤖 Testing RAG System")
    print("=" * 40)

    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            print(f"   Status: {response.json()['status']}")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")

    # Test categories endpoint
    try:
        response = requests.get(f"{base_url}/api/categories")
        if response.status_code == 200:
            print("✅ Categories endpoint working")
            categories = response.json()["categories"]
            print(f"   Found {len(categories)} categories")
        else:
            print(f"❌ Categories endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Categories endpoint error: {e}")

    # Test document creation
    try:
        data = {
            "title": "Test Document",
            "content": "This is a test document",
            "category": "b-rag",
            "source": "manual",
        }
        response = requests.post(f"{base_url}/api/documents", json=data)
        if response.status_code == 200:
            print("✅ Document creation working")
            result = response.json()
            print(f"   Created document: {result['document']['id']}")
        else:
            print(f"❌ Document creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Document creation error: {e}")

    print("=" * 40)


if __name__ == "__main__":
    test_rag_system()
