# CoolBits.ai @oPipe - Non-Human Agents (NHA) Registry
# Official centralized registry for all NHA agents in the CoolBits ecosystem
# Internal use only - not for public distribution

import json
import logging
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess


@dataclass
class NHAAgent:
    """Non-Human Agent definition"""

    name: str
    category: str
    description: str
    responsible_bot: str
    status: str  # active, inactive, development, deprecated
    gcloud_project: Optional[str] = None
    service_account: Optional[str] = None
    permissions: List[str] = None
    last_updated: str = None
    version: str = "1.0"

    def __post_init__(self):
        if self.permissions is None:
            self.permissions = []
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()


class NHARegistry:
    """Centralized registry for all Non-Human Agents"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents: Dict[str, NHAAgent] = {}
        self.setup_logging()
        self.load_agents()

    def setup_logging(self):
        """Setup logging for NHA registry"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/nha_registry.log"),
                logging.StreamHandler(),
            ],
        )

    def load_agents(self):
        """Load all NHA agents into registry"""
        try:
            # Personal Agents
            self._register_personal_agents()

            # Business Channel Agents
            self._register_business_channel_agents()

            # Business Tool Agents
            self._register_business_tool_agents()

            # Development Tool Agents
            self._register_dev_tool_agents()

            # SEO Tool Agents
            self._register_seo_tool_agents()

            # Agency/MCC Agents
            self._register_agency_agents()

            self.logger.info(f"Loaded {len(self.agents)} NHA agents into registry")

        except Exception as e:
            self.logger.error(f"Failed to load agents: {e}")

    def _register_personal_agents(self):
        """Register personal communication agents"""
        personal_agents = [
            NHAAgent(
                name="oAndy",
                category="personal_agent",
                description="Personal assistant agent for general tasks",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oKim",
                category="personal_agent",
                description="Personal communication agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oPersonal",
                category="personal_tools",
                description="Responsible bot for personal tools management",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                ],
            ),
            NHAAgent(
                name="oFacebook",
                category="personal_tools",
                description="Facebook integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oTelegram",
                category="personal_tools",
                description="Telegram bot integration",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oTikTok",
                category="personal_tools",
                description="TikTok integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oLinkedIn",
                category="personal_tools",
                description="LinkedIn integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oX",
                category="personal_tools",
                description="X (Twitter) integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oReddit",
                category="personal_tools",
                description="Reddit integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oGmail",
                category="personal_tools",
                description="Gmail integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "gmail.readonly",
                ],
            ),
            NHAAgent(
                name="oDocs",
                category="personal_tools",
                description="Google Docs integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "docs.readonly",
                ],
            ),
            NHAAgent(
                name="oSheets",
                category="personal_tools",
                description="Google Sheets integration agent",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "sheets.readonly",
                ],
            ),
            NHAAgent(
                name="oDiscord",
                category="personal_tools",
                description="Discord bot integration",
                responsible_bot="oPersonal",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
        ]

        for agent in personal_agents:
            self.agents[agent.name] = agent

    def _register_business_channel_agents(self):
        """Register business channel agents"""
        business_channel_agents = [
            NHAAgent(
                name="oBusinessChannels",
                category="business_channels",
                description="Responsible bot for business channel management",
                responsible_bot="oBusinessChannels",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                ],
            ),
            NHAAgent(
                name="oGoogleAds",
                category="business_channels",
                description="Google Ads integration agent",
                responsible_bot="oBusinessChannels",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "ads.readonly",
                ],
            ),
            NHAAgent(
                name="oMetaAds",
                category="business_channels",
                description="Meta (Facebook) Ads integration agent",
                responsible_bot="oBusinessChannels",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oTikTokAds",
                category="business_channels",
                description="TikTok Ads integration agent",
                responsible_bot="oBusinessChannels",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oLinkedInAds",
                category="business_channels",
                description="LinkedIn Ads integration agent",
                responsible_bot="oBusinessChannels",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
        ]

        for agent in business_channel_agents:
            self.agents[agent.name] = agent

    def _register_business_tool_agents(self):
        """Register business tool agents"""
        business_tool_agents = [
            NHAAgent(
                name="oBusinessTools",
                category="business_tools",
                description="Responsible bot for business tools management",
                responsible_bot="oBusinessTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                ],
            ),
            NHAAgent(
                name="oGA4",
                category="business_tools",
                description="Google Analytics 4 integration agent",
                responsible_bot="oBusinessTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "analytics.readonly",
                ],
            ),
            NHAAgent(
                name="oGTM",
                category="business_tools",
                description="Google Tag Manager integration agent",
                responsible_bot="oBusinessTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "tagmanager.readonly",
                ],
            ),
            NHAAgent(
                name="oGSC",
                category="business_tools",
                description="Google Search Console integration agent",
                responsible_bot="oBusinessTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "webmasters.readonly",
                ],
            ),
            NHAAgent(
                name="oGBP",
                category="business_tools",
                description="Google Business Profile integration agent",
                responsible_bot="oBusinessTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "businessprofile.readonly",
                ],
            ),
            NHAAgent(
                name="oCGS",
                category="business_tools",
                description="Google Cloud Storage integration agent",
                responsible_bot="oBusinessTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "storage.objectViewer",
                ],
            ),
        ]

        for agent in business_tool_agents:
            self.agents[agent.name] = agent

    def _register_seo_tool_agents(self):
        """Register SEO tool agents"""
        seo_tool_agents = [
            NHAAgent(
                name="oSEOTools",
                category="seo_tools",
                description="Responsible bot for SEO tools management",
                responsible_bot="oSEOTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                ],
            ),
            NHAAgent(
                name="oSEMrush",
                category="seo_tools",
                description="SEMrush integration agent",
                responsible_bot="oSEOTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oAhrefs",
                category="seo_tools",
                description="Ahrefs integration agent",
                responsible_bot="oSEOTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oMoz",
                category="seo_tools",
                description="Moz integration agent",
                responsible_bot="oSEOTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oScreamingFrog",
                category="seo_tools",
                description="Screaming Frog integration agent",
                responsible_bot="oSEOTools",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
        ]

        for agent in seo_tool_agents:
            self.agents[agent.name] = agent

    def _register_agency_agents(self):
        """Register agency/MCC agents"""
        agency_agents = [
            NHAAgent(
                name="oAgencyMCC",
                category="agency_mcc",
                description="Responsible bot for agency MCC management",
                responsible_bot="oAgencyMCC",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                ],
            ),
            NHAAgent(
                name="oGoogleAdsMCC",
                category="agency_mcc",
                description="Google Ads MCC integration agent",
                responsible_bot="oAgencyMCC",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "ads.readonly",
                ],
            ),
            NHAAgent(
                name="oMetaAdsMCC",
                category="agency_mcc",
                description="Meta Ads Manager integration agent",
                responsible_bot="oAgencyMCC",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oLinkedInMCC",
                category="agency_mcc",
                description="LinkedIn Campaign Manager integration agent",
                responsible_bot="oAgencyMCC",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
        ]

        for agent in agency_agents:
            self.agents[agent.name] = agent

    def _register_dev_tool_agents(self):
        """Register development tool agents"""
        dev_tool_agents = [
            NHAAgent(
                name="oDev",
                category="dev_tools",
                description="Responsible bot for development tools management",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                    "cloudbuild.builds.create",
                ],
            ),
            NHAAgent(
                name="oCursor",
                category="dev_tools",
                description="Cursor IDE integration agent",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oGit",
                category="dev_tools",
                description="Git integration agent",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "source.repos.read",
                ],
            ),
            NHAAgent(
                name="oDocker",
                category="dev_tools",
                description="Docker integration agent",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                ],
            ),
            NHAAgent(
                name="oTerminal",
                category="dev_tools",
                description="Terminal integration agent",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=["storage.objectViewer", "logging.logWriter"],
            ),
            NHAAgent(
                name="oCloudBuild",
                category="dev_tools",
                description="Google Cloud Build integration agent",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "cloudbuild.builds.create",
                ],
            ),
            NHAAgent(
                name="oCloudRun",
                category="dev_tools",
                description="Google Cloud Run integration agent",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "run.invoker",
                ],
            ),
            NHAAgent(
                name="oVertexAI",
                category="dev_tools",
                description="Google Vertex AI integration agent",
                responsible_bot="oDev",
                status="active",
                gcloud_project="coolbits-ai",
                permissions=[
                    "storage.objectViewer",
                    "logging.logWriter",
                    "aiplatform.endpoints.predict",
                ],
            ),
        ]

        for agent in dev_tool_agents:
            self.agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[NHAAgent]:
        """Get agent by name"""
        return self.agents.get(name)

    def get_agents_by_category(self, category: str) -> List[NHAAgent]:
        """Get all agents in a category"""
        return [agent for agent in self.agents.values() if agent.category == category]

    def get_active_agents(self) -> List[NHAAgent]:
        """Get all active agents"""
        return [agent for agent in self.agents.values() if agent.status == "active"]

    def update_agent(self, name: str, **kwargs) -> bool:
        """Update agent properties"""
        try:
            if name not in self.agents:
                self.logger.error(f"Agent {name} not found")
                return False

            agent = self.agents[name]
            for key, value in kwargs.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)

            agent.last_updated = datetime.now().isoformat()
            self.logger.info(f"Updated agent {name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to update agent {name}: {e}")
            return False

    def export_registry(self, filename: str = "nha_registry.json") -> bool:
        """Export registry to JSON file"""
        try:
            registry_data = {
                "timestamp": datetime.now().isoformat(),
                "total_agents": len(self.agents),
                "agents": {name: asdict(agent) for name, agent in self.agents.items()},
            }

            os.makedirs("data/nha", exist_ok=True)
            with open(f"data/nha/{filename}", "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Exported registry to data/nha/{filename}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export registry: {e}")
            return False

    def sync_with_gcloud(self) -> bool:
        """Sync agent permissions with Google Cloud IAM"""
        try:
            self.logger.info("Syncing NHA registry with Google Cloud IAM")

            for agent_name, agent in self.agents.items():
                if agent.gcloud_project and agent.service_account:
                    self._sync_agent_permissions(agent)

            self.logger.info("Successfully synced NHA registry with Google Cloud")
            return True

        except Exception as e:
            self.logger.error(f"Failed to sync with Google Cloud: {e}")
            return False

    def _sync_agent_permissions(self, agent: NHAAgent):
        """Sync individual agent permissions with Google Cloud"""
        try:
            if not agent.service_account:
                # Create service account if it doesn't exist
                service_account_email = f"{agent.name.lower()}@{agent.gcloud_project}.iam.gserviceaccount.com"

                cmd = [
                    "gcloud",
                    "iam",
                    "service-accounts",
                    "create",
                    agent.name.lower(),
                    "--project",
                    agent.gcloud_project,
                    "--display-name",
                    f"NHA Agent: {agent.name}",
                    "--description",
                    agent.description,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    self.logger.warning(
                        f"Service account {agent.name} may already exist"
                    )

                agent.service_account = service_account_email

            # Apply IAM permissions
            for permission in agent.permissions:
                cmd = [
                    "gcloud",
                    "projects",
                    "add-iam-policy-binding",
                    agent.gcloud_project,
                    "--member",
                    f"serviceAccount:{agent.service_account}",
                    "--role",
                    permission,
                ]

                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0:
                    self.logger.info(f"Applied permission {permission} to {agent.name}")
                else:
                    self.logger.warning(
                        f"Failed to apply permission {permission} to {agent.name}"
                    )

        except Exception as e:
            self.logger.error(f"Failed to sync permissions for {agent.name}: {e}")

    def generate_report(self) -> str:
        """Generate NHA registry report"""
        try:
            report = f"""# CoolBits.ai @oPipe NHA Registry Report

Generated: {datetime.now().isoformat()}

## Summary
- **Total Agents**: {len(self.agents)}
- **Active Agents**: {len(self.get_active_agents())}
- **Categories**: {len(set(agent.category for agent in self.agents.values()))}

## Agent Categories

"""

            categories = {}
            for agent in self.agents.values():
                if agent.category not in categories:
                    categories[agent.category] = []
                categories[agent.category].append(agent)

            for category, agents in categories.items():
                report += f"### {category.replace('_', ' ').title()}\n"
                report += f"**Count**: {len(agents)}\n\n"

                for agent in agents:
                    report += f"- **{agent.name}**: {agent.description}\n"
                    report += f"  - Status: {agent.status}\n"
                    report += f"  - Responsible Bot: {agent.responsible_bot}\n"
                    report += f"  - GCloud Project: {agent.gcloud_project or 'N/A'}\n"
                    report += f"  - Permissions: {', '.join(agent.permissions) if agent.permissions else 'None'}\n\n"

            return report

        except Exception as e:
            self.logger.error(f"Failed to generate report: {e}")
            return f"# NHA Registry Report\n\nError generating report: {e}"


def main():
    """Main function for NHA registry management"""
    try:
        # Initialize registry
        registry = NHARegistry()

        # Export registry
        registry.export_registry()

        # Generate report
        report = registry.generate_report()

        # Save report
        os.makedirs("reports", exist_ok=True)
        with open("reports/nha_registry_report.md", "w", encoding="utf-8") as f:
            f.write(report)

        print("NHA Registry initialized successfully!")
        print(f"Total agents: {len(registry.agents)}")
        print("Report saved to: reports/nha_registry_report.md")

        return registry

    except Exception as e:
        print(f"Failed to initialize NHA registry: {e}")
        return None


if __name__ == "__main__":
    main()
