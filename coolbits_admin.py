#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai Administration Script
CEO: Andrei - andrei@coolbits.ro
Managed by: oCursor (Local Development)

This script provides comprehensive administration capabilities for:
- User and role management
- Panel system administration
- Bits framework management
- cbT economy operations
- Security and RBAC management
"""

import json
import yaml
import argparse
import sys
from datetime import datetime
from typing import Dict, Optional, Any
import requests


class CoolBitsAdmin:
    """CoolBits.ai Administration Script"""

    def __init__(
        self,
        config_file: str = "coolbits_ai_config.json",
        base_url: str = "http://localhost:8082",
    ):
        self.config_file = config_file
        self.base_url = base_url
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON or YAML file"""
        try:
            if self.config_file.endswith(".yaml") or self.config_file.endswith(".yml"):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file {self.config_file} not found!")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            sys.exit(1)

    def save_config(self):
        """Save configuration back to file"""
        try:
            if self.config_file.endswith(".yaml") or self.config_file.endswith(".yml"):
                with open(self.config_file, "w", encoding="utf-8") as f:
                    yaml.dump(
                        self.config, f, default_flow_style=False, allow_unicode=True
                    )
            else:
                with open(self.config_file, "w", encoding="utf-8") as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"✅ Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")

    def make_api_request(
        self, endpoint: str, method: str = "GET", data: Optional[Dict] = None
    ) -> Optional[Dict]:
        """Make API request to CoolBits.ai server"""
        try:
            url = f"{self.base_url}{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=10)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=10)
            else:
                print(f"❌ Unsupported HTTP method: {method}")
                return None

            if response.status_code == 200:
                return response.json()
            else:
                print(
                    f"❌ API request failed: {response.status_code} - {response.text}"
                )
                return None
        except requests.exceptions.RequestException as e:
            print(f"❌ API request error: {e}")
            return None

    def list_roles(self, category: Optional[str] = None):
        """List all roles or roles by category"""
        if category:
            endpoint = f"/roles/{category}"
            result = self.make_api_request(endpoint)
            if result and result.get("success"):
                roles = result.get("roles", {})
                print(f"\n📋 Roles in {category.upper()} category:")
                print("=" * 50)
                for role_id, role_data in roles.items():
                    if isinstance(role_data, dict) and "name" in role_data:
                        print(f"• {role_data['name']} ({role_id})")
                        print(f"  Email: {role_data.get('email', 'N/A')}")
                        print(f"  Agent: {role_data.get('agent', 'N/A')}")
                        print(f"  Access Level: {role_data.get('access_level', 'N/A')}")
                        print(f"  Status: {role_data.get('status', 'N/A')}")
                        print(
                            f"  cbT Allocation: {role_data.get('cbt_allocation', 'N/A')}"
                        )
                        print()
        else:
            result = self.make_api_request("/roles")
            if result and result.get("success"):
                roles = result.get("roles", {})
                print(f"\n📋 All Roles ({result.get('total_roles', 0)} total):")
                print("=" * 50)
                for category_name, category_roles in roles.items():
                    print(f"\n🏢 {category_name.upper()}:")
                    for role_id, role_data in category_roles.items():
                        if isinstance(role_data, dict) and "name" in role_data:
                            print(f"  • {role_data['name']} ({role_id})")
                        elif isinstance(role_data, dict):
                            for sub_role_id, sub_role_data in role_data.items():
                                if (
                                    isinstance(sub_role_data, dict)
                                    and "name" in sub_role_data
                                ):
                                    print(
                                        f"    • {sub_role_data['name']} ({sub_role_id})"
                                    )

    def list_panels(self):
        """List all panels"""
        result = self.make_api_request("/panels")
        if result and result.get("success"):
            panels = result.get("panels", {})
            print(f"\n🎛️ All Panels ({result.get('total_panels', 0)} total):")
            print("=" * 50)
            for panel_id, panel_data in panels.items():
                print(f"• {panel_data['name']} ({panel_id})")
                print(f"  Description: {panel_data.get('description', 'N/A')}")
                print(f"  Access Level: {panel_data.get('access_level', 'N/A')}")
                print(f"  Status: {panel_data.get('status', 'N/A')}")
                print(f"  cbT Allocation: {panel_data.get('cbt_allocation', 'N/A')}")
                print(f"  Features: {', '.join(panel_data.get('features', []))}")
                print()

    def list_bits(self):
        """List all bits framework"""
        result = self.make_api_request("/bits")
        if result and result.get("success"):
            bits = result.get("bits_framework", {})
            print(f"\n🔧 Bits Framework ({result.get('total_bits', 0)} total):")
            print("=" * 50)
            for bit_id, bit_data in bits.items():
                print(f"• {bit_data['name']} ({bit_id})")
                print(f"  Description: {bit_data.get('description', 'N/A')}")
                print(f"  Access Level: {bit_data.get('access_level', 'N/A')}")
                print(f"  Status: {bit_data.get('status', 'N/A')}")
                print(f"  cbT Allocation: {bit_data.get('cbt_allocation', 'N/A')}")
                print(f"  Features: {', '.join(bit_data.get('features', []))}")
                print()

    def show_cbt_economy(self):
        """Show cbT economy status"""
        result = self.make_api_request("/cbt")
        if result and result.get("success"):
            cbt = result.get("cbt_economy", {})
            print("\n💰 cbT Economy Status:")
            print("=" * 50)
            print(f"Total Supply: {cbt.get('total_supply', 0):,} cbT")
            print(f"Circulating: {cbt.get('circulating', 0):,} cbT")
            print(f"Reserved: {cbt.get('reserved', 0):,} cbT")
            print(f"Status: {cbt.get('status', 'N/A')}")
            print("\nAllocation by Bit Type:")
            for bit_type, allocation in cbt.get("allocation", {}).items():
                print(f"  {bit_type}: {allocation:,} cbT")
            print(f"\nTotal Transactions: {len(cbt.get('transactions', []))}")

    def show_board_status(self):
        """Show AI Board status"""
        result = self.make_api_request("/board")
        if result and result.get("success"):
            board = result.get("board_status", {})
            print("\n🎯 AI Board Status:")
            print("=" * 50)
            print(f"Roles: {board.get('roles', 0)}")
            print(f"Panels: {board.get('panels', 0)}")
            print(f"Bits: {board.get('bits', 0)}")
            print(f"cbT Total: {board.get('cbt_total', 0):,}")
            print(f"Status: {board.get('status', 'N/A')}")
            print(f"Mode: {board.get('mode', 'N/A')}")

    def execute_board_command(self, command: str):
        """Execute AI Board command"""
        data = {"command": command}
        result = self.make_api_request("/board/command", "POST", data)
        if result and result.get("success"):
            print(f"\n🎯 Board Command '{command}' executed:")
            print("=" * 50)
            response = result.get("response", {})
            if isinstance(response, dict):
                for key, value in response.items():
                    print(f"{key}: {value}")
            else:
                print(response)
        else:
            print(f"❌ Failed to execute command '{command}'")

    def transfer_cbt(self, from_bit: str, to_bit: str, amount: int):
        """Transfer cbT tokens between bit types"""
        data = {"from": from_bit, "to": to_bit, "amount": amount}
        result = self.make_api_request("/cbt/transfer", "POST", data)
        if result and result.get("success"):
            transaction = result.get("transaction", {})
            print("\n💰 cbT Transfer Successful:")
            print("=" * 50)
            print(f"From: {transaction.get('from', 'N/A')}")
            print(f"To: {transaction.get('to', 'N/A')}")
            print(f"Amount: {transaction.get('amount', 0):,} cbT")
            print(f"Transaction ID: {transaction.get('id', 'N/A')}")
            print(f"Status: {transaction.get('status', 'N/A')}")
            print(f"Timestamp: {transaction.get('timestamp', 'N/A')}")
        else:
            print(f"❌ Failed to transfer {amount:,} cbT from {from_bit} to {to_bit}")

    def show_health(self):
        """Show system health"""
        result = self.make_api_request("/health")
        if result:
            print("\n🏥 System Health:")
            print("=" * 50)
            print(f"Status: {result.get('status', 'N/A')}")
            print(f"Service: {result.get('service', 'N/A')}")
            print(f"CEO: {result.get('ceo', 'N/A')}")
            print(f"Port: {result.get('port', 'N/A')}")
            print(f"Roles Count: {result.get('roles_count', 0)}")
            print(f"Panels Count: {result.get('panels_count', 0)}")
            print(f"Bits Count: {result.get('bits_count', 0)}")
            print(f"Timestamp: {result.get('timestamp', 'N/A')}")

    def generate_report(self):
        """Generate comprehensive system report"""
        print("\n📊 CoolBits.ai System Report")
        print("=" * 60)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("CEO: Andrei - andrei@coolbits.ro")
        print("Managed by: oCursor (Local Development)")
        print()

        self.show_health()
        self.show_board_status()
        self.show_cbt_economy()

        print("\n📋 Organizational Summary:")
        print("=" * 50)
        org_structure = self.config.get("coolbits_ai", {}).get(
            "organizational_structure", {}
        )
        total_roles = 0
        for category, category_data in org_structure.items():
            roles = category_data.get("roles", [])
            role_count = len(roles)
            total_roles += role_count
            print(f"{category.upper()}: {role_count} roles")
        print(f"TOTAL ROLES: {total_roles}")

        print("\n🎛️ Panel Summary:")
        print("=" * 50)
        panels = self.config.get("coolbits_ai", {}).get("panel_system", {})
        for panel_id, panel_data in panels.items():
            print(
                f"{panel_data.get('name', 'N/A')}: {panel_data.get('access_level', 'N/A')}"
            )

        print("\n🔧 Bits Summary:")
        print("=" * 50)
        bits = self.config.get("coolbits_ai", {}).get("bits_framework", {})
        for bit_id, bit_data in bits.items():
            print(
                f"{bit_data.get('name', 'N/A')}: {bit_data.get('access_level', 'N/A')}"
            )


def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="CoolBits.ai Administration Script")
    parser.add_argument(
        "--config", default="coolbits_ai_config.json", help="Configuration file path"
    )
    parser.add_argument(
        "--url", default="http://localhost:8082", help="Base URL for API"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Health command
    subparsers.add_parser("health", help="Show system health")

    # Roles commands
    roles_parser = subparsers.add_parser("roles", help="List roles")
    roles_parser.add_argument("--category", help="Filter by category")

    # Panels command
    subparsers.add_parser("panels", help="List panels")

    # Bits command
    subparsers.add_parser("bits", help="List bits framework")

    # cbT commands
    cbt_parser = subparsers.add_parser("cbt", help="Show cbT economy")
    cbt_parser.add_argument(
        "--transfer",
        nargs=3,
        metavar=("FROM", "TO", "AMOUNT"),
        help="Transfer cbT tokens",
    )

    # Board commands
    board_parser = subparsers.add_parser("board", help="Board operations")
    board_parser.add_argument("--command", help="Execute board command")

    # Report command
    subparsers.add_parser("report", help="Generate comprehensive report")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    admin = CoolBitsAdmin(args.config, args.url)

    if args.command == "health":
        admin.show_health()
    elif args.command == "roles":
        admin.list_roles(args.category)
    elif args.command == "panels":
        admin.list_panels()
    elif args.command == "bits":
        admin.list_bits()
    elif args.command == "cbt":
        if args.transfer:
            from_bit, to_bit, amount = args.transfer
            try:
                amount = int(amount)
                admin.transfer_cbt(from_bit, to_bit, amount)
            except ValueError:
                print("❌ Amount must be a number")
        else:
            admin.show_cbt_economy()
    elif args.command == "board":
        if args.command:
            admin.execute_board_command(args.command)
        else:
            admin.show_board_status()
    elif args.command == "report":
        admin.generate_report()


if __name__ == "__main__":
    main()
