#!/usr/bin/env python3
"""
🧠 CoolBits.ai Simple Functional RAG System
Working RAG system with real document management

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
import json
import logging
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


# Data models
class Document(BaseModel):
    id: str
    domain_id: str
    title: str
    content: str
    doc_type: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}


class DocumentRequest(BaseModel):
    domain_id: str
    title: str
    content: str
    doc_type: str = "general"
    metadata: Dict[str, Any] = {}


class QueryRequest(BaseModel):
    domain_id: str
    query: str
    max_results: int = 5


# Database setup
class SimpleRAGDatabase:
    def __init__(self, db_path: str = "simple_rag.db"):
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
                metadata TEXT DEFAULT '{}'
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()
        logger.info("✅ Database initialized successfully")

    def add_domain(
        self, domain_id: str, name: str, domain_type: str, description: str = ""
    ):
        """Add a new domain"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR REPLACE INTO domains (id, name, domain_type, description)
            VALUES (?, ?, ?, ?)
        """,
            (domain_id, name, domain_type, description),
        )

        conn.commit()
        conn.close()

    def get_domains(self) -> List[Dict[str, Any]]:
        """Get all domains"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT d.id, d.name, d.domain_type, d.description, d.created_at,
                   COUNT(doc.id) as doc_count
            FROM domains d
            LEFT JOIN documents doc ON d.id = doc.domain_id
            GROUP BY d.id, d.name, d.domain_type, d.description, d.created_at
            ORDER BY d.created_at DESC
        """
        )

        rows = cursor.fetchall()
        conn.close()

        domains = []
        for row in rows:
            domains.append(
                {
                    "domain_id": row[0],
                    "domain_name": row[1],
                    "domain_type": row[2],
                    "description": row[3],
                    "created_at": row[4],
                    "documents_count": row[5],
                    "status": "active",
                }
            )

        return domains

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
            SELECT id, domain_id, title, content, doc_type, created_at, updated_at, metadata
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
                metadata=json.loads(row[7]) if row[7] else {},
            )
            documents.append(doc)

        return documents

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Get specific document"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, domain_id, title, content, doc_type, created_at, updated_at, metadata
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
                metadata=json.loads(row[7]) if row[7] else {},
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

    def search_documents(
        self, domain_id: str, query: str, max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search documents using text matching"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, content, doc_type, created_at, updated_at
            FROM documents 
            WHERE domain_id = ? AND (
                title LIKE ? OR content LIKE ?
            )
            ORDER BY created_at DESC
        """,
            (domain_id, f"%{query}%", f"%{query}%"),
        )

        rows = cursor.fetchall()
        conn.close()

        results = []
        for row in rows:
            results.append(
                {
                    "document_id": row[0],
                    "title": row[1],
                    "content": row[2][:200] + "..." if len(row[2]) > 200 else row[2],
                    "doc_type": row[3],
                    "created_at": row[4],
                    "updated_at": row[5],
                    "relevance_score": 1.0,  # Simple matching
                }
            )

        return results[:max_results]


# Global RAG manager
class SimpleRAGManager:
    def __init__(self):
        self.db = SimpleRAGDatabase()
        self.init_test_domains()

    def init_test_domains(self):
        """Initialize test domains"""
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

        logger.info(f"✅ Initialized {len(test_domains)} test domains")

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
        """Search documents"""
        return self.db.search_documents(domain_id, query, max_results)

    def get_domains(self) -> List[Dict[str, Any]]:
        """Get all domains"""
        return self.db.get_domains()


# Initialize RAG manager
rag_manager = SimpleRAGManager()

# Create FastAPI app
app = FastAPI(
    title="CoolBits.ai Simple Functional RAG System",
    description="Working RAG system with real document management",
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
    return {
        "status": "healthy",
        "service": "CoolBits.ai Simple Functional RAG System",
        "version": "1.0.0",
        "domains_count": len(domains),
        "database_path": "simple_rag.db",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/domains")
async def list_domains():
    """List all available RAG domains"""
    domains = rag_manager.get_domains()
    return {"domains": domains, "total_domains": len(domains)}


@app.get("/domains/{domain_id}")
async def get_domain(domain_id: str):
    """Get specific domain information"""
    domains = rag_manager.get_domains()
    domain = next((d for d in domains if d["domain_id"] == domain_id), None)

    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

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
            }
            for doc in documents
        ],
        "total_documents": len(documents),
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
        )

        return {
            "status": "success",
            "message": f"Document added to {domain['domain_name']}",
            "document_id": doc_id,
            "total_documents": len(rag_manager.get_documents(domain_id)),
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


@app.post("/domains/{domain_id}/search")
async def search_documents(domain_id: str, request: QueryRequest):
    """Search documents in a domain"""
    domains = rag_manager.get_domains()
    domain = next((d for d in domains if d["domain_id"] == domain_id), None)

    if not domain:
        raise HTTPException(status_code=404, detail=f"Domain {domain_id} not found")

    try:
        results = rag_manager.search_documents(
            domain_id, request.query, request.max_results
        )

        return {
            "domain_id": domain_id,
            "domain_name": domain["domain_name"],
            "query": request.query,
            "results": results,
            "total_results": len(results),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error searching documents in {domain_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("🚀 Starting CoolBits.ai Simple Functional RAG System")
    logger.info("📄 Real document management with SQLite database")
    logger.info("🔍 Functional search and retrieval")
    logger.info("🌐 Available at: http://localhost:8093")

    uvicorn.run(app, host="localhost", port=8093, log_level="info")
