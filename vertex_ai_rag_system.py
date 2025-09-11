#!/usr/bin/env python3
"""
🧠 CoolBits.ai Vertex AI Compatible RAG System
Vector search compatible with Google Cloud Vertex AI

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
import json
import logging
import sqlite3
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import uuid
import hashlib
import pickle
import base64

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Vector search libraries
try:
    import torch
    from sentence_transformers import SentenceTransformer
    import faiss

    HAS_VECTOR_LIBS = True
except ImportError:
    HAS_VECTOR_LIBS = False
    print(
        "⚠️ Vector libraries not available. Install: pip install torch sentence-transformers faiss-cpu"
    )

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class VertexAIConfig(BaseModel):
    base_port: int = 8094
    max_domains: int = 100
    gpu_enabled: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"
    db_path: str = "vertex_rag.db"
    vector_dimension: int = 384  # all-MiniLM-L6-v2 dimension
    similarity_threshold: float = 0.7
    max_results: int = 10


config = VertexAIConfig()


# Data models compatible with Vertex AI
class Document(BaseModel):
    id: str
    domain_id: str
    title: str
    content: str
    doc_type: str
    created_at: datetime
    updated_at: datetime
    embedding_id: Optional[str] = None
    metadata: Dict[str, Any] = {}
    # Vertex AI compatible fields
    vertex_id: Optional[str] = None
    vertex_embedding: Optional[List[float]] = None
    vertex_metadata: Dict[str, Any] = {}


class VectorSearchRequest(BaseModel):
    domain_id: str
    query: str
    max_results: int = 10
    similarity_threshold: float = 0.7
    use_vertex_format: bool = True


class VectorSearchResponse(BaseModel):
    domain_id: str
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    processing_time: float
    timestamp: datetime
    # Vertex AI compatible response format
    vertex_format: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"


class DocumentRequest(BaseModel):
    domain_id: str
    title: str
    content: str
    doc_type: str = "general"
    metadata: Dict[str, Any] = {}
    # Vertex AI compatible fields
    vertex_metadata: Dict[str, Any] = {}


# Vector search engine
class VertexAIVectorSearch:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.embedding_model = None
        self.indexes: Dict[str, faiss.IndexFlatIP] = {}
        self.document_mappings: Dict[str, Dict[int, str]] = {}

        if HAS_VECTOR_LIBS:
            self._initialize_embedding_model()
        else:
            logger.warning("Vector libraries not available. Using text-based search.")

    def _initialize_embedding_model(self):
        """Initialize embedding model compatible with Vertex AI"""
        try:
            device = (
                "cuda" if torch.cuda.is_available() and config.gpu_enabled else "cpu"
            )
            self.embedding_model = SentenceTransformer(
                config.embedding_model, device=device
            )
            logger.info(f"✅ Embedding model loaded on {device}")
        except Exception as e:
            logger.error(f"❌ Error loading embedding model: {e}")
            self.embedding_model = None

    def create_domain_index(self, domain_id: str):
        """Create FAISS index for a domain"""
        if not HAS_VECTOR_LIBS:
            return

        try:
            # Use Inner Product for similarity (compatible with Vertex AI)
            index = faiss.IndexFlatIP(self.dimension)
            self.indexes[domain_id] = index
            self.document_mappings[domain_id] = {}
            logger.info(f"✅ Created FAISS index for domain {domain_id}")
        except Exception as e:
            logger.error(f"❌ Error creating index for {domain_id}: {e}")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding for text"""
        if not self.embedding_model:
            return None

        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"❌ Error generating embedding: {e}")
            return None

    def add_document_to_index(
        self, domain_id: str, doc_id: str, embedding: List[float]
    ):
        """Add document embedding to FAISS index"""
        if not HAS_VECTOR_LIBS or domain_id not in self.indexes:
            return False

        try:
            # Normalize embedding for Inner Product
            embedding_array = np.array([embedding], dtype=np.float32)
            faiss.normalize_L2(embedding_array)

            # Add to index
            self.indexes[domain_id].add(embedding_array)

            # Store mapping
            doc_index = self.indexes[domain_id].ntotal - 1
            self.document_mappings[domain_id][doc_index] = doc_id

            logger.info(f"✅ Added document {doc_id} to index for domain {domain_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error adding document to index: {e}")
            return False

    def search_similar(
        self,
        domain_id: str,
        query_embedding: List[float],
        max_results: int = 10,
        similarity_threshold: float = 0.7,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents using vector similarity"""
        if not HAS_VECTOR_LIBS or domain_id not in self.indexes:
            return []

        try:
            # Normalize query embedding
            query_array = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_array)

            # Search
            scores, indices = self.indexes[domain_id].search(query_array, max_results)

            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx != -1 and score >= similarity_threshold:
                    doc_id = self.document_mappings[domain_id].get(idx)
                    if doc_id:
                        results.append(
                            {
                                "document_id": doc_id,
                                "similarity_score": float(score),
                                "index": int(idx),
                            }
                        )

            return results
        except Exception as e:
            logger.error(f"❌ Error searching index: {e}")
            return []

    def get_index_stats(self, domain_id: str) -> Dict[str, Any]:
        """Get statistics for domain index"""
        if domain_id not in self.indexes:
            return {"total_documents": 0, "dimension": self.dimension}

        return {
            "total_documents": self.indexes[domain_id].ntotal,
            "dimension": self.dimension,
            "index_type": "FAISS_IndexFlatIP",
        }


# Database setup compatible with Vertex AI
class VertexAIDatabase:
    def __init__(self, db_path: str = "vertex_rag.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with Vertex AI compatible schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create documents table with Vertex AI fields
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                domain_id TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                doc_type TEXT DEFAULT 'general',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                embedding_id TEXT,
                metadata TEXT DEFAULT '{}',
                vertex_id TEXT,
                vertex_embedding TEXT,
                vertex_metadata TEXT DEFAULT '{}'
            )
        """
        )

        # Create domains table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS domains (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                domain_type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                vertex_config TEXT DEFAULT '{}'
            )
        """
        )

        # Create embeddings table for Vertex AI compatibility
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                domain_id TEXT NOT NULL,
                embedding_vector TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                vertex_embedding_id TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Vertex AI compatible database initialized")

    def add_domain(
        self, domain_id: str, name: str, domain_type: str, description: str = ""
    ):
        """Add a new domain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        vertex_config = json.dumps(
            {
                "embedding_model": config.embedding_model,
                "dimension": config.vector_dimension,
                "similarity_threshold": config.similarity_threshold,
            }
        )

        cursor.execute(
            """
            INSERT OR REPLACE INTO domains (id, name, domain_type, description, vertex_config)
            VALUES (?, ?, ?, ?, ?)
        """,
            (domain_id, name, domain_type, description, vertex_config),
        )

        conn.commit()
        conn.close()

    def get_domains(self) -> List[Dict[str, Any]]:
        """Get all domains"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT d.id, d.name, d.domain_type, d.description, d.created_at, d.vertex_config,
                   COUNT(doc.id) as doc_count
            FROM domains d
            LEFT JOIN documents doc ON d.id = doc.domain_id
            GROUP BY d.id, d.name, d.domain_type, d.description, d.created_at, d.vertex_config
            ORDER BY d.created_at DESC
        """
        )

        rows = cursor.fetchall()
        conn.close()

        domains = []
        for row in rows:
            vertex_config = json.loads(row[5]) if row[5] else {}
            domains.append(
                {
                    "domain_id": row[0],
                    "domain_name": row[1],
                    "domain_type": row[2],
                    "description": row[3],
                    "created_at": row[4],
                    "documents_count": row[6],
                    "status": "active",
                    "vertex_config": vertex_config,
                }
            )

        return domains

    def add_document(self, doc: Document) -> str:
        """Add document to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Serialize embeddings
        vertex_embedding_str = (
            json.dumps(doc.vertex_embedding) if doc.vertex_embedding else None
        )

        cursor.execute(
            """
            INSERT INTO documents (id, domain_id, title, content, doc_type, metadata, 
                                vertex_id, vertex_embedding, vertex_metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                doc.id,
                doc.domain_id,
                doc.title,
                doc.content,
                doc.doc_type,
                json.dumps(doc.metadata),
                doc.vertex_id,
                vertex_embedding_str,
                json.dumps(doc.vertex_metadata),
            ),
        )

        conn.commit()
        conn.close()
        return doc.id

    def get_documents(self, domain_id: str) -> List[Document]:
        """Get all documents for a domain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, domain_id, title, content, doc_type, created_at, updated_at, 
                   embedding_id, metadata, vertex_id, vertex_embedding, vertex_metadata
            FROM documents WHERE domain_id = ?
            ORDER BY created_at DESC
        """,
            (domain_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        documents = []
        for row in rows:
            vertex_embedding = json.loads(row[10]) if row[10] else None
            doc = Document(
                id=row[0],
                domain_id=row[1],
                title=row[2],
                content=row[3],
                doc_type=row[4],
                created_at=datetime.fromisoformat(row[5]),
                updated_at=datetime.fromisoformat(row[6]),
                embedding_id=row[7],
                metadata=json.loads(row[8]) if row[8] else {},
                vertex_id=row[9],
                vertex_embedding=vertex_embedding,
                vertex_metadata=json.loads(row[11]) if row[11] else {},
            )
            documents.append(doc)

        return documents

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get specific document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, domain_id, title, content, doc_type, created_at, updated_at, 
                   embedding_id, metadata, vertex_id, vertex_embedding, vertex_metadata
            FROM documents WHERE id = ?
        """,
            (doc_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            vertex_embedding = json.loads(row[10]) if row[10] else None
            return Document(
                id=row[0],
                domain_id=row[1],
                title=row[2],
                content=row[3],
                doc_type=row[4],
                created_at=datetime.fromisoformat(row[5]),
                updated_at=datetime.fromisoformat(row[6]),
                embedding_id=row[7],
                metadata=json.loads(row[8]) if row[8] else {},
                vertex_id=row[9],
                vertex_embedding=vertex_embedding,
                vertex_metadata=json.loads(row[11]) if row[11] else {},
            )
        return None


# Global RAG manager with Vertex AI compatibility
class VertexAIRAGManager:
    def __init__(self):
        self.db = VertexAIDatabase(config.db_path)
        self.vector_search = VertexAIVectorSearch(config.vector_dimension)
        self.domains: Dict[str, Dict] = {}
        self.init_test_domains()

    def init_test_domains(self):
        """Initialize test domains compatible with Vertex AI"""
        test_domains = [
            (
                "ceo",
                "CEO Leadership",
                "role",
                "Chief Executive Officer responsibilities and strategies",
            ),
            (
                "cto",
                "CTO Technology",
                "role",
                "Chief Technology Officer technical leadership",
            ),
            (
                "ai_board",
                "AI Board Management",
                "industry",
                "AI Board coordination and management",
            ),
            (
                "blockchain",
                "Blockchain Technology",
                "industry",
                "Blockchain and cryptocurrency expertise",
            ),
            (
                "fintech",
                "FinTech Solutions",
                "industry",
                "Financial technology and digital banking",
            ),
        ]

        for domain_id, name, domain_type, description in test_domains:
            self.db.add_domain(domain_id, name, domain_type, description)
            self.vector_search.create_domain_index(domain_id)

        logger.info(f"✅ Initialized {len(test_domains)} Vertex AI compatible domains")

    def add_document(
        self,
        domain_id: str,
        title: str,
        content: str,
        doc_type: str = "general",
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Add document with vector embedding"""
        doc_id = str(uuid.uuid4())

        # Generate embedding
        embedding = self.vector_search.generate_embedding(f"{title} {content}")

        # Create Vertex AI compatible document
        doc = Document(
            id=doc_id,
            domain_id=domain_id,
            title=title,
            content=content,
            doc_type=doc_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata=metadata or {},
            vertex_id=f"vertex_{doc_id}",
            vertex_embedding=embedding,
            vertex_metadata={
                "source": "local_development",
                "embedding_model": config.embedding_model,
                "dimension": config.vector_dimension,
            },
        )

        # Add to database
        doc_id = self.db.add_document(doc)

        # Add to vector index
        if embedding:
            self.vector_search.add_document_to_index(domain_id, doc_id, embedding)

        logger.info(
            f"✅ Added document '{title}' to domain {domain_id} with vector embedding"
        )
        return doc_id

    def vector_search_documents(
        self,
        domain_id: str,
        query: str,
        max_results: int = 10,
        similarity_threshold: float = 0.7,
    ) -> VectorSearchResponse:
        """Perform vector search compatible with Vertex AI"""
        start_time = datetime.now()

        # Generate query embedding
        query_embedding = self.vector_search.generate_embedding(query)

        if not query_embedding:
            # Fallback to text search
            return self._fallback_text_search(domain_id, query, max_results)

        # Perform vector search
        search_results = self.vector_search.search_similar(
            domain_id, query_embedding, max_results, similarity_threshold
        )

        # Get document details
        results = []
        for result in search_results:
            doc = self.db.get_document(result["document_id"])
            if doc:
                results.append(
                    {
                        "document_id": doc.id,
                        "title": doc.title,
                        "content": doc.content,
                        "doc_type": doc.doc_type,
                        "similarity_score": result["similarity_score"],
                        "created_at": doc.created_at.isoformat(),
                        "updated_at": doc.updated_at.isoformat(),
                        "vertex_id": doc.vertex_id,
                        "vertex_metadata": doc.vertex_metadata,
                    }
                )

        processing_time = (datetime.now() - start_time).total_seconds()

        return VectorSearchResponse(
            domain_id=domain_id,
            query=query,
            results=results,
            total_results=len(results),
            processing_time=processing_time,
            timestamp=datetime.now(),
            vertex_format=True,
            embedding_model=config.embedding_model,
        )

    def _fallback_text_search(
        self, domain_id: str, query: str, max_results: int
    ) -> VectorSearchResponse:
        """Fallback text search when vector search is not available"""
        documents = self.db.get_documents(domain_id)
        results = []

        query_words = query.lower().split()

        for doc in documents:
            content_words = doc.content.lower().split()
            title_words = doc.title.lower().split()

            # Calculate relevance score
            content_matches = sum(1 for word in query_words if word in content_words)
            title_matches = sum(1 for word in query_words if word in title_words)

            total_matches = content_matches + (title_matches * 2)
            relevance_score = total_matches / len(query_words) if query_words else 0

            if relevance_score > 0:
                results.append(
                    {
                        "document_id": doc.id,
                        "title": doc.title,
                        "content": doc.content,
                        "doc_type": doc.doc_type,
                        "similarity_score": relevance_score,
                        "created_at": doc.created_at.isoformat(),
                        "updated_at": doc.updated_at.isoformat(),
                        "vertex_id": doc.vertex_id,
                        "vertex_metadata": doc.vertex_metadata,
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = results[:max_results]

        return VectorSearchResponse(
            domain_id=domain_id,
            query=query,
            results=results,
            total_results=len(results),
            processing_time=0.001,
            timestamp=datetime.now(),
            vertex_format=True,
            embedding_model="text_fallback",
        )

    def get_domains(self) -> List[Dict[str, Any]]:
        """Get all domains"""
        return self.db.get_domains()

    def get_documents(self, domain_id: str) -> List[Document]:
        """Get documents for domain"""
        return self.db.get_documents(domain_id)

    def get_vector_stats(self, domain_id: str) -> Dict[str, Any]:
        """Get vector search statistics for domain"""
        return self.vector_search.get_index_stats(domain_id)


# Initialize RAG manager
rag_manager = VertexAIRAGManager()

# Create FastAPI app
app = FastAPI(
    title="CoolBits.ai Vertex AI Compatible RAG System",
    description="Vector search compatible with Google Cloud Vertex AI",
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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    domains = rag_manager.get_domains()
    vector_libs_available = HAS_VECTOR_LIBS

    return {
        "status": "healthy",
        "service": "CoolBits.ai Vertex AI Compatible RAG System",
        "version": "1.0.0",
        "domains_count": len(domains),
        "database_path": config.db_path,
        "vector_libraries_available": vector_libs_available,
        "embedding_model": config.embedding_model,
        "vector_dimension": config.vector_dimension,
        "gpu_enabled": config.gpu_enabled,
        "vertex_ai_compatible": True,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/domains")
async def list_domains():
    """List all available RAG domains"""
    domains = rag_manager.get_domains()
    return {
        "domains": domains,
        "total_domains": len(domains),
        "vertex_ai_compatible": True,
    }


@app.get("/domains/{domain_id}")
async def get_domain(domain_id: str):
    """Get specific domain information"""
    domains = rag_manager.get_domains()
    domain = next((d for d in domains if d["domain_id"] == domain_id), None)

    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    # Add vector stats
    vector_stats = rag_manager.get_vector_stats(domain_id)
    domain.update(vector_stats)

    return domain


@app.get("/domains/{domain_id}/documents")
async def get_domain_documents(domain_id: str):
    """Get all documents for a domain"""
    domains = rag_manager.get_domains()
    domain = next((d for d in domains if d["domain_id"] == domain_id), None)

    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    documents = rag_manager.get_documents(domain_id)

    return {
        "domain_id": domain_id,
        "domain_name": domain["domain_name"],
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "doc_type": doc.doc_type,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
                "metadata": doc.metadata,
                "vertex_id": doc.vertex_id,
                "vertex_metadata": doc.vertex_metadata,
                "has_embedding": bool(doc.vertex_embedding),
            }
            for doc in documents
        ],
        "total_documents": len(documents),
        "vertex_ai_compatible": True,
    }


@app.post("/domains/{domain_id}/add-document")
async def add_document(domain_id: str, request: DocumentRequest):
    """Add a new document to a domain"""
    domains = rag_manager.get_domains()
    domain = next((d for d in domains if d["domain_id"] == domain_id), None)

    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    try:
        doc_id = rag_manager.add_document(
            domain_id=domain_id,
            title=request.title,
            content=request.content,
            doc_type=request.doc_type,
            metadata=request.metadata,
        )

        return {
            "status": "success",
            "message": f"Document added to {domain['domain_name']} with vector embedding",
            "document_id": doc_id,
            "vertex_id": f"vertex_{doc_id}",
            "total_documents": len(rag_manager.get_documents(domain_id)),
            "vertex_ai_compatible": True,
        }

    except Exception as e:
        logger.error(f"Error adding document to {domain_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/domains/{domain_id}/vector-search", response_model=VectorSearchResponse)
async def vector_search_documents(domain_id: str, request: VectorSearchRequest):
    """Perform vector search compatible with Vertex AI"""
    domains = rag_manager.get_domains()
    domain = next((d for d in domains if d["domain_id"] == domain_id), None)

    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    try:
        result = rag_manager.vector_search_documents(
            domain_id=domain_id,
            query=request.query,
            max_results=request.max_results,
            similarity_threshold=request.similarity_threshold,
        )
        return result
    except Exception as e:
        logger.error(f"Error performing vector search in {domain_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/domains/{domain_id}/vector-stats")
async def get_vector_stats(domain_id: str):
    """Get vector search statistics for domain"""
    domains = rag_manager.get_domains()
    domain = next((d for d in domains if d["domain_id"] == domain_id), None)

    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    try:
        stats = rag_manager.get_vector_stats(domain_id)
        return {
            "domain_id": domain_id,
            "domain_name": domain["domain_name"],
            "vector_stats": stats,
            "embedding_model": config.embedding_model,
            "vector_dimension": config.vector_dimension,
            "vertex_ai_compatible": True,
        }
    except Exception as e:
        logger.error(f"Error getting vector stats for {domain_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("🚀 Starting CoolBits.ai Vertex AI Compatible RAG System")
    logger.info("🧠 Vector search compatible with Google Cloud Vertex AI")
    logger.info("📄 Real document management with SQLite database")
    logger.info("🔍 FAISS vector search with embeddings")
    logger.info("🌐 Available at: http://localhost:8094")

    uvicorn.run(app, host="localhost", port=8094, log_level="info")
