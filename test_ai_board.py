#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for CoolBits.ai Offline AI Board
"""

import asyncio
import aiohttp
import json


async def test_ai_board():
    """Test AI Board endpoints"""
    base_url = "http://localhost:8082"

    async with aiohttp.ClientSession() as session:
        print("🧪 Testing CoolBits.ai Offline AI Board...")
        print("=" * 50)

        # Test health check
        try:
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Health Check: PASSED")
                    print(f"   Roles: {data['roles_count']}")
                    print(f"   Panels: {data['panels_count']}")
                    print(f"   Bits: {data['bits_count']}")
                else:
                    print(f"❌ Health Check: FAILED ({response.status})")
        except Exception as e:
            print(f"❌ Health Check: ERROR - {e}")

        # Test organization structure
        try:
            async with session.get(f"{base_url}/organization") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Organization Structure: PASSED")
                    print(f"   Total Roles: {data['total_roles']}")
                else:
                    print(f"❌ Organization Structure: FAILED ({response.status})")
        except Exception as e:
            print(f"❌ Organization Structure: ERROR - {e}")

        # Test panels
        try:
            async with session.get(f"{base_url}/panels") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Panels System: PASSED")
                    print(f"   Total Panels: {data['total_panels']}")
                else:
                    print(f"❌ Panels System: FAILED ({response.status})")
        except Exception as e:
            print(f"❌ Panels System: ERROR - {e}")

        # Test bits framework
        try:
            async with session.get(f"{base_url}/bits") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Bits Framework: PASSED")
                    print(f"   Total Bits: {data['total_bits']}")
                else:
                    print(f"❌ Bits Framework: FAILED ({response.status})")
        except Exception as e:
            print(f"❌ Bits Framework: ERROR - {e}")

        # Test cbT economy
        try:
            async with session.get(f"{base_url}/cbt") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ cbT Economy: PASSED")
                    print(
                        f"   Total Supply: {data['cbt_economy']['total_supply']:,} cbT"
                    )
                else:
                    print(f"❌ cbT Economy: FAILED ({response.status})")
        except Exception as e:
            print(f"❌ cbT Economy: ERROR - {e}")

        # Test board status
        try:
            async with session.get(f"{base_url}/board") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ Board Status: PASSED")
                    print(f"   Status: {data['board_status']['status']}")
                    print(f"   Mode: {data['board_status']['mode']}")
                else:
                    print(f"❌ Board Status: FAILED ({response.status})")
        except Exception as e:
            print(f"❌ Board Status: ERROR - {e}")

        print("=" * 50)
        print("🎯 AI Board Test Complete!")
        print("📊 Access AI Board at: http://localhost:8082/ai-board")


if __name__ == "__main__":
    asyncio.run(test_ai_board())
