#!/usr/bin/env python3
"""
🤖 CoolBits.ai RAG Categories System
Advanced RAG system for organizing AI discussions by categories

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import json
import logging
import sqlite3
from typing import Dict, List, Any
from datetime import datetime
import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Configuration
class RAGConfig(BaseModel):
    base_port: int = 8097
    max_documents: int = 1000
    categories: List[str] = [
        "u-rag",  # User
        "b-rag",  # Business
        "a-rag",  # Agency
        "d-rag",  # Development
    ]


config = RAGConfig()


# Data models
class Document(BaseModel):
    id: str
    title: str
    content: str
    category: str
    source: str
    created_at: str
    metadata: Dict[str, Any]


class RAGCategory(BaseModel):
    name: str
    description: str
    document_count: int
    last_updated: str


# Database setup
def init_database():
    """Initialize SQLite database for RAG system"""
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    # Create documents table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL,
            metadata TEXT NOT NULL
        )
    """
    )

    # Create categories table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS categories (
            name TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            document_count INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL
        )
    """
    )

    # Insert default categories with descriptions
    category_descriptions = {
        "u-rag": "User-focused RAG - User experience, interface, and user-related content",
        "b-rag": "Business RAG - Business strategy, operations, and business intelligence",
        "a-rag": "Agency RAG - Agency operations, client management, and agency-specific content",
        "d-rag": "Development RAG - Technical development, code, and development processes",
    }

    for category in config.categories:
        description = category_descriptions.get(
            category, f"RAG category for {category}"
        )
        cursor.execute(
            """
            INSERT OR IGNORE INTO categories (name, description, document_count, last_updated)
            VALUES (?, ?, 0, ?)
        """,
            (category, description, datetime.now().isoformat()),
        )

    conn.commit()
    conn.close()
    logger.info("✅ RAG database initialized")


# Initialize database
init_database()

# FastAPI app
app = FastAPI(
    title="CoolBits.ai RAG Categories System",
    description="Advanced RAG system for organizing AI discussions by categories",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8098", "http://127.0.0.1:8098", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global storage
documents: Dict[str, Document] = {}
categories: Dict[str, RAGCategory] = {}


def load_documents_from_db():
    """Load documents from database"""
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM documents")
    rows = cursor.fetchall()

    for row in rows:
        try:
            # Handle corrupted or empty JSON metadata
            metadata_str = row[6] if row[6] else "{}"
            if not metadata_str.strip():
                metadata_str = "{}"

            metadata = json.loads(metadata_str)
        except (json.JSONDecodeError, TypeError):
            # If JSON is corrupted, use empty metadata
            logger.warning(
                f"Corrupted JSON metadata for document {row[0]}, using empty metadata"
            )
            metadata = {}

        doc = Document(
            id=row[0],
            title=row[1],
            content=row[2],
            category=row[3],
            source=row[4],
            created_at=row[5],
            metadata=metadata,
        )
        documents[doc.id] = doc

    conn.close()
    logger.info(f"✅ Loaded {len(documents)} documents from database")


def load_categories_from_db():
    """Load categories from database"""
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM categories")
    rows = cursor.fetchall()

    for row in rows:
        try:
            # Handle corrupted data with proper type conversion
            name = row[0] if row[0] else "unknown"
            description = row[1] if row[1] else ""

            # Convert document_count to int, default to 0 if invalid
            try:
                document_count = int(row[2]) if row[2] else 0
            except (ValueError, TypeError):
                document_count = 0

            # Convert last_updated to string, default to current time if invalid
            try:
                last_updated = str(row[3]) if row[3] else datetime.now().isoformat()
            except (ValueError, TypeError):
                last_updated = datetime.now().isoformat()

            cat = RAGCategory(
                name=name,
                description=description,
                document_count=document_count,
                last_updated=last_updated,
            )
            categories[cat.name] = cat
        except Exception as e:
            logger.warning(
                f"Error loading category {row[0] if row[0] else 'unknown'}: {e}"
            )
            continue

    conn.close()
    logger.info(f"✅ Loaded {len(categories)} categories from database")


# Load data on startup
load_documents_from_db()
load_categories_from_db()


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint - serve web interface"""
    return FileResponse("rag_web_interface.html")


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "service": "CoolBits.ai RAG Categories System",
        "version": "1.0.0",
        "status": "healthy",
        "total_documents": len(documents),
        "total_categories": len(categories),
        "categories": list(categories.keys()),
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CoolBits.ai RAG Categories System",
        "version": "1.0.0",
        "total_documents": len(documents),
        "total_categories": len(categories),
        "timestamp": datetime.now().isoformat(),
    }


@app.options("/api/documents/upload")
async def options_upload():
    """Handle preflight requests for document upload"""
    return {"status": "ok"}


@app.options("/api/documents")
async def options_documents():
    """Handle preflight requests for documents"""
    return {"status": "ok"}


@app.options("/api/categories")
async def options_categories():
    """Handle preflight requests for categories"""
    return {"status": "ok"}


@app.get("/api/categories")
async def get_categories():
    """Get all RAG categories"""
    return {
        "categories": list(categories.values()),
        "total_categories": len(categories),
    }


@app.get("/api/categories/{category_name}")
async def get_category(category_name: str):
    """Get specific category with documents"""
    if category_name not in categories:
        raise HTTPException(
            status_code=404, detail=f"Category {category_name} not found"
        )

    category_docs = [doc for doc in documents.values() if doc.category == category_name]

    return {
        "category": categories[category_name],
        "documents": category_docs,
        "document_count": len(category_docs),
    }


class DocumentCreate(BaseModel):
    title: str
    content: str
    category: str
    source: str = "manual"
    metadata: str = "{}"


class TrainingDiscussion(BaseModel):
    discussion_content: str
    session_title: str
    category: str = "b-rag"  # Default to Business RAG for training discussions


@app.post("/api/documents")
async def create_document(doc_data: DocumentCreate):
    """Create a new document"""
    if doc_data.category not in categories:
        raise HTTPException(
            status_code=400, detail=f"Category {doc_data.category} not found"
        )

    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title=doc_data.title,
        content=doc_data.content,
        category=doc_data.category,
        source=doc_data.source,
        created_at=datetime.now().isoformat(),
        metadata=json.loads(doc_data.metadata),
    )

    # Save to database
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (id, title, content, category, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            doc.source,
            doc.created_at,
            json.dumps(doc.metadata),
        ),
    )

    # Update category count
    cursor.execute(
        """
        UPDATE categories SET document_count = document_count + 1, last_updated = ?
        WHERE name = ?
    """,
        (datetime.now().isoformat(), doc_data.category),
    )

    conn.commit()
    conn.close()

    documents[doc_id] = doc
    categories[doc_data.category].document_count += 1
    categories[doc_data.category].last_updated = datetime.now().isoformat()

    logger.info(f"✅ Created document {doc_id} in category {doc_data.category}")

    return {"document": doc, "status": "created"}


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...), category: str = "b-rag", title: str = None
):
    """Upload a document file"""
    if category not in categories:
        raise HTTPException(status_code=400, detail=f"Category {category} not found")

    content = await file.read()
    content_str = content.decode("utf-8")

    if not title:
        title = (
            file.filename or f"Document {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title=title,
        content=content_str,
        category=category,
        source=f"upload:{file.filename}",
        created_at=datetime.now().isoformat(),
        metadata={
            "filename": file.filename,
            "file_size": len(content),
            "upload_time": datetime.now().isoformat(),
        },
    )

    # Save to database
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (id, title, content, category, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            doc.source,
            doc.created_at,
            json.dumps(doc.metadata),
        ),
    )

    # Update category count
    cursor.execute(
        """
        UPDATE categories SET document_count = document_count + 1, last_updated = ?
        WHERE name = ?
    """,
        (datetime.now().isoformat(), category),
    )

    conn.commit()
    conn.close()

    documents[doc_id] = doc
    categories[category].document_count += 1
    categories[category].last_updated = datetime.now().isoformat()

    logger.info(f"✅ Uploaded document {doc_id} to category {category}")

    return {"document": doc, "status": "uploaded"}


@app.get("/api/documents")
async def get_documents(category: str = None, limit: int = 100):
    """Get documents, optionally filtered by category"""
    if category and category not in categories:
        raise HTTPException(status_code=400, detail=f"Category {category} not found")

    docs = list(documents.values())
    if category:
        docs = [doc for doc in docs if doc.category == category]

    docs = docs[:limit]

    return {"documents": docs, "total_documents": len(docs), "category": category}


@app.get("/api/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get specific document"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    return {"document": documents[doc_id]}


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """Delete a document"""
    if doc_id not in documents:
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")

    doc = documents[doc_id]
    category = doc.category

    # Remove from database
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))

    # Update category count
    cursor.execute(
        """
        UPDATE categories SET document_count = document_count - 1, last_updated = ?
        WHERE name = ?
    """,
        (datetime.now().isoformat(), category),
    )

    conn.commit()
    conn.close()

    del documents[doc_id]
    categories[category].document_count -= 1
    categories[category].last_updated = datetime.now().isoformat()

    logger.info(f"✅ Deleted document {doc_id} from category {category}")

    return {"status": "deleted", "document_id": doc_id}


@app.post("/api/categories")
async def create_category(name: str, description: str = None):
    """Create a new RAG category"""
    if name in categories:
        raise HTTPException(status_code=400, detail=f"Category {name} already exists")

    if not description:
        description = f"RAG category for {name}"

    category = RAGCategory(
        name=name,
        description=description,
        document_count=0,
        last_updated=datetime.now().isoformat(),
    )

    # Save to database
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO categories (name, description, document_count, last_updated)
        VALUES (?, ?, ?, ?)
    """,
        (
            category.name,
            category.description,
            category.document_count,
            category.last_updated,
        ),
    )

    conn.commit()
    conn.close()

    categories[name] = category

    logger.info(f"✅ Created category {name}")

    return {"category": category, "status": "created"}


# Special endpoint for processing training discussions
@app.post("/api/process-training-discussion")
async def process_training_discussion(discussion_data: TrainingDiscussion):
    """Process a training discussion and save it to RAG"""
    if discussion_data.category not in categories:
        raise HTTPException(
            status_code=400, detail=f"Category {discussion_data.category} not found"
        )

    # Extract key information from discussion
    lines = discussion_data.discussion_content.strip().split("\n")

    # Find discussion topic
    topic = "Unknown Topic"
    for line in lines:
        if "DISCUSSION TOPIC:" in line:
            topic = line.split("DISCUSSION TOPIC:")[-1].strip()
            break

    # Extract participants
    participants = []
    for line in lines:
        if (
            line.strip()
            and not line.startswith("Characters:")
            and not line.startswith("System")
        ):
            if ":" in line and any(
                role in line for role in ["CEO", "CTO", "CFO", "COO"]
            ):
                participants.append(line.strip())

    # Create document
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title=f"{discussion_data.session_title} - {topic}",
        content=discussion_data.discussion_content,
        category=discussion_data.category,
        source="training-discussion",
        created_at=datetime.now().isoformat(),
        metadata={
            "session_title": discussion_data.session_title,
            "topic": topic,
            "participants": participants,
            "total_lines": len(lines),
            "processed_at": datetime.now().isoformat(),
        },
    )

    # Save to database
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (id, title, content, category, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            doc.source,
            doc.created_at,
            json.dumps(doc.metadata),
        ),
    )

    # Update category count
    cursor.execute(
        """
        UPDATE categories SET document_count = document_count + 1, last_updated = ?
        WHERE name = ?
    """,
        (datetime.now().isoformat(), discussion_data.category),
    )

    conn.commit()
    conn.close()

    documents[doc_id] = doc
    categories[discussion_data.category].document_count += 1
    categories[discussion_data.category].last_updated = datetime.now().isoformat()

    logger.info(
        f"✅ Processed training discussion {doc_id} in category {discussion_data.category}"
    )

    return {"document": doc, "status": "processed", "metadata": doc.metadata}


if __name__ == "__main__":
    logger.info("🤖 Starting CoolBits.ai RAG Categories System")
    logger.info("📚 Advanced RAG system for organizing AI discussions by categories")
    logger.info("🎯 Categories: AI Training, Business Data, Development, Design, etc.")
    logger.info(f"🌐 Available at: http://localhost:{config.base_port}")

    uvicorn.run(app, host="0.0.0.0", port=config.base_port)
