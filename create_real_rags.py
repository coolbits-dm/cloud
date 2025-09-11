#!/usr/bin/env python3
"""
Create real RAG infrastructure for all industries using Vertex AI Search (Discovery Engine)
This creates actual Search Apps, Data Stores, and Cloud Storage buckets
"""

import os
import json
import time
from typing import Dict, List, Optional
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.cloud import storage
from google.cloud import secretmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealIndustryRAGManager:
    """Creates real RAG infrastructure using Vertex AI Search"""

    def __init__(self, project_id: str, location: str = "global"):
        self.project_id = project_id
        self.location = location

        # Use default credentials (gcloud auth)
        self.storage_client = storage.Client(project=project_id)
        self.secret_client = secretmanager.SecretManagerServiceClient()

        # Initialize Discovery Engine client
        self.discovery_client = discoveryengine.DataStoreServiceClient()

        # Industry definitions (same as before)
        self.industries = {
            "agritech": {
                "name": "AgTech",
                "description": "Agricultural Technology and Innovation",
                "keywords": [
                    "agriculture",
                    "farming",
                    "crop",
                    "livestock",
                    "precision agriculture",
                    "IoT sensors",
                ],
                "documents": [
                    "agricultural_tech_guide.pdf",
                    "precision_farming_whitepaper.pdf",
                ],
            },
            "banking": {
                "name": "Banking",
                "description": "Commercial and Retail Banking Services",
                "keywords": [
                    "banking",
                    "banks",
                    "financial services",
                    "commercial banking",
                ],
                "documents": ["banking.pdf", "financial_services.pdf"],
            },
            "saas_b2b": {
                "name": "SaaS B2B",
                "description": "Business-to-Business Software as a Service",
                "keywords": ["SaaS", "B2B", "software", "business software"],
                "documents": ["saas_b2b.pdf", "business_software.pdf"],
            },
            "healthcare": {
                "name": "Healthcare",
                "description": "Healthcare Services and Medical Technology",
                "keywords": ["healthcare", "medical", "health", "medicine"],
                "documents": ["healthcare.pdf", "medical_technology.pdf"],
            },
            "exchanges": {
                "name": "Cryptocurrency Exchanges",
                "description": "Cryptocurrency Trading Platforms and Exchanges",
                "keywords": [
                    "cryptocurrency",
                    "exchanges",
                    "trading",
                    "crypto trading",
                ],
                "documents": ["crypto_exchanges.pdf", "cryptocurrency.pdf"],
            },
        }

    def create_cloud_storage_bucket(self, industry_id: str) -> str:
        """Use existing Cloud Storage bucket for industry documents"""
        bucket_name = f"coolbits-rag-{industry_id}-{self.project_id}"

        try:
            # Check if bucket exists
            bucket = self.storage_client.bucket(bucket_name)
            bucket.reload()
            logger.info(f"Using existing bucket: {bucket_name}")
            return bucket_name

        except Exception as e:
            logger.error(f"Bucket {bucket_name} does not exist: {e}")
            return None

    def upload_sample_documents(self, industry_id: str, bucket_name: str) -> bool:
        """Upload sample documents to Cloud Storage bucket"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            industry_info = self.industries[industry_id]

            # Create sample document
            sample_content = f"""# {industry_info['name']} Industry Documentation

## Industry Overview
{industry_info['description']}

## Key Topics
{', '.join(industry_info['keywords'])}

## Sample Content
This is a sample document for the {industry_info['name']} industry RAG system.
It contains placeholder content that should be replaced with actual industry-specific documentation.

## Industry-Specific Information
- Market trends and analysis
- Best practices and guidelines
- Regulatory requirements
- Technology solutions
- Case studies and examples

Generated for CoolBits.ai RAG system on {time.strftime('%Y-%m-%d %H:%M:%S')}
"""

            # Upload sample document
            blob_name = f"sample_{industry_id}_document.txt"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(sample_content)

            logger.info(f"Uploaded sample document: {blob_name}")
            return True

        except Exception as e:
            logger.error(f"Error uploading documents for {industry_id}: {e}")
            return False

    def create_data_store(self, industry_id: str, bucket_name: str) -> str:
        """Create Discovery Engine Data Store"""
        try:
            industry_info = self.industries[industry_id]

            # Data Store configuration
            data_store = discoveryengine.DataStore(
                display_name=f"{industry_info['name']} RAG Data Store",
                industry_vertical=discoveryengine.IndustryVertical.GENERIC,
                content_config=discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED,
                solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
            )

            # Create Data Store
            parent = f"projects/{self.project_id}/locations/{self.location}"
            request = discoveryengine.CreateDataStoreRequest(
                parent=parent,
                data_store=data_store,
                data_store_id=f"{industry_id}-rag-store",
            )

            operation = self.discovery_client.create_data_store(request=request)
            logger.info(f"Creating Data Store for {industry_id}...")

            # Wait for operation to complete
            result = operation.result(timeout=300)  # 5 minutes timeout
            data_store_name = result.name

            logger.info(f"Created Data Store: {data_store_name}")
            return data_store_name

        except Exception as e:
            logger.error(f"Error creating Data Store for {industry_id}: {e}")
            return None

    def create_search_app(self, industry_id: str, data_store_name: str) -> str:
        """Create Discovery Engine Search App"""
        try:
            industry_info = self.industries[industry_id]

            # Search App configuration
            search_app = discoveryengine.SearchApp(
                display_name=f"{industry_info['name']} Search App",
                data_store_ids=[
                    data_store_name.split("/")[-1]
                ],  # Extract data store ID
            )

            # Create Search App
            parent = f"projects/{self.project_id}/locations/{self.location}"
            request = discoveryengine.CreateSearchAppRequest(
                parent=parent,
                search_app=search_app,
                search_app_id=f"{industry_id}-search-app",
            )

            operation = self.discovery_client.create_search_app(request=request)
            logger.info(f"Creating Search App for {industry_id}...")

            # Wait for operation to complete
            result = operation.result(timeout=300)  # 5 minutes timeout
            search_app_name = result.name

            logger.info(f"Created Search App: {search_app_name}")
            return search_app_name

        except Exception as e:
            logger.error(f"Error creating Search App for {industry_id}: {e}")
            return None

    def setup_industry_rag(self, industry_id: str) -> Dict[str, str]:
        """Set up complete RAG infrastructure for an industry"""
        logger.info(f"Setting up RAG for industry: {industry_id}")

        result = {
            "industry_id": industry_id,
            "bucket_name": None,
            "data_store_name": None,
            "search_app_name": None,
            "success": False,
        }

        try:
            # 1. Create Cloud Storage bucket
            bucket_name = self.create_cloud_storage_bucket(industry_id)
            if not bucket_name:
                return result
            result["bucket_name"] = bucket_name

            # 2. Upload sample documents
            if not self.upload_sample_documents(industry_id, bucket_name):
                return result

            # 3. Create Data Store
            data_store_name = self.create_data_store(industry_id, bucket_name)
            if not data_store_name:
                return result
            result["data_store_name"] = data_store_name

            # 4. Create Search App
            search_app_name = self.create_search_app(industry_id, data_store_name)
            if not search_app_name:
                return result
            result["search_app_name"] = search_app_name

            result["success"] = True
            logger.info(f"Successfully set up RAG for {industry_id}")

        except Exception as e:
            logger.error(f"Error setting up RAG for {industry_id}: {e}")

        return result

    def setup_all_industries(self) -> Dict[str, Dict]:
        """Set up RAG infrastructure for all industries"""
        logger.info("Starting RAG setup for all industries...")

        results = {}
        successful = 0
        total = len(self.industries)

        for industry_id in self.industries.keys():
            logger.info(f"Processing industry {industry_id} ({successful + 1}/{total})")

            result = self.setup_industry_rag(industry_id)
            results[industry_id] = result

            if result["success"]:
                successful += 1

            # Add delay between requests to avoid rate limiting
            time.sleep(2)

        logger.info(f"RAG setup complete: {successful}/{total} industries configured")
        return results


def main():
    """Main function to set up RAG infrastructure"""
    # Configuration
    PROJECT_ID = "coolbits-ai"
    LOCATION = "us-central1"  # Use specific region for better compatibility

    print("🚀 Setting up real RAG infrastructure for industries...")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}")

    # Initialize RAG manager
    rag_manager = RealIndustryRAGManager(project_id=PROJECT_ID, location=LOCATION)

    # Set up all industries
    results = rag_manager.setup_all_industries()

    # Print summary
    successful = sum(1 for result in results.values() if result["success"])
    total = len(results)

    print(f"\n📊 RAG Setup Summary:")
    print(f"✅ Successful: {successful}/{total}")
    print(f"❌ Failed: {total - successful}/{total}")

    if successful > 0:
        print(
            f"\n🎉 Successfully created RAG infrastructure for {successful} industries!"
        )
        print("\nCreated resources:")
        for industry_id, result in results.items():
            if result["success"]:
                print(f"  📁 {industry_id}:")
                print(f"    - Bucket: {result['bucket_name']}")
                print(f"    - Data Store: {result['data_store_name']}")
                print(f"    - Search App: {result['search_app_name']}")

    # Save results to file
    with open("rag_setup_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: rag_setup_results.json")


if __name__ == "__main__":
    main()
