#!/usr/bin/env python3
"""
🧠 CoolBits.ai Multi-Domain RAG System
Each entity (role/industry) gets its own RAG with domain-specific knowledge

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import asyncio
import aiohttp
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class RAGConfig(BaseModel):
    base_port: int = 8090
    max_domains: int = 100
    gpu_enabled: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"


config = RAGConfig()


# Data models
class DomainRAG(BaseModel):
    domain_id: str
    domain_name: str
    domain_type: str  # "role" or "industry"
    api_keys: Dict[str, str]  # xAI and OpenAI keys
    documents: List[str]
    embeddings_count: int = 0
    last_updated: datetime
    status: str = "active"


class QueryRequest(BaseModel):
    domain_id: str
    query: str
    use_api: bool = True
    max_results: int = 5


class QueryResponse(BaseModel):
    domain_id: str
    query: str
    results: List[Dict[str, Any]]
    api_response: Optional[str] = None
    processing_time: float
    timestamp: datetime


# Global RAG manager
class MultiDomainRAGManager:
    def __init__(self):
        self.domains: Dict[str, DomainRAG] = {}
        self.embeddings_cache: Dict[str, Any] = {}
        self.api_clients: Dict[str, Dict[str, Any]] = {}

    async def initialize_domains(self):
        """Initialize all domains from team system"""
        try:
            # Get team data
            async with aiohttp.ClientSession() as session:
                # Get roles
                async with session.get("http://localhost:8088/team/roles") as resp:
                    roles_data = await resp.json()

                # Get industries
                async with session.get("http://localhost:8088/team/industries") as resp:
                    industries_data = await resp.json()

                # Create RAG domains for roles
                for role_id, role_data in roles_data["roles"].items():
                    domain_id = f"role_{role_id}"
                    self.domains[domain_id] = DomainRAG(
                        domain_id=domain_id,
                        domain_name=role_data["name"],
                        domain_type="role",
                        api_keys={
                            "xai": role_data["api_keys"]["xai_key"],
                            "openai": role_data["api_keys"]["openai_key"],
                        },
                        documents=self._get_role_documents(role_data),
                        last_updated=datetime.now(),
                    )

                # Create RAG domains for industries
                for industry_id, industry_data in industries_data["industries"].items():
                    domain_id = f"industry_{industry_id}"
                    self.domains[domain_id] = DomainRAG(
                        domain_id=domain_id,
                        domain_name=industry_data["name"],
                        domain_type="industry",
                        api_keys={
                            "xai": industry_data["api_keys"]["xai_key"],
                            "openai": industry_data["api_keys"]["openai_key"],
                        },
                        documents=self._get_industry_documents(industry_data),
                        last_updated=datetime.now(),
                    )

                logger.info(f"✅ Initialized {len(self.domains)} RAG domains")

        except Exception as e:
            logger.error(f"❌ Error initializing domains: {e}")

    def _get_role_documents(self, role_data: Dict) -> List[str]:
        """Generate domain-specific documents for roles"""
        documents = []

        # Base role document
        documents.append(
            f"""
        Role: {role_data['name']}
        Category: {role_data['category']}
        Level: {role_data['level']}
        Responsibilities: {', '.join(role_data['responsibilities'])}
        Permissions: {', '.join(role_data['permissions'])}
        
        This role is responsible for {role_data['category'].lower()} operations
        and has {role_data['level']} level access to the organization.
        """
        )

        # Add specific knowledge based on role
        if role_data["category"] == "Executive":
            documents.append(
                """
            Executive Leadership Knowledge:
            - Strategic planning and vision setting
            - Board communication and governance
            - Stakeholder management
            - Financial oversight and budgeting
            - Risk management and compliance
            """
            )
        elif role_data["category"] == "Technology":
            documents.append(
                """
            Technology Leadership Knowledge:
            - Software architecture and design patterns
            - Cloud infrastructure and DevOps
            - Security best practices
            - Technology stack decisions
            - Team management and technical mentoring
            """
            )
        elif role_data["category"] == "Product":
            documents.append(
                """
            Product Management Knowledge:
            - Product strategy and roadmap planning
            - User research and analytics
            - Feature prioritization
            - Cross-functional collaboration
            - Market analysis and competitive intelligence
            """
            )

        return documents

    def _get_industry_documents(self, industry_data: Dict) -> List[str]:
        """Generate domain-specific documents for industries"""
        documents = []

        # Base industry document
        documents.append(
            f"""
        Industry: {industry_data['name']}
        Description: {industry_data['description']}
        
        This industry focuses on {industry_data['description'].lower()}
        and requires specialized knowledge and expertise.
        """
        )

        # Add specific industry knowledge
        industry_name = industry_data["name"].lower()
        if "ai" in industry_name or "artificial intelligence" in industry_name:
            documents.append(
                """
            AI Industry Knowledge:
            - Machine learning algorithms and models
            - Neural networks and deep learning
            - Natural language processing
            - Computer vision
            - AI ethics and responsible AI
            - MLOps and model deployment
            """
            )
        elif "blockchain" in industry_name or "crypto" in industry_name:
            documents.append(
                """
            Blockchain Industry Knowledge:
            - Cryptocurrency and digital assets
            - Smart contracts and DeFi
            - Consensus mechanisms
            - Blockchain security
            - Tokenomics and governance
            - Web3 and decentralized applications
            """
            )
        elif "fintech" in industry_name or "finance" in industry_name:
            documents.append(
                """
            Fintech Industry Knowledge:
            - Payment processing and digital wallets
            - Banking and financial services
            - Regulatory compliance (PCI DSS, GDPR)
            - Risk management and fraud detection
            - Financial APIs and integrations
            - Cryptocurrency and digital assets
            """
            )

        return documents

    async def query_domain(
        self, domain_id: str, query: str, use_api: bool = True
    ) -> QueryResponse:
        """Query a specific domain's RAG system"""
        start_time = datetime.now()

        if domain_id not in self.domains:
            raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

        domain = self.domains[domain_id]

        # Simulate document search (in real implementation, use vector search)
        relevant_docs = self._search_documents(domain, query)

        # If API is requested, call the appropriate API
        api_response = None
        if use_api:
            api_response = await self._call_api(domain, query, relevant_docs)

        processing_time = (datetime.now() - start_time).total_seconds()

        return QueryResponse(
            domain_id=domain_id,
            query=query,
            results=relevant_docs,
            api_response=api_response,
            processing_time=processing_time,
            timestamp=datetime.now(),
        )

    def _search_documents(self, domain: DomainRAG, query: str) -> List[Dict[str, Any]]:
        """Search documents for relevant content"""
        results = []

        for i, doc in enumerate(domain.documents):
            # Simple keyword matching (in real implementation, use semantic search)
            query_words = query.lower().split()
            doc_words = doc.lower().split()

            matches = sum(1 for word in query_words if word in doc_words)
            if matches > 0:
                results.append(
                    {
                        "document_id": f"{domain.domain_id}_doc_{i}",
                        "content": doc[:200] + "..." if len(doc) > 200 else doc,
                        "relevance_score": matches / len(query_words),
                        "domain": domain.domain_name,
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:5]

    async def _call_api(
        self, domain: DomainRAG, query: str, context_docs: List[Dict]
    ) -> str:
        """Call the appropriate API (xAI or OpenAI) for the domain"""
        try:
            # Prepare context from documents
            context = "\n".join([doc["content"] for doc in context_docs[:3]])

            # For now, simulate API response (in real implementation, call actual APIs)
            if domain.api_keys.get("xai"):
                return f"[xAI Response for {domain.domain_name}]: Based on {domain.domain_type} knowledge: {query} - Context: {context[:100]}..."
            elif domain.api_keys.get("openai"):
                return f"[OpenAI Response for {domain.domain_name}]: Based on {domain.domain_type} knowledge: {query} - Context: {context[:100]}..."
            else:
                return f"[Local Response for {domain.domain_name}]: {query} - Context: {context[:100]}..."

        except Exception as e:
            logger.error(f"Error calling API for {domain.domain_id}: {e}")
            return f"Error calling API: {str(e)}"


# Initialize RAG manager
rag_manager = MultiDomainRAGManager()

# Create FastAPI app
app = FastAPI(
    title="CoolBits.ai Multi-Domain RAG System",
    description="Domain-specific RAG for each role and industry with API integration",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize RAG system on startup"""
    logger.info("🚀 Starting CoolBits.ai Multi-Domain RAG System")
    await rag_manager.initialize_domains()
    logger.info(f"✅ Initialized {len(rag_manager.domains)} RAG domains")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CoolBits.ai Multi-Domain RAG System",
        "version": "1.0.0",
        "domains_count": len(rag_manager.domains),
        "gpu_enabled": config.gpu_enabled,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/domains")
async def list_domains():
    """List all available RAG domains"""
    return {
        "domains": [
            {
                "domain_id": domain.domain_id,
                "domain_name": domain.domain_name,
                "domain_type": domain.domain_type,
                "documents_count": len(domain.documents),
                "embeddings_count": domain.embeddings_count,
                "last_updated": domain.last_updated.isoformat(),
                "status": domain.status,
            }
            for domain in rag_manager.domains.values()
        ],
        "total_domains": len(rag_manager.domains),
    }


@app.get("/domains/{domain_id}")
async def get_domain(domain_id: str):
    """Get specific domain information"""
    if domain_id not in rag_manager.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    domain = rag_manager.domains[domain_id]
    return {
        "domain_id": domain.domain_id,
        "domain_name": domain.domain_name,
        "domain_type": domain.domain_type,
        "api_keys": {
            "xai_configured": bool(domain.api_keys.get("xai")),
            "openai_configured": bool(domain.api_keys.get("openai")),
        },
        "documents": domain.documents,
        "embeddings_count": domain.embeddings_count,
        "last_updated": domain.last_updated.isoformat(),
        "status": domain.status,
    }


@app.post("/query", response_model=QueryResponse)
async def query_domain_rag(request: QueryRequest):
    """Query a specific domain's RAG system"""
    try:
        result = await rag_manager.query_domain(
            domain_id=request.domain_id, query=request.query, use_api=request.use_api
        )
        return result
    except Exception as e:
        logger.error(f"Error querying domain {request.domain_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/domains/{domain_id}/query")
async def query_domain_simple(domain_id: str, query: str, use_api: bool = True):
    """Simple query endpoint"""
    try:
        result = await rag_manager.query_domain(domain_id, query, use_api)
        return result
    except Exception as e:
        logger.error(f"Error querying domain {domain_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/domains/{domain_id}/documents")
async def get_domain_documents(domain_id: str):
    """Get all documents for a domain"""
    if domain_id not in rag_manager.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    domain = rag_manager.domains[domain_id]
    return {
        "domain_id": domain_id,
        "domain_name": domain.domain_name,
        "documents": domain.documents,
        "total_documents": len(domain.documents),
    }


@app.post("/domains/{domain_id}/add-document")
async def add_document(domain_id: str, document: str):
    """Add a new document to a domain"""
    if domain_id not in rag_manager.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    domain = rag_manager.domains[domain_id]
    domain.documents.append(document)
    domain.last_updated = datetime.now()

    return {
        "status": "success",
        "message": f"Document added to {domain.domain_name}",
        "total_documents": len(domain.documents),
    }


if __name__ == "__main__":
    logger.info("🚀 Starting CoolBits.ai Multi-Domain RAG System")
    logger.info("🧠 Each role and industry gets its own RAG with API keys")
    logger.info("🌐 Available at: http://localhost:8090")

    uvicorn.run(app, host="localhost", port=8090, log_level="info")
