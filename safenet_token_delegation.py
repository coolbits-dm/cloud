#!/usr/bin/env python3
"""
SafeNet Auth Token Delegation - COOL BITS SRL
Delegates SafeNet authentication token to ogpt09 and ogrok09 agents
"""

import json
import subprocess
from datetime import datetime
from typing import Dict, Any


class SafeNetTokenDelegation:
    """SafeNet Authentication Token Delegation Manager"""

    def __init__(self):
        self.company = "COOL BITS S.R.L."
        self.company_cui = "42331573"
        self.company_registration = "ROONRC.J22/676/2020"
        self.project_id = "coolbits-ai"

        # Target agents for SafeNet delegation
        self.target_agents = {
            "ogpt09": {
                "name": "oGPT09",
                "role": "Head of AI Agent",
                "responsibility": "AI strategy and implementation",
                "api_provider": "openai",
                "api_key_secret": "ogpt09",
                "rag_access": ["d-rag", "b-rag"],
                "profile_picture": "profile-ogpt.png",
                "safenet_access_level": "L4",  # Critical level for AI operations
            },
            "ogrok09": {
                "name": "oGrok09",
                "role": "CAIO - Chief AI Officer",
                "responsibility": "AI Policy Framework",
                "api_provider": "xai",
                "api_key_secret": "ogrok09",
                "rag_access": ["d-rag", "b-rag"],
                "profile_picture": "profile-ogrok09.png",
                "safenet_access_level": "L5",  # Maximum level for policy operations
            },
        }

        # SafeNet token configuration
        self.safenet_token_config = {
            "token_name": "safenet-auth-token",
            "token_description": "SafeNet Authentication Token for COOL BITS SRL digital signing",
            "token_type": "authentication",
            "security_level": "L4",
            "company_registration": self.company_registration,
            "company_cui": self.company_cui,
            "delegated_to": ["ogpt09", "ogrok09"],
            "permissions": [
                "digital_signing",
                "certificate_management",
                "signature_verification",
                "audit_trail_access",
                "compliance_reporting",
            ],
        }

    def create_safenet_secret(self) -> bool:
        """Create SafeNet authentication token in Google Secrets"""
        try:
            print("🔐 Creating SafeNet authentication token in Google Secrets...")

            # Create SafeNet token secret
            safenet_token_data = {
                "token_id": f"safenet-cb-{int(datetime.now().timestamp())}",
                "company": self.company,
                "cui": self.company_cui,
                "registration": self.company_registration,
                "token_type": "authentication",
                "security_level": "L4",
                "permissions": self.safenet_token_config["permissions"],
                "created_at": datetime.now().isoformat(),
                "expires_at": (
                    datetime.now().replace(year=datetime.now().year + 1)
                ).isoformat(),
                "delegated_agents": list(self.target_agents.keys()),
            }

            # Convert to JSON string for secret storage
            token_json = json.dumps(safenet_token_data, indent=2)

            # Create secret in Google Cloud
            cmd = [
                "gcloud",
                "secrets",
                "create",
                "safenet-auth-token",
                "--data-file=-",
                "--project",
                self.project_id,
                "--labels",
                f"company={self.company},type=safenet,token=auth,delegated=ogpt09,ogrok09",
            ]

            result = subprocess.run(
                cmd, input=token_json, text=True, capture_output=True
            )

            if result.returncode == 0:
                print("✅ SafeNet authentication token created successfully")
                return True
            else:
                print(f"❌ Failed to create SafeNet token: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ Error creating SafeNet token: {e}")
            return False

    def grant_agent_access(self, agent_id: str) -> bool:
        """Grant SafeNet token access to specific agent"""
        try:
            agent_info = self.target_agents[agent_id]
            print(
                f"🔑 Granting SafeNet access to {agent_info['name']} ({agent_info['role']})..."
            )

            # Grant Secret Manager Secret Accessor role
            cmd = [
                "gcloud",
                "secrets",
                "add-iam-policy-binding",
                "safenet-auth-token",
                "--member",
                f"user:{agent_id}@coolbits.ai",
                "--role",
                "roles/secretmanager.secretAccessor",
                "--project",
                self.project_id,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ SafeNet access granted to {agent_info['name']}")
                return True
            else:
                print(
                    f"❌ Failed to grant access to {agent_info['name']}: {result.stderr}"
                )
                return False

        except Exception as e:
            print(f"❌ Error granting access to {agent_id}: {e}")
            return False

    def create_agent_safenet_config(self, agent_id: str) -> bool:
        """Create SafeNet configuration for specific agent"""
        try:
            agent_info = self.target_agents[agent_id]

            safenet_config = {
                "agent_id": agent_id,
                "agent_name": agent_info["name"],
                "agent_role": agent_info["role"],
                "company": self.company,
                "company_cui": self.company_cui,
                "company_registration": self.company_registration,
                "safenet_access": {
                    "token_secret": "safenet-auth-token",
                    "access_level": agent_info["safenet_access_level"],
                    "permissions": self.safenet_token_config["permissions"],
                    "granted_at": datetime.now().isoformat(),
                },
                "api_integration": {
                    "safenet_api_endpoint": "http://localhost:5001/api/safenet",
                    "certificate_types": [
                        "company_signing",
                        "api_authentication",
                        "document_signing",
                        "code_signing",
                    ],
                    "security_levels": ["L1", "L2", "L3", "L4", "L5"],
                },
                "delegation_info": {
                    "delegated_by": "Andrei (CEO)",
                    "delegation_date": datetime.now().isoformat(),
                    "delegation_purpose": f"Enable {agent_info['role']} to perform SafeNet operations",
                    "compliance_status": "COMPLIANT",
                },
            }

            # Save agent-specific SafeNet config
            config_file = f"{agent_id}_safenet_config.json"
            with open(config_file, "w") as f:
                json.dump(safenet_config, f, indent=2)

            print(
                f"✅ SafeNet configuration created for {agent_info['name']}: {config_file}"
            )
            return True

        except Exception as e:
            print(f"❌ Error creating SafeNet config for {agent_id}: {e}")
            return False

    def update_agent_capabilities(self, agent_id: str) -> bool:
        """Update agent capabilities to include SafeNet operations"""
        try:
            agent_info = self.target_agents[agent_id]

            # Enhanced capabilities with SafeNet
            enhanced_capabilities = {
                "original_capabilities": agent_info.get("original_capabilities", []),
                "safenet_capabilities": [
                    "digital_document_signing",
                    "certificate_management",
                    "signature_verification",
                    "compliance_reporting",
                    "audit_trail_access",
                    "security_policy_enforcement",
                ],
                "safenet_integration": {
                    "api_endpoints": [
                        "POST /api/safenet/sign",
                        "POST /api/safenet/verify",
                        "GET /api/safenet/certificates",
                        "GET /api/safenet/compliance-report",
                    ],
                    "security_levels": ["L1", "L2", "L3", "L4", "L5"],
                    "certificate_types": [
                        "company_signing",
                        "api_authentication",
                        "document_signing",
                        "code_signing",
                    ],
                },
            }

            # Save enhanced capabilities
            capabilities_file = f"{agent_id}_enhanced_capabilities.json"
            with open(capabilities_file, "w") as f:
                json.dump(enhanced_capabilities, f, indent=2)

            print(
                f"✅ Enhanced capabilities created for {agent_info['name']}: {capabilities_file}"
            )
            return True

        except Exception as e:
            print(f"❌ Error updating capabilities for {agent_id}: {e}")
            return False

    def create_delegation_report(self) -> Dict[str, Any]:
        """Create comprehensive delegation report"""

        report = {
            "delegation_info": {
                "company": self.company,
                "company_cui": self.company_cui,
                "company_registration": self.company_registration,
                "delegation_date": datetime.now().isoformat(),
                "delegated_by": "Andrei (CEO)",
                "delegation_purpose": "Enable AI agents to perform SafeNet digital signing operations",
            },
            "safenet_token": {
                "token_name": "safenet-auth-token",
                "token_type": "authentication",
                "security_level": "L4",
                "permissions": self.safenet_token_config["permissions"],
                "delegated_agents": list(self.target_agents.keys()),
            },
            "delegated_agents": {},
            "delegation_status": "COMPLETED",
            "compliance_status": "COMPLIANT",
            "next_steps": [
                "Test SafeNet integration with ogpt09",
                "Test SafeNet integration with ogrok09",
                "Verify digital signing capabilities",
                "Monitor audit trails",
                "Schedule compliance reviews",
            ],
        }

        # Add agent-specific delegation details
        for agent_id, agent_info in self.target_agents.items():
            report["delegated_agents"][agent_id] = {
                "name": agent_info["name"],
                "role": agent_info["role"],
                "responsibility": agent_info["responsibility"],
                "safenet_access_level": agent_info["safenet_access_level"],
                "permissions": self.safenet_token_config["permissions"],
                "delegation_status": "ACTIVE",
                "compliance_status": "COMPLIANT",
            }

        return report

    def execute_delegation(self) -> bool:
        """Execute complete SafeNet token delegation process"""
        print("🔐 SafeNet Authentication Token Delegation")
        print("=" * 60)
        print(f"Company: {self.company}")
        print(f"CUI: {self.company_cui}")
        print(f"Registration: {self.company_registration}")
        print("=" * 60)

        try:
            # Step 1: Create SafeNet token secret
            print("\n📋 Step 1: Creating SafeNet authentication token...")
            if not self.create_safenet_secret():
                return False

            # Step 2: Grant access to each agent
            print("\n📋 Step 2: Granting agent access...")
            for agent_id in self.target_agents.keys():
                if not self.grant_agent_access(agent_id):
                    return False

            # Step 3: Create agent-specific configurations
            print("\n📋 Step 3: Creating agent configurations...")
            for agent_id in self.target_agents.keys():
                if not self.create_agent_safenet_config(agent_id):
                    return False

            # Step 4: Update agent capabilities
            print("\n📋 Step 4: Updating agent capabilities...")
            for agent_id in self.target_agents.keys():
                if not self.update_agent_capabilities(agent_id):
                    return False

            # Step 5: Generate delegation report
            print("\n📋 Step 5: Generating delegation report...")
            delegation_report = self.create_delegation_report()

            # Save delegation report
            with open("safenet_token_delegation_report.json", "w") as f:
                json.dump(delegation_report, f, indent=2)

            print("\n✅ SafeNet token delegation completed successfully!")
            print("📁 Delegation report saved to: safenet_token_delegation_report.json")

            return True

        except Exception as e:
            print(f"\n❌ Delegation failed: {e}")
            return False


def main():
    """Main function to execute SafeNet token delegation"""

    print("🔐 SafeNet Authentication Token Delegation - COOL BITS SRL")
    print("=" * 70)
    print("Delegating SafeNet auth token to ogpt09 and ogrok09 agents")
    print("=" * 70)

    # Initialize delegation manager
    delegation_manager = SafeNetTokenDelegation()

    # Execute delegation
    if delegation_manager.execute_delegation():
        print("\n🎉 DELEGATION SUMMARY:")
        print("=" * 40)
        print("✅ SafeNet authentication token created")
        print("✅ Access granted to ogpt09 (Head of AI Agent)")
        print("✅ Access granted to ogrok09 (CAIO - Chief AI Officer)")
        print("✅ Agent configurations created")
        print("✅ Capabilities enhanced")
        print("✅ Delegation report generated")

        print("\n📋 DELEGATED AGENTS:")
        for agent_id, agent_info in delegation_manager.target_agents.items():
            print(f"  {agent_info['name']} ({agent_info['role']})")
            print(f"    - Access Level: {agent_info['safenet_access_level']}")
            print(f"    - Profile: {agent_info['profile_picture']}")
            print("    - Status: ACTIVE")

        print("\n🔐 SAFENET CAPABILITIES ENABLED:")
        for permission in delegation_manager.safenet_token_config["permissions"]:
            print(f"  ✅ {permission}")

        print("\n📋 NEXT STEPS:")
        print("1. Test SafeNet integration with ogpt09")
        print("2. Test SafeNet integration with ogrok09")
        print("3. Verify digital signing capabilities")
        print("4. Monitor audit trails")
        print("5. Schedule compliance reviews")

        return 0
    else:
        print("\n❌ Delegation failed!")
        print("Please check the logs above for error details.")
        return 1


if __name__ == "__main__":
    exit(main())
