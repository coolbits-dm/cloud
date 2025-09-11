#!/usr/bin/env python3
"""
Automated RAG Corpus Creation Script for CoolBits.ai
Creates all 88 RAG corpora using Vertex AI SDK

Requirements:
pip install google-cloud-discoveryengine google-cloud-storage
"""

import json
import time
import logging
from typing import Dict, Optional
from dataclasses import dataclass

from google.cloud import discoveryengine_v1beta as discoveryengine
from google.cloud import storage
from google.api_core import exceptions as gcp_exceptions

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """Configuration for RAG creation"""

    project_id: str = "coolbits-ai"
    location: str = "global"  # Discovery Engine uses 'global' location
    region: str = "europe-west1"  # For Cloud Storage buckets
    bucket_prefix: str = "coolbits-rag"


class RAGCorpusCreator:
    """Creates RAG corpora using Vertex AI Discovery Engine SDK"""

    def __init__(self, config: RAGConfig):
        self.config = config
        self.discovery_client = discoveryengine.DataStoreServiceClient()
        self.storage_client = storage.Client(project=config.project_id)

        # Base paths
        self.project_path = f"projects/{config.project_id}"
        self.location_path = f"{self.project_path}/locations/{config.location}"

        logger.info(f"Initialized RAG Creator for project: {config.project_id}")

    def create_data_store(
        self, rag_id: str, rag_name: str, rag_description: str
    ) -> Optional[str]:
        """Create a data store (corpus) for RAG"""
        data_store_name = f"{rag_id}-corpus"

        logger.info(f"Creating data store: {data_store_name}")

        # Check if data store already exists
        try:
            existing_stores = self.discovery_client.list_data_stores(
                parent=self.location_path, filter=f'displayName="{data_store_name}"'
            )

            for store in existing_stores:
                if store.display_name == data_store_name:
                    logger.warning(
                        f"Data store {data_store_name} already exists, skipping..."
                    )
                    return store.name
        except Exception as e:
            logger.debug(f"Error checking existing stores: {e}")

        # Create data store
        data_store = discoveryengine.DataStore(
            display_name=data_store_name,
            industry_vertical=discoveryengine.IndustryVertical.GENERIC,
            solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
        )

        try:
            operation = self.discovery_client.create_data_store(
                parent=self.location_path,
                data_store=data_store,
                data_store_id=data_store_name.replace(
                    "-", "_"
                ),  # Data store ID cannot contain hyphens
            )

            # Wait for operation to complete
            logger.info("Waiting for data store creation to complete...")
            result = operation.result(timeout=300)  # 5 minutes timeout

            logger.success(f"Created data store: {data_store_name} (ID: {result.name})")
            return result.name

        except gcp_exceptions.AlreadyExists:
            logger.warning(f"Data store {data_store_name} already exists")
            return (
                f"{self.location_path}/dataStores/{data_store_name.replace('-', '_')}"
            )
        except Exception as e:
            logger.error(f"Failed to create data store {data_store_name}: {e}")
            return None

    def create_gcs_connector(self, data_store_name: str, rag_id: str) -> bool:
        """Create GCS connector for data store"""
        bucket_name = f"{self.config.bucket_prefix}-{rag_id}-{self.config.project_id}"
        connector_name = f"{rag_id}-gcs-connector"

        logger.info(f"Creating GCS connector for bucket: {bucket_name}")

        # Check if connector already exists
        try:
            existing_connectors = self.discovery_client.list_connectors(
                parent=data_store_name
            )

            for connector in existing_connectors:
                if connector.display_name == connector_name:
                    logger.warning(
                        f"Connector {connector_name} already exists, skipping..."
                    )
                    return True
        except Exception as e:
            logger.debug(f"Error checking existing connectors: {e}")

        # Create GCS connector
        connector = discoveryengine.Connector(
            display_name=connector_name,
            gcs_source=discoveryengine.GcsSource(
                input_uris=[f"gs://{bucket_name}/*"],
                data_schema="content",
            ),
        )

        try:
            operation = self.discovery_client.create_connector(
                parent=data_store_name,
                connector=connector,
                connector_id=connector_name.replace("-", "_"),
            )

            # Wait for operation to complete
            logger.info("Waiting for connector creation to complete...")
            result = operation.result(timeout=300)

            logger.success(f"Created GCS connector: {connector_name}")
            return True

        except gcp_exceptions.AlreadyExists:
            logger.warning(f"Connector {connector_name} already exists")
            return True
        except Exception as e:
            logger.error(f"Failed to create connector {connector_name}: {e}")
            return False

    def create_search_app(
        self, data_store_name: str, rag_id: str, rag_name: str
    ) -> Optional[str]:
        """Create search app for data store"""
        search_app_name = f"{rag_id}-search-app"

        logger.info(f"Creating search app: {search_app_name}")

        # Check if search app already exists
        try:
            existing_apps = self.discovery_client.list_engines(
                parent=self.location_path, filter=f'displayName="{search_app_name}"'
            )

            for app in existing_apps:
                if app.display_name == search_app_name:
                    logger.warning(
                        f"Search app {search_app_name} already exists, skipping..."
                    )
                    return app.name
        except Exception as e:
            logger.debug(f"Error checking existing search apps: {e}")

        # Create search app
        search_app = discoveryengine.Engine(
            display_name=search_app_name,
            solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
            search_engine_config=discoveryengine.Engine.SearchEngineConfig(
                search_tier=discoveryengine.SearchTier.SEARCH_TIER_STANDARD,
                search_add_ons=[discoveryengine.SearchAddOn.SEARCH_ADD_ON_LLM],
            ),
        )

        try:
            operation = self.discovery_client.create_engine(
                parent=self.location_path,
                engine=search_app,
                engine_id=search_app_name.replace("-", "_"),
            )

            # Wait for operation to complete
            logger.info("Waiting for search app creation to complete...")
            result = operation.result(timeout=300)

            logger.success(f"Created search app: {search_app_name} (ID: {result.name})")
            return result.name

        except gcp_exceptions.AlreadyExists:
            logger.warning(f"Search app {search_app_name} already exists")
            return f"{self.location_path}/engines/{search_app_name.replace('-', '_')}"
        except Exception as e:
            logger.error(f"Failed to create search app {search_app_name}: {e}")
            return None

    def create_rag_complete(
        self, rag_id: str, rag_name: str, rag_description: str
    ) -> Dict:
        """Create complete RAG infrastructure for a single entity"""
        result = {
            "rag_id": rag_id,
            "rag_name": rag_name,
            "data_store_name": None,
            "search_app_name": None,
            "success": False,
            "error": None,
        }

        try:
            # Step 1: Create data store
            data_store_name = self.create_data_store(rag_id, rag_name, rag_description)
            if not data_store_name:
                result["error"] = "Failed to create data store"
                return result

            result["data_store_name"] = data_store_name

            # Step 2: Create GCS connector
            if not self.create_gcs_connector(data_store_name, rag_id):
                result["error"] = "Failed to create GCS connector"
                return result

            # Step 3: Create search app
            search_app_name = self.create_search_app(data_store_name, rag_id, rag_name)
            if not search_app_name:
                result["error"] = "Failed to create search app"
                return result

            result["search_app_name"] = search_app_name
            result["success"] = True

            logger.success(f"✅ Successfully created RAG for {rag_name} ({rag_id})")

        except Exception as e:
            result["error"] = str(e)
            logger.error(f"❌ Failed to create RAG for {rag_name} ({rag_id}): {e}")

        return result


def main():
    """Main execution function"""
    config = RAGConfig()
    creator = RAGCorpusCreator(config)

    logger.info("🚀 Starting RAG corpus creation for CoolBits.ai...")
    logger.info(f"Project: {config.project_id}")
    logger.info(f"Location: {config.location}")
    logger.info("Total RAGs to create: 88")

    # Define all RAGs to create
    all_rags = [
        # Phase 1: High Priority RAGs
        ("ai_board", "AI Board", "AI Board management and coordination"),
        (
            "business",
            "Business AI Council",
            "Business AI Council for strategic decisions",
        ),
        ("agritech", "AgTech", "Agricultural Technology and Innovation"),
        ("banking", "Banking", "Commercial and Retail Banking Services"),
        ("saas_b2b", "SaaS B2B", "Business-to-Business Software as a Service"),
        # Phase 2: Medium Priority RAGs
        ("healthcare", "Healthcare", "Healthcare Services and Medical Technology"),
        ("exchanges", "Exchanges", "Cryptocurrency Exchanges"),
        ("user", "User", "Personal AI Assistant for users"),
        ("agency", "Agency", "Agency Management AI"),
        ("dev", "Dev", "Developer Tools AI"),
        # Phase 3: All remaining Industry RAGs
        ("agri_inputs", "Agri Inputs", "Agricultural Inputs and Supplies"),
        ("aftermarket_service", "Aftermarket Service", "Aftermarket Services"),
        (
            "capital_markets",
            "Capital Markets",
            "Capital Markets and Investment Banking",
        ),
        ("payments_fintech", "Payments FinTech", "Payments and Financial Technology"),
        ("wealth_asset", "Wealth Asset", "Wealth and Asset Management"),
        ("insurtech", "InsurTech", "Insurance Technology"),
        ("defi", "DeFi", "Decentralized Finance"),
        ("ai_ml_platforms", "AI ML Platforms", "AI and Machine Learning Platforms"),
        ("devtools_cloud", "DevTools Cloud", "Developer Tools and Cloud Services"),
        ("data_infra", "Data Infrastructure", "Data Infrastructure and Analytics"),
        ("identity_access", "Identity Access", "Identity and Access Management"),
        ("threat_intel", "Threat Intelligence", "Threat Intelligence and Security"),
        ("mssp", "MSSP", "Managed Security Service Providers"),
        ("physical_security", "Physical Security", "Physical Security Solutions"),
        ("digital_health", "Digital Health", "Digital Health Solutions"),
        ("hospitals_clinics", "Hospitals Clinics", "Hospitals and Clinics"),
        ("med_devices", "Medical Devices", "Medical Devices"),
        ("pharma_branded", "Pharma Branded", "Branded Pharmaceuticals"),
        ("generics", "Generics", "Generic Pharmaceuticals"),
        ("biotech_cro_cdmo", "Biotech CRO CDMO", "Biotechnology and Contract Research"),
        ("electronics_mfg", "Electronics Manufacturing", "Electronics Manufacturing"),
        ("automation_robotics", "Automation Robotics", "Automation and Robotics"),
        ("industrial_equipment", "Industrial Equipment", "Industrial Equipment"),
        ("auto_oem", "Auto OEM", "Automotive Original Equipment Manufacturers"),
        ("food_bev_mfg", "Food Bev Manufacturing", "Food and Beverage Manufacturing"),
        ("cement_glass", "Cement Glass", "Cement and Glass Manufacturing"),
        ("specialty_chem", "Specialty Chemicals", "Specialty Chemicals"),
        ("mining_metals", "Mining Metals", "Mining and Metals"),
        ("power_gen", "Power Generation", "Power Generation"),
        ("renewables", "Renewables", "Renewable Energy"),
        ("oil_gas", "Oil Gas", "Oil and Gas"),
        ("water_wastewater", "Water Wastewater", "Water and Wastewater Management"),
        ("waste_management", "Waste Management", "Waste Management"),
        ("recycling_circular", "Recycling Circular", "Recycling and Circular Economy"),
        ("carbon_esg", "Carbon ESG", "Carbon and ESG Solutions"),
        ("ev_charging", "EV Charging", "Electric Vehicle Charging"),
        ("freight_logistics", "Freight Logistics", "Freight and Logistics"),
        ("rail_logistics", "Rail Logistics", "Rail Logistics"),
        ("maritime_ports", "Maritime Ports", "Maritime and Ports"),
        ("commercial_aviation", "Commercial Aviation", "Commercial Aviation"),
        ("airlines_travel", "Airlines Travel", "Airlines and Travel"),
        (
            "otas_traveltech",
            "OTAs TravelTech",
            "Online Travel Agencies and Travel Technology",
        ),
        (
            "proptech_realestate",
            "PropTech Real Estate",
            "Property Technology and Real Estate",
        ),
        (
            "commercial_construction",
            "Commercial Construction",
            "Commercial Construction",
        ),
        (
            "residential_construction",
            "Residential Construction",
            "Residential Construction",
        ),
        ("home_improvement", "Home Improvement", "Home Improvement"),
        ("fashion_retail", "Fashion Retail", "Fashion and Retail"),
        ("grocery_retail", "Grocery Retail", "Grocery Retail"),
        ("marketplaces_d2c", "Marketplaces D2C", "Marketplaces and Direct-to-Consumer"),
        ("beauty_cosmetics", "Beauty Cosmetics", "Beauty and Cosmetics"),
        ("personal_care_fmcg", "Personal Care FMCG", "Personal Care and FMCG"),
        ("household_fmcg", "Household FMCG", "Household FMCG"),
        ("beverages_snacks", "Beverages Snacks", "Beverages and Snacks"),
        ("foodservice", "Food Service", "Food Service"),
        ("gaming_esports", "Gaming Esports", "Gaming and Esports"),
        ("streaming_ott", "Streaming OTT", "Streaming and Over-the-Top Media"),
        ("music_sports_media", "Music Sports Media", "Music, Sports, and Media"),
        ("publishing", "Publishing", "Publishing"),
        ("higher_ed", "Higher Education", "Higher Education"),
        ("k12_edtech", "K12 EdTech", "K-12 Education Technology"),
        ("consulting", "Consulting", "Consulting Services"),
        ("law_firms", "Law Firms", "Law Firms"),
        ("accounting_audit", "Accounting Audit", "Accounting and Audit"),
        ("marketing_agencies", "Marketing Agencies", "Marketing Agencies"),
        ("hr_staffing", "HR Staffing", "Human Resources and Staffing"),
        ("gov_services", "Government Services", "Government Services"),
        ("defense", "Defense", "Defense and Military"),
        ("intl_aid", "International Aid", "International Aid"),
        ("foundations", "Foundations", "Foundations"),
        ("faith_based", "Faith Based", "Faith-Based Organizations"),
        (
            "wallets_infra",
            "Wallets Infrastructure",
            "Cryptocurrency Wallets and Infrastructure",
        ),
        ("smart_home", "Smart Home", "Smart Home Technology"),
        ("fitness_wellness", "Fitness Wellness", "Fitness and Wellness"),
        ("hotels_resorts", "Hotels Resorts", "Hotels and Resorts"),
        ("clubs_leagues", "Clubs Leagues", "Clubs and Leagues"),
        ("ip_patents", "IP Patents", "Intellectual Property and Patents"),
        (
            "regtech_ediscovery",
            "RegTech E-Discovery",
            "Regulatory Technology and E-Discovery",
        ),
        ("space_newspace", "Space NewSpace", "Space and New Space Technology"),
        ("fixed_isp", "Fixed ISP", "Fixed Internet Service Providers"),
        ("mobile_operators", "Mobile Operators", "Mobile Network Operators"),
        ("network_equipment", "Network Equipment", "Network Equipment"),
        # Phase 4: Panel RAGs
        ("andrei-panel", "Andrei Panel", "RAG for Andrei Panel"),
        ("user-panel", "User Panel", "RAG for User Panel"),
        ("business-panel", "Business Panel", "RAG for Business Panel"),
        ("agency-panel", "Agency Panel", "RAG for Agency Panel"),
        ("dev-panel", "Dev Panel", "RAG for Dev Panel"),
        ("admin-panel", "Admin Panel", "RAG for Admin Panel"),
    ]

    results = []
    successful = 0
    total = len(all_rags)

    # Process RAGs in phases
    phases = [
        ("Phase 1: High Priority RAGs", all_rags[:5]),
        ("Phase 2: Medium Priority RAGs", all_rags[5:10]),
        ("Phase 3: All remaining Industry RAGs", all_rags[10:85]),
        ("Phase 4: Panel RAGs", all_rags[85:]),
    ]

    for phase_name, phase_rags in phases:
        logger.info(f"\n{phase_name}...")

        for rag_id, rag_name, rag_description in phase_rags:
            logger.info(f"\n{'=' * 50}")
            logger.info(f"Processing: {rag_name} ({rag_id})")
            logger.info(f"{'=' * 50}")

            result = creator.create_rag_complete(rag_id, rag_name, rag_description)
            results.append(result)

            if result["success"]:
                successful += 1

            # Add delay between creations to avoid rate limiting
            time.sleep(2)

    # Save results
    with open("rag_creation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Final summary
    logger.info(f"\n{'=' * 60}")
    logger.info("=== FINAL SUMMARY ===")
    logger.info(f"{'=' * 60}")
    logger.info(f"Total RAGs processed: {total}")
    logger.info(f"Successful creations: {successful}")
    logger.info(f"Failed creations: {total - successful}")

    if successful == total:
        logger.info("🎉 All RAG corpora created successfully!")
    else:
        logger.warning("⚠️  Some RAG creations failed. Check logs above.")

    logger.info("\nNext steps:")
    logger.info("1. Upload industry-specific documents to Cloud Storage buckets")
    logger.info("2. Wait for corpus indexing to complete")
    logger.info("3. Test RAG queries through API endpoints")
    logger.info("4. Integrate with Business Panel")

    logger.info("\n📄 Results saved to: rag_creation_results.json")


if __name__ == "__main__":
    main()
