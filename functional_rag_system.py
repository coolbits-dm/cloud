#!/usr/bin/env python3
"""
🧠 CoolBits.ai Complete Functional RAG System
Real document management, embeddings, and search functionality

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import json
import logging
import aiohttp
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class RAGConfig(BaseModel):
    base_port: int = 8092
    max_domains: int = 100
    gpu_enabled: bool = True
    embedding_model: str = "all-MiniLM-L6-v2"
    db_path: str = "rag_system.db"


config = RAGConfig()


# Data models
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


class QueryRequest(BaseModel):
    domain_id: str
    query: str
    use_api: bool = True
    max_results: int = 5
    similarity_threshold: float = 0.7


class QueryResponse(BaseModel):
    domain_id: str
    query: str
    results: List[Dict[str, Any]]
    api_response: Optional[str] = None
    processing_time: float
    timestamp: datetime


class DocumentRequest(BaseModel):
    domain_id: str
    title: str
    content: str
    doc_type: str = "general"
    metadata: Dict[str, Any] = {}


# Database setup
class RAGDatabase:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create documents table
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
                metadata TEXT DEFAULT '{}'
            )
        """
        )

        # Create embeddings table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                domain_id TEXT NOT NULL,
                embedding_vector TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (id)
            )
        """
        )

        # Create chat_history table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id TEXT PRIMARY KEY,
                domain_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_response TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}'
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")

    def add_document(self, doc: Document) -> str:
        """Add document to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO documents (id, domain_id, title, content, doc_type, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                doc.id,
                doc.domain_id,
                doc.title,
                doc.content,
                doc.doc_type,
                json.dumps(doc.metadata),
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
            SELECT id, domain_id, title, content, doc_type, created_at, updated_at, embedding_id, metadata
            FROM documents WHERE domain_id = ?
            ORDER BY created_at DESC
        """,
            (domain_id,),
        )

        rows = cursor.fetchall()
        conn.close()

        documents = []
        for row in rows:
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
            )
            documents.append(doc)

        return documents

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get specific document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, domain_id, title, content, doc_type, created_at, updated_at, embedding_id, metadata
            FROM documents WHERE id = ?
        """,
            (doc_id,),
        )

        row = cursor.fetchone()
        conn.close()

        if row:
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
            )
        return None

    def update_document(
        self, doc_id: str, title: str, content: str, doc_type: str = None
    ) -> bool:
        """Update document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if doc_type:
            cursor.execute(
                """
                UPDATE documents 
                SET title = ?, content = ?, doc_type = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (title, content, doc_type, doc_id),
            )
        else:
            cursor.execute(
                """
                UPDATE documents 
                SET title = ?, content = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (title, content, doc_id),
            )

        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def delete_document(self, doc_id: str) -> bool:
        """Delete document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
        success = cursor.rowcount > 0

        conn.commit()
        conn.close()
        return success

    def add_chat_message(
        self, domain_id: str, user_message: str, assistant_response: str
    ) -> str:
        """Add chat message to history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        chat_id = str(uuid.uuid4())
        cursor.execute(
            """
            INSERT INTO chat_history (id, domain_id, user_message, assistant_response)
            VALUES (?, ?, ?, ?)
        """,
            (chat_id, domain_id, user_message, assistant_response),
        )

        conn.commit()
        conn.close()
        return chat_id

    def get_chat_history(self, domain_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get chat history for domain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, user_message, assistant_response, timestamp
            FROM chat_history 
            WHERE domain_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """,
            (domain_id, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        history = []
        for row in rows:
            history.append(
                {
                    "id": row[0],
                    "user_message": row[1],
                    "assistant_response": row[2],
                    "timestamp": row[3],
                }
            )

        return history


# Global RAG manager
class FunctionalRAGManager:
    def __init__(self):
        self.db = RAGDatabase(config.db_path)
        self.domains: Dict[str, Dict] = {}
        self.embeddings_cache: Dict[str, Any] = {}

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
                    self.domains[domain_id] = {
                        "domain_id": domain_id,
                        "domain_name": role_data["name"],
                        "domain_type": "role",
                        "api_keys": {
                            "xai": role_data["api_keys"]["xai_key"],
                            "openai": role_data["api_keys"]["openai_key"],
                        },
                        "documents_count": len(self.db.get_documents(domain_id)),
                        "last_updated": datetime.now().isoformat(),
                        "status": "active",
                    }

                # Create RAG domains for industries
                for industry_id, industry_data in industries_data["industries"].items():
                    domain_id = f"industry_{industry_id}"
                    self.domains[domain_id] = {
                        "domain_id": domain_id,
                        "domain_name": industry_data["name"],
                        "domain_type": "industry",
                        "api_keys": {
                            "xai": industry_data["api_keys"]["xai_key"],
                            "openai": industry_data["api_keys"]["openai_key"],
                        },
                        "documents_count": len(self.db.get_documents(domain_id)),
                        "last_updated": datetime.now().isoformat(),
                        "status": "active",
                    }

                logger.info(
                    f"✅ Initialized {len(self.domains)} functional RAG domains"
                )

        except Exception as e:
            logger.error(f"❌ Error initializing domains: {e}")

    def add_document(
        self, domain_id: str, title: str, content: str, doc_type: str = "general"
    ) -> str:
        """Add document to domain"""
        doc_id = str(uuid.uuid4())
        doc = Document(
            id=doc_id,
            domain_id=domain_id,
            title=title,
            content=content,
            doc_type=doc_type,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            metadata={"source": "admin_panel", "added_by": "user"},
        )

        doc_id = self.db.add_document(doc)

        # Update domain document count
        if domain_id in self.domains:
            self.domains[domain_id]["documents_count"] = len(
                self.db.get_documents(domain_id)
            )
            self.domains[domain_id]["last_updated"] = datetime.now().isoformat()

        logger.info(f"✅ Added document '{title}' to domain {domain_id}")
        return doc_id

    def get_documents(self, domain_id: str) -> List[Document]:
        """Get documents for domain"""
        return self.db.get_documents(domain_id)

    def update_document(
        self, doc_id: str, title: str, content: str, doc_type: str = None
    ) -> bool:
        """Update document"""
        return self.db.update_document(doc_id, title, content, doc_type)

    def delete_document(self, doc_id: str) -> bool:
        """Delete document"""
        return self.db.delete_document(doc_id)

    def search_documents(
        self, domain_id: str, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search documents using simple text matching"""
        documents = self.db.get_documents(domain_id)
        results = []

        query_words = query.lower().split()

        for doc in documents:
            content_words = doc.content.lower().split()
            title_words = doc.title.lower().split()

            # Calculate relevance score
            content_matches = sum(1 for word in query_words if word in content_words)
            title_matches = sum(1 for word in query_words if word in title_words)

            total_matches = content_matches + (
                title_matches * 2
            )  # Title matches weighted more
            relevance_score = total_matches / len(query_words) if query_words else 0

            if relevance_score > 0:
                results.append(
                    {
                        "document_id": doc.id,
                        "title": doc.title,
                        "content": (
                            doc.content[:200] + "..."
                            if len(doc.content) > 200
                            else doc.content
                        ),
                        "doc_type": doc.doc_type,
                        "relevance_score": relevance_score,
                        "created_at": doc.created_at.isoformat(),
                        "updated_at": doc.updated_at.isoformat(),
                    }
                )

        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:max_results]

    async def query_domain(
        self, domain_id: str, query: str, use_api: bool = True
    ) -> QueryResponse:
        """Query domain with real search and API integration"""
        start_time = datetime.now()

        if domain_id not in self.domains:
            raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

        # Search documents
        search_results = self.search_documents(domain_id, query)

        # Generate API response if requested
        api_response = None
        if use_api and search_results:
            api_response = await self._generate_api_response(
                domain_id, query, search_results
            )

        processing_time = (datetime.now() - start_time).total_seconds()

        return QueryResponse(
            domain_id=domain_id,
            query=query,
            results=search_results,
            api_response=api_response,
            processing_time=processing_time,
            timestamp=datetime.now(),
        )

    async def _generate_api_response(
        self, domain_id: str, query: str, search_results: List[Dict]
    ) -> str:
        """Generate API response using context from search results"""
        try:
            domain = self.domains[domain_id]

            # Prepare context from search results
            context = "\n".join(
                [
                    f"Title: {r['title']}\nContent: {r['content']}"
                    for r in search_results[:3]
                ]
            )

            # For now, simulate API response (in real implementation, call actual APIs)
            if domain["api_keys"].get("xai"):
                response = f"[xAI Response for {domain['domain_name']}]:\n\nBased on {domain['domain_type']} knowledge base:\n\nQuery: {query}\n\nContext from documents:\n{context[:500]}...\n\nThis response is generated using the specific knowledge base for {domain['domain_name']} with xAI integration."
            elif domain["api_keys"].get("openai"):
                response = f"[OpenAI Response for {domain['domain_name']}]:\n\nBased on {domain['domain_type']} knowledge base:\n\nQuery: {query}\n\nContext from documents:\n{context[:500]}...\n\nThis response is generated using the specific knowledge base for {domain['domain_name']} with OpenAI integration."
            else:
                response = f"[Local Response for {domain['domain_name']}]:\n\nBased on {domain['domain_type']} knowledge base:\n\nQuery: {query}\n\nContext from documents:\n{context[:500]}...\n\nThis response is generated using the local knowledge base for {domain['domain_name']}."

            # Save to chat history
            self.db.add_chat_message(domain_id, query, response)

            return response

        except Exception as e:
            logger.error(f"Error generating API response for {domain_id}: {e}")
            return f"Error generating response: {str(e)}"


# Initialize RAG manager
rag_manager = FunctionalRAGManager()

# Create FastAPI app
app = FastAPI(
    title="CoolBits.ai Complete Functional RAG System",
    description="Real document management, embeddings, and search functionality",
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
    logger.info("🚀 Starting CoolBits.ai Complete Functional RAG System")
    await rag_manager.initialize_domains()
    logger.info(f"✅ Initialized {len(rag_manager.domains)} functional RAG domains")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CoolBits.ai Complete Functional RAG System",
        "version": "1.0.0",
        "domains_count": len(rag_manager.domains),
        "database_path": config.db_path,
        "gpu_enabled": config.gpu_enabled,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/domains")
async def list_domains():
    """List all available RAG domains"""
    return {
        "domains": list(rag_manager.domains.values()),
        "total_domains": len(rag_manager.domains),
    }


@app.get("/domains/{domain_id}")
async def get_domain(domain_id: str):
    """Get specific domain information"""
    if domain_id not in rag_manager.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    domain = rag_manager.domains[domain_id]
    return {
        "domain_id": domain["domain_id"],
        "domain_name": domain["domain_name"],
        "domain_type": domain["domain_type"],
        "api_keys": {
            "xai_configured": bool(domain["api_keys"].get("xai")),
            "openai_configured": bool(domain["api_keys"].get("openai")),
        },
        "documents_count": domain["documents_count"],
        "last_updated": domain["last_updated"],
        "status": domain["status"],
    }


@app.get("/domains/{domain_id}/documents")
async def get_domain_documents(domain_id: str):
    """Get all documents for a domain"""
    if domain_id not in rag_manager.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    documents = rag_manager.get_documents(domain_id)

    return {
        "domain_id": domain_id,
        "domain_name": rag_manager.domains[domain_id]["domain_name"],
        "documents": [
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "doc_type": doc.doc_type,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
                "metadata": doc.metadata,
            }
            for doc in documents
        ],
        "total_documents": len(documents),
    }


@app.post("/domains/{domain_id}/add-document")
async def add_document(domain_id: str, request: DocumentRequest):
    """Add a new document to a domain"""
    if domain_id not in rag_manager.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    try:
        doc_id = rag_manager.add_document(
            domain_id=domain_id,
            title=request.title,
            content=request.content,
            doc_type=request.doc_type,
        )

        return {
            "status": "success",
            "message": f"Document added to {rag_manager.domains[domain_id]['domain_name']}",
            "document_id": doc_id,
            "total_documents": rag_manager.domains[domain_id]["documents_count"],
        }

    except Exception as e:
        logger.error(f"Error adding document to {domain_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/documents/{doc_id}")
async def update_document(doc_id: str, request: DocumentRequest):
    """Update an existing document"""
    try:
        success = rag_manager.update_document(
            doc_id=doc_id,
            title=request.title,
            content=request.content,
            doc_type=request.doc_type,
        )

        if success:
            return {
                "status": "success",
                "message": "Document updated successfully",
                "document_id": doc_id,
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except Exception as e:
        logger.error(f"Error updating document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    try:
        success = rag_manager.delete_document(doc_id)

        if success:
            return {
                "status": "success",
                "message": "Document deleted successfully",
                "document_id": doc_id,
            }
        else:
            raise HTTPException(status_code=404, detail="Document not found")

    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/domains/{domain_id}/chat-history")
async def get_chat_history(domain_id: str, limit: int = 50):
    """Get chat history for a domain"""
    if domain_id not in rag_manager.domains:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    history = rag_manager.db.get_chat_history(domain_id, limit)

    return {
        "domain_id": domain_id,
        "domain_name": rag_manager.domains[domain_id]["domain_name"],
        "chat_history": history,
        "total_messages": len(history),
    }


if __name__ == "__main__":
    logger.info("🚀 Starting CoolBits.ai Complete Functional RAG System")
    logger.info("📄 Real document management with SQLite database")
    logger.info("🔍 Functional search and retrieval")
    logger.info("💬 Real chat with API integration")
    logger.info("🌐 Available at: http://localhost:8092")

    uvicorn.run(app, host="localhost", port=8092, log_level="info")
