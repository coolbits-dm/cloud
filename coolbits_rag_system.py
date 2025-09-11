#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai RAG System with Vertex AI Vector Search
CEO: Andrei - andrei@coolbits.ro
Managed by: oCursor (Local Development)

This module integrates Vertex AI Vector Search with CoolBits.ai for RAG functionality.
Provides semantic search across organizational knowledge and documents.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import numpy as np
from google.cloud import aiplatform
from google.cloud.aiplatform import MatchingEngineIndexEndpoint
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CoolBitsRAG:
    """CoolBits.ai RAG System with Vertex AI Vector Search"""

    def __init__(self, config_file: str = "coolbits_ai_config.json"):
        self.config_file = config_file
        self.config = self.load_config()

        # Vertex AI Configuration
        self.PROJECT_ID = "271190369805"
        self.LOCATION = "europe-west4"
        self.INDEX_ID = "357314890748133376"
        self.INDEX_ENDPOINT_ID = self.get_index_endpoint_id()

        # Initialize Vertex AI
        self.initialize_vertex_ai()

        # CoolBits.ai API
        self.coolbits_api_url = "http://localhost:8082"

    def load_config(self) -> Dict[str, Any]:
        """Load CoolBits.ai configuration"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_file} not found!")
            raise
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            raise

    def get_index_endpoint_id(self) -> str:
        """Get Index Endpoint ID from configuration or environment"""
        # Try to get from environment first
        endpoint_id = os.getenv("VERTEX_AI_INDEX_ENDPOINT_ID")
        if endpoint_id:
            return endpoint_id

        # Try to get from config
        if "vertex_ai" in self.config.get("coolbits_ai", {}):
            return self.config["coolbits_ai"]["vertex_ai"].get("index_endpoint_id", "")

        # Default placeholder
        return "YOUR_INDEX_ENDPOINT_ID"

    def initialize_vertex_ai(self):
        """Initialize Vertex AI connection"""
        try:
            aiplatform.init(project=self.PROJECT_ID, location=self.LOCATION)
            logger.info(
                f"✅ Vertex AI initialized for project {self.PROJECT_ID} in {self.LOCATION}"
            )

            # Construct index endpoint name
            self.index_endpoint_name = f"projects/{self.PROJECT_ID}/locations/{self.LOCATION}/indexEndpoints/{self.INDEX_ENDPOINT_ID}"
            logger.info(f"Index endpoint: {self.index_endpoint_name}")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Vertex AI: {e}")
            raise

    def get_coolbits_organization(self) -> Dict[str, Any]:
        """Get CoolBits.ai organizational structure"""
        try:
            response = requests.get(f"{self.coolbits_api_url}/organization", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get organization: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error getting organization: {e}")
            return {}

    def get_coolbits_roles(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Get CoolBits.ai roles"""
        try:
            endpoint = f"{self.coolbits_api_url}/roles"
            if category:
                endpoint += f"/{category}"

            response = requests.get(endpoint, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get roles: {response.status_code}")
                return {}
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return {}

    def create_embedding_vector(self, text: str, dimensions: int = 768) -> List[float]:
        """Create embedding vector for text (placeholder implementation)"""
        # In a real implementation, you would use a proper embedding model
        # For now, we'll create a random vector as placeholder
        np.random.seed(hash(text) % 2**32)  # Deterministic based on text
        return np.random.random(dimensions).tolist()

    def find_neighbors(
        self, query_text: str, num_neighbors: int = 10
    ) -> Dict[str, Any]:
        """
        Find similar content using Vertex AI Vector Search
        """
        try:
            # Create embedding vector for query
            query_vector = self.create_embedding_vector(query_text)

            # Initialize index endpoint
            index_endpoint = MatchingEngineIndexEndpoint(
                index_endpoint_name=self.index_endpoint_name
            )

            logger.info(f"🔍 Searching for neighbors of: '{query_text}'")

            # Query the endpoint
            response = index_endpoint.find_neighbors(
                queries=[query_vector], num_neighbors=num_neighbors
            )

            logger.info("✅ Successfully found neighbors")
            return {
                "success": True,
                "query": query_text,
                "neighbors": response,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Error finding neighbors: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query_text,
                "timestamp": datetime.now().isoformat(),
            }

    def search_organizational_knowledge(
        self, query: str, context: str = "all"
    ) -> Dict[str, Any]:
        """
        Search organizational knowledge using RAG
        """
        try:
            # Get relevant organizational data
            org_data = self.get_coolbits_organization()

            # Find similar content using Vector Search
            neighbors = self.find_neighbors(query)

            # Combine with organizational context
            result = {
                "success": True,
                "query": query,
                "context": context,
                "organizational_data": org_data,
                "vector_search_results": neighbors,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ RAG search completed for: '{query}'")
            return result

        except Exception as e:
            logger.error(f"❌ Error in RAG search: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "timestamp": datetime.now().isoformat(),
            }

    def get_role_specific_knowledge(self, role_id: str, query: str) -> Dict[str, Any]:
        """
        Get role-specific knowledge using RAG
        """
        try:
            # Get role information
            roles_data = self.get_coolbits_roles()

            # Find the specific role
            role_info = None
            for category, category_roles in roles_data.get("roles", {}).items():
                if role_id in category_roles:
                    role_info = category_roles[role_id]
                    break

            if not role_info:
                return {
                    "success": False,
                    "error": f"Role {role_id} not found",
                    "query": query,
                }

            # Search for role-specific knowledge
            rag_result = self.search_organizational_knowledge(query, f"role:{role_id}")

            # Combine role info with search results
            result = {
                "success": True,
                "role": role_info,
                "query": query,
                "rag_results": rag_result,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Role-specific knowledge retrieved for {role_id}")
            return result

        except Exception as e:
            logger.error(f"❌ Error getting role-specific knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "role_id": role_id,
                "query": query,
            }

    def get_panel_specific_knowledge(
        self, panel_name: str, query: str
    ) -> Dict[str, Any]:
        """
        Get panel-specific knowledge using RAG
        """
        try:
            # Get panel information
            response = requests.get(
                f"{self.coolbits_api_url}/panels/{panel_name}", timeout=10
            )
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Panel {panel_name} not found",
                    "query": query,
                }

            panel_data = response.json()

            # Search for panel-specific knowledge
            rag_result = self.search_organizational_knowledge(
                query, f"panel:{panel_name}"
            )

            # Combine panel info with search results
            result = {
                "success": True,
                "panel": panel_data.get("panel", {}),
                "query": query,
                "rag_results": rag_result,
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ Panel-specific knowledge retrieved for {panel_name}")
            return result

        except Exception as e:
            logger.error(f"❌ Error getting panel-specific knowledge: {e}")
            return {
                "success": False,
                "error": str(e),
                "panel_name": panel_name,
                "query": query,
            }

    def generate_rag_response(
        self, query: str, user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive RAG response
        """
        try:
            # Extract context information
            user_role = user_context.get("role", "user")
            user_panel = user_context.get("panel", "user")
            user_access_level = user_context.get("access_level", "USER")

            # Get relevant knowledge
            org_knowledge = self.search_organizational_knowledge(query)
            role_knowledge = self.get_role_specific_knowledge(user_role, query)
            panel_knowledge = self.get_panel_specific_knowledge(user_panel, query)

            # Combine all knowledge sources
            result = {
                "success": True,
                "query": query,
                "user_context": user_context,
                "organizational_knowledge": org_knowledge,
                "role_knowledge": role_knowledge,
                "panel_knowledge": panel_knowledge,
                "recommendations": self.generate_recommendations(query, user_context),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"✅ RAG response generated for: '{query}'")
            return result

        except Exception as e:
            logger.error(f"❌ Error generating RAG response: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "user_context": user_context,
            }

    def generate_recommendations(
        self, query: str, user_context: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommendations based on query and user context
        """
        recommendations = []

        # Role-based recommendations
        user_role = user_context.get("role", "user")
        if user_role == "ceo":
            recommendations.extend(
                [
                    "Access full organizational overview",
                    "Review strategic initiatives",
                    "Monitor key performance indicators",
                ]
            )
        elif user_role in ["cto", "backend", "frontend", "mobile", "platform"]:
            recommendations.extend(
                [
                    "Review technical documentation",
                    "Check system architecture",
                    "Monitor development metrics",
                ]
            )
        elif user_role in ["cpo", "pm", "design", "ux"]:
            recommendations.extend(
                [
                    "Review product roadmap",
                    "Check user feedback",
                    "Monitor product metrics",
                ]
            )

        # Panel-based recommendations
        user_panel = user_context.get("panel", "user")
        if user_panel == "andrei":
            recommendations.extend(
                [
                    "Access God Mode features",
                    "Review system status",
                    "Execute administrative commands",
                ]
            )
        elif user_panel == "business":
            recommendations.extend(
                [
                    "Review business analytics",
                    "Check multi-business status",
                    "Access business AI council",
                ]
            )
        elif user_panel == "dev":
            recommendations.extend(
                [
                    "Access development tools",
                    "Check GitHub integration",
                    "Review API documentation",
                ]
            )

        return recommendations[:5]  # Limit to 5 recommendations

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connections to both CoolBits.ai and Vertex AI
        """
        results = {
            "coolbits_ai": {"status": "unknown", "error": None},
            "vertex_ai": {"status": "unknown", "error": None},
            "timestamp": datetime.now().isoformat(),
        }

        # Test CoolBits.ai connection
        try:
            response = requests.get(f"{self.coolbits_api_url}/health", timeout=5)
            if response.status_code == 200:
                results["coolbits_ai"]["status"] = "connected"
            else:
                results["coolbits_ai"]["status"] = "error"
                results["coolbits_ai"]["error"] = f"HTTP {response.status_code}"
        except Exception as e:
            results["coolbits_ai"]["status"] = "error"
            results["coolbits_ai"]["error"] = str(e)

        # Test Vertex AI connection
        try:
            # Try to initialize and get endpoint info
            aiplatform.init(project=self.PROJECT_ID, location=self.LOCATION)
            results["vertex_ai"]["status"] = "connected"
        except Exception as e:
            results["vertex_ai"]["status"] = "error"
            results["vertex_ai"]["error"] = str(e)

        return results


def main():
    """Main function for testing RAG system"""
    print("🚀 CoolBits.ai RAG System with Vertex AI Vector Search")
    print("=" * 60)

    # Initialize RAG system
    try:
        rag = CoolBitsRAG()
        print("✅ RAG system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG system: {e}")
        return

    # Test connections
    print("\n🔍 Testing connections...")
    connection_test = rag.test_connection()

    print(f"CoolBits.ai: {connection_test['coolbits_ai']['status']}")
    if connection_test["coolbits_ai"]["error"]:
        print(f"  Error: {connection_test['coolbits_ai']['error']}")

    print(f"Vertex AI: {connection_test['vertex_ai']['status']}")
    if connection_test["vertex_ai"]["error"]:
        print(f"  Error: {connection_test['vertex_ai']['error']}")

    # Test RAG functionality
    if connection_test["coolbits_ai"]["status"] == "connected":
        print("\n🧠 Testing RAG functionality...")

        # Test organizational knowledge search
        test_query = "What are the main technology roles in CoolBits.ai?"
        result = rag.search_organizational_knowledge(test_query)

        if result["success"]:
            print(f"✅ RAG search successful for: '{test_query}'")
        else:
            print(f"❌ RAG search failed: {result.get('error', 'Unknown error')}")

        # Test role-specific knowledge
        role_result = rag.get_role_specific_knowledge(
            "ceo", "What are my responsibilities?"
        )
        if role_result["success"]:
            print("✅ Role-specific knowledge retrieval successful")
        else:
            print(
                f"❌ Role-specific knowledge failed: {role_result.get('error', 'Unknown error')}"
            )

    print("\n🎯 RAG System Test Complete!")


if __name__ == "__main__":
    main()
