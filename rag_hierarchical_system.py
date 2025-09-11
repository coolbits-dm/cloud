#!/usr/bin/env python3
"""
🤖 CoolBits.ai RAG Categories System
Advanced RAG system for organizing AI discussions by categories

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
import json
import logging
import asyncio
import sqlite3
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid
import re

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

    # Main categories with display names and subcategories
    categories: Dict[str, Dict[str, Any]] = {
        "u-rag": {
            "display_name": "User RAG",
            "description": "User-focused RAG - Personal user experience, interface, and user-related content",
            "subcategories": {
                "social": {
                    "display_name": "Social RAG",
                    "description": "Social media platforms and interactions",
                    "items": {
                        "facebook": "Facebook RAG",
                        "tiktok": "TikTok RAG",
                        "twitter": "X (Twitter) RAG",
                        "linkedin": "LinkedIn RAG",
                        "youtube": "YouTube RAG",
                        "instagram": "Instagram RAG",
                        "discord": "Discord RAG",
                        "telegram": "Telegram RAG",
                    },
                },
                "email": {
                    "display_name": "Email RAG",
                    "description": "Email platforms and communication",
                    "items": {
                        "gmail": "Gmail RAG",
                        "outlook": "Outlook RAG",
                        "personal": "Personal Email RAG",
                        "business": "Business Email RAG",
                    },
                },
                "personal_ai": {
                    "display_name": "Personal AI RAG",
                    "description": "Personal AI assistants and tools",
                    "items": {
                        "chatgpt": "ChatGPT Personal RAG",
                        "grok": "Grok Personal RAG",
                        "claude": "Claude Personal RAG",
                        "gemini": "Gemini Personal RAG",
                        "copilot": "Microsoft Copilot RAG",
                    },
                },
                "productivity": {
                    "display_name": "Productivity RAG",
                    "description": "Personal productivity tools and apps",
                    "items": {
                        "notion": "Notion RAG",
                        "obsidian": "Obsidian RAG",
                        "todoist": "Todoist RAG",
                        "calendar": "Calendar RAG",
                        "notes": "Notes RAG",
                    },
                },
            },
        },
        "b-rag": {
            "display_name": "Business RAG",
            "description": "Business strategy, operations, and business intelligence",
            "subcategories": {
                "channels": {
                    "display_name": "Marketing Channels RAG",
                    "description": "Advertising and marketing channels",
                    "items": {
                        "google_ads": "Google Ads RAG",
                        "meta_ads": "Meta Ads RAG",
                        "tiktok_ads": "TikTok Ads RAG",
                        "linkedin_ads": "LinkedIn Ads RAG",
                        "twitter_ads": "X Ads RAG",
                        "youtube_ads": "YouTube Ads RAG",
                        "bing_ads": "Bing Ads RAG",
                        "pinterest_ads": "Pinterest Ads RAG",
                    },
                },
                "business_tools": {
                    "display_name": "Business Tools RAG",
                    "description": "Google and other business tools",
                    "items": {
                        "ga4": "Google Analytics 4 RAG",
                        "gsc": "Google Search Console RAG",
                        "gmb": "Google My Business RAG",
                        "gads": "Google Ads Manager RAG",
                        "gtm": "Google Tag Manager RAG",
                        "gds": "Google Data Studio RAG",
                        "sheets": "Google Sheets RAG",
                        "slides": "Google Slides RAG",
                        "docs": "Google Docs RAG",
                        "drive": "Google Drive RAG",
                    },
                },
                "seo": {
                    "display_name": "SEO RAG",
                    "description": "Search Engine Optimization tools and strategies",
                    "items": {
                        "semrush": "SEMrush RAG",
                        "ahrefs": "Ahrefs RAG",
                        "moz": "Moz RAG",
                        "screaming_frog": "Screaming Frog RAG",
                        "gtmetrix": "GTmetrix RAG",
                        "pagespeed": "PageSpeed Insights RAG",
                        "keyword_tools": "Keyword Research RAG",
                        "competitor_analysis": "Competitor Analysis RAG",
                    },
                },
                "analytics": {
                    "display_name": "Analytics RAG",
                    "description": "Business analytics and reporting",
                    "items": {
                        "mixpanel": "Mixpanel RAG",
                        "amplitude": "Amplitude RAG",
                        "hotjar": "Hotjar RAG",
                        "crazy_egg": "Crazy Egg RAG",
                        "tableau": "Tableau RAG",
                        "power_bi": "Power BI RAG",
                        "looker": "Looker RAG",
                    },
                },
                "crm": {
                    "display_name": "CRM RAG",
                    "description": "Customer Relationship Management",
                    "items": {
                        "salesforce": "Salesforce RAG",
                        "hubspot": "HubSpot RAG",
                        "pipedrive": "Pipedrive RAG",
                        "zoho": "Zoho CRM RAG",
                        "monday": "Monday.com RAG",
                        "asana": "Asana RAG",
                        "trello": "Trello RAG",
                    },
                },
            },
        },
        "a-rag": {
            "display_name": "Agency RAG",
            "description": "Agency operations, client management, and agency-specific content",
            "subcategories": {
                "client_management": {
                    "display_name": "Client Management RAG",
                    "description": "Client relationship and project management",
                    "items": {
                        "client_onboarding": "Client Onboarding RAG",
                        "project_management": "Project Management RAG",
                        "communication": "Client Communication RAG",
                        "reporting": "Client Reporting RAG",
                        "billing": "Billing & Invoicing RAG",
                        "contracts": "Contracts RAG",
                    },
                },
                "team_management": {
                    "display_name": "Team Management RAG",
                    "description": "Internal team operations and management",
                    "items": {
                        "hr": "HR Management RAG",
                        "recruitment": "Recruitment RAG",
                        "training": "Team Training RAG",
                        "performance": "Performance Management RAG",
                        "workflows": "Workflow Management RAG",
                        "collaboration": "Team Collaboration RAG",
                    },
                },
                "agency_tools": {
                    "display_name": "Agency Tools RAG",
                    "description": "Specialized agency software and tools",
                    "items": {
                        "figma": "Figma RAG",
                        "adobe": "Adobe Creative Suite RAG",
                        "canva": "Canva RAG",
                        "slack": "Slack RAG",
                        "zoom": "Zoom RAG",
                        "teams": "Microsoft Teams RAG",
                        "jira": "Jira RAG",
                        "confluence": "Confluence RAG",
                    },
                },
                "specializations": {
                    "display_name": "Agency Specializations RAG",
                    "description": "Different agency service areas",
                    "items": {
                        "digital_marketing": "Digital Marketing RAG",
                        "web_development": "Web Development RAG",
                        "branding": "Branding RAG",
                        "content_creation": "Content Creation RAG",
                        "social_media": "Social Media Management RAG",
                        "ppc": "PPC Management RAG",
                        "seo_services": "SEO Services RAG",
                        "email_marketing": "Email Marketing RAG",
                    },
                },
            },
        },
        "d-rag": {
            "display_name": "Development RAG",
            "description": "Technical development, code, and development processes",
            "subcategories": {
                "programming": {
                    "display_name": "Programming RAG",
                    "description": "Programming languages and frameworks",
                    "items": {
                        "python": "Python RAG",
                        "javascript": "JavaScript RAG",
                        "typescript": "TypeScript RAG",
                        "react": "React RAG",
                        "vue": "Vue.js RAG",
                        "angular": "Angular RAG",
                        "nodejs": "Node.js RAG",
                        "django": "Django RAG",
                        "flask": "Flask RAG",
                        "fastapi": "FastAPI RAG",
                    },
                },
                "devops": {
                    "display_name": "DevOps RAG",
                    "description": "Development operations and infrastructure",
                    "items": {
                        "docker": "Docker RAG",
                        "kubernetes": "Kubernetes RAG",
                        "aws": "AWS RAG",
                        "azure": "Azure RAG",
                        "gcp": "Google Cloud RAG",
                        "terraform": "Terraform RAG",
                        "jenkins": "Jenkins RAG",
                        "github_actions": "GitHub Actions RAG",
                        "ci_cd": "CI/CD RAG",
                    },
                },
                "databases": {
                    "display_name": "Databases RAG",
                    "description": "Database systems and management",
                    "items": {
                        "postgresql": "PostgreSQL RAG",
                        "mysql": "MySQL RAG",
                        "mongodb": "MongoDB RAG",
                        "redis": "Redis RAG",
                        "elasticsearch": "Elasticsearch RAG",
                        "sqlite": "SQLite RAG",
                        "firebase": "Firebase RAG",
                        "supabase": "Supabase RAG",
                    },
                },
                "ai_ml": {
                    "display_name": "AI/ML RAG",
                    "description": "Artificial Intelligence and Machine Learning",
                    "items": {
                        "tensorflow": "TensorFlow RAG",
                        "pytorch": "PyTorch RAG",
                        "openai": "OpenAI API RAG",
                        "huggingface": "Hugging Face RAG",
                        "langchain": "LangChain RAG",
                        "vector_dbs": "Vector Databases RAG",
                        "embeddings": "Embeddings RAG",
                        "llms": "Large Language Models RAG",
                    },
                },
                "testing": {
                    "display_name": "Testing RAG",
                    "description": "Software testing and quality assurance",
                    "items": {
                        "unit_testing": "Unit Testing RAG",
                        "integration_testing": "Integration Testing RAG",
                        "e2e_testing": "End-to-End Testing RAG",
                        "pytest": "Pytest RAG",
                        "jest": "Jest RAG",
                        "cypress": "Cypress RAG",
                        "selenium": "Selenium RAG",
                        "performance_testing": "Performance Testing RAG",
                    },
                },
            },
        },
    }


config = RAGConfig()


# Data models
class Document(BaseModel):
    id: str
    title: str
    content: str
    category: str
    subcategory: str
    item: str
    source: str
    created_at: str
    metadata: Dict[str, Any]


class RAGCategory(BaseModel):
    name: str
    display_name: str
    description: str
    document_count: int
    last_updated: str
    subcategories: Dict[str, Any]


# Database setup
def init_database():
    """Initialize SQLite database for advanced RAG system"""
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    # Create documents table with hierarchical structure
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT NOT NULL,
            subcategory TEXT NOT NULL,
            item TEXT NOT NULL,
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
            display_name TEXT NOT NULL,
            description TEXT NOT NULL,
            document_count INTEGER DEFAULT 0,
            last_updated TEXT NOT NULL,
            subcategories TEXT NOT NULL
        )
    """
    )

    # Insert categories with hierarchical structure
    for category_key, category_data in config.categories.items():
        cursor.execute(
            """
            INSERT OR IGNORE INTO categories (name, display_name, description, document_count, last_updated, subcategories)
            VALUES (?, ?, ?, 0, ?, ?)
        """,
            (
                category_key,
                category_data["display_name"],
                category_data["description"],
                datetime.now().isoformat(),
                json.dumps(category_data["subcategories"]),
            ),
        )

    conn.commit()
    conn.close()
    logger.info("✅ Advanced RAG database initialized with hierarchical structure")


# Initialize database
init_database()

# FastAPI app
app = FastAPI(
    title="CoolBits.ai RAG Categories System",
    description="Hierarchical RAG system with main categories and detailed subcategories",
    version="2.0.0",
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
        doc = Document(
            id=row[0],
            title=row[1],
            content=row[2],
            category=row[3],
            subcategory=row[4],
            item=row[5],
            source=row[6],
            created_at=row[7],
            metadata=json.loads(row[8]),
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
        cat = RAGCategory(
            name=row[0],
            display_name=row[1],
            description=row[2],
            document_count=row[3],
            last_updated=row[4],
            subcategories=json.loads(row[5]),
        )
        categories[cat.name] = cat

    conn.close()
    logger.info(f"✅ Loaded {len(categories)} categories from database")


# Load data on startup
load_documents_from_db()
load_categories_from_db()


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "CoolBits.ai RAG Categories System",
        "version": "2.0.0",
        "status": "healthy",
        "total_documents": len(documents),
        "total_categories": len(categories),
        "categories": {cat.name: cat.display_name for cat in categories.values()},
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CoolBits.ai RAG Categories System",
        "version": "2.0.0",
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
    """Get all RAG categories with hierarchical structure"""
    return {
        "categories": list(categories.values()),
        "total_categories": len(categories),
        "hierarchical_structure": config.categories,
    }


@app.get("/api/categories/{category_name}")
async def get_category(category_name: str):
    """Get specific category with documents and subcategories"""
    if category_name not in categories:
        raise HTTPException(
            status_code=404, detail=f"Category {category_name} not found"
        )

    category_docs = [doc for doc in documents.values() if doc.category == category_name]

    return {
        "category": categories[category_name],
        "documents": category_docs,
        "document_count": len(category_docs),
        "subcategories": categories[category_name].subcategories,
    }


@app.get("/api/categories/{category_name}/{subcategory_name}")
async def get_subcategory(category_name: str, subcategory_name: str):
    """Get specific subcategory with documents"""
    if category_name not in categories:
        raise HTTPException(
            status_code=404, detail=f"Category {category_name} not found"
        )

    if subcategory_name not in categories[category_name].subcategories:
        raise HTTPException(
            status_code=404, detail=f"Subcategory {subcategory_name} not found"
        )

    subcategory_docs = [
        doc
        for doc in documents.values()
        if doc.category == category_name and doc.subcategory == subcategory_name
    ]

    return {
        "category": category_name,
        "subcategory": subcategory_name,
        "subcategory_info": categories[category_name].subcategories[subcategory_name],
        "documents": subcategory_docs,
        "document_count": len(subcategory_docs),
    }


class DocumentCreate(BaseModel):
    title: str
    content: str
    category: str
    subcategory: str
    item: str
    source: str = "manual"
    metadata: str = "{}"


class TrainingDiscussion(BaseModel):
    discussion_content: str
    session_title: str
    category: str = "b-rag"
    subcategory: str = "business_tools"
    item: str = "general"


@app.post("/api/documents")
async def create_document(doc_data: DocumentCreate):
    """Create a new document with hierarchical structure"""
    if doc_data.category not in categories:
        raise HTTPException(
            status_code=400, detail=f"Category {doc_data.category} not found"
        )

    if doc_data.subcategory not in categories[doc_data.category].subcategories:
        raise HTTPException(
            status_code=400, detail=f"Subcategory {doc_data.subcategory} not found"
        )

    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title=doc_data.title,
        content=doc_data.content,
        category=doc_data.category,
        subcategory=doc_data.subcategory,
        item=doc_data.item,
        source=doc_data.source,
        created_at=datetime.now().isoformat(),
        metadata=json.loads(doc_data.metadata),
    )

    # Save to database
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (id, title, content, category, subcategory, item, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            doc.subcategory,
            doc.item,
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

    logger.info(
        f"✅ Created document {doc_id} in {doc_data.category}/{doc_data.subcategory}/{doc_data.item}"
    )

    return {"document": doc, "status": "created"}


@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    category: str = "u-rag",
    subcategory: str = "social",
    item: str = "facebook",
    title: str = None,
):
    """Upload a document file with hierarchical structure"""
    if category not in categories:
        raise HTTPException(status_code=400, detail=f"Category {category} not found")

    if subcategory not in categories[category].subcategories:
        raise HTTPException(
            status_code=400, detail=f"Subcategory {subcategory} not found"
        )

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
        subcategory=subcategory,
        item=item,
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
        INSERT INTO documents (id, title, content, category, subcategory, item, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            doc.subcategory,
            doc.item,
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

    logger.info(f"✅ Uploaded document {doc_id} to {category}/{subcategory}/{item}")

    return {"document": doc, "status": "uploaded"}


@app.post("/api/documents/create")
async def create_document_json(request: dict):
    """Create a document from JSON data"""
    filename = request.get("filename", "untitled")
    content = request.get("content", "")
    category = request.get("category", "u-rag")
    subcategory = request.get("subcategory", "social")
    item = request.get("item", "general")
    source = request.get("source", "manual")

    if category not in categories:
        raise HTTPException(status_code=400, detail=f"Category {category} not found")

    if subcategory not in categories[category].subcategories:
        raise HTTPException(
            status_code=400, detail=f"Subcategory {subcategory} not found"
        )

    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        title=filename,
        content=content,
        category=category,
        subcategory=subcategory,
        item=item,
        source=f"{source}:{filename}",
        created_at=datetime.now().isoformat(),
        metadata={
            "filename": filename,
            "content_length": len(content),
            "created_time": datetime.now().isoformat(),
        },
    )

    # Save to database
    conn = sqlite3.connect("rag_system.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO documents (id, title, content, category, subcategory, item, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            doc.subcategory,
            doc.item,
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

    logger.info(f"✅ Created document {doc_id} in {category}/{subcategory}/{item}")

    return {"document": doc, "status": "created"}


@app.get("/api/documents")
async def get_documents(
    category: str = None, subcategory: str = None, item: str = None, limit: int = 100
):
    """Get documents with optional filtering by category, subcategory, or item"""
    docs = list(documents.values())

    if category:
        docs = [doc for doc in docs if doc.category == category]
    if subcategory:
        docs = [doc for doc in docs if doc.subcategory == subcategory]
    if item:
        docs = [doc for doc in docs if doc.item == item]

    docs = docs[:limit]

    return {
        "documents": docs,
        "total_documents": len(docs),
        "filters": {"category": category, "subcategory": subcategory, "item": item},
    }


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

    logger.info(
        f"✅ Deleted document {doc_id} from {category}/{doc.subcategory}/{doc.item}"
    )

    return {"status": "deleted", "document_id": doc_id}


# Special endpoint for processing training discussions
@app.post("/api/process-training-discussion")
async def process_training_discussion(discussion_data: TrainingDiscussion):
    """Process a training discussion and save it to RAG"""
    if discussion_data.category not in categories:
        raise HTTPException(
            status_code=400, detail=f"Category {discussion_data.category} not found"
        )

    if (
        discussion_data.subcategory
        not in categories[discussion_data.category].subcategories
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Subcategory {discussion_data.subcategory} not found",
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
        subcategory=discussion_data.subcategory,
        item=discussion_data.item,
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
        INSERT INTO documents (id, title, content, category, subcategory, item, source, created_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            doc.id,
            doc.title,
            doc.content,
            doc.category,
            doc.subcategory,
            doc.item,
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
        f"✅ Processed training discussion {doc_id} in {discussion_data.category}/{discussion_data.subcategory}/{discussion_data.item}"
    )

    return {"document": doc, "status": "processed", "metadata": doc.metadata}


if __name__ == "__main__":
    logger.info("🤖 Starting CoolBits.ai RAG Categories System")
    logger.info(
        "📚 Hierarchical RAG system with main categories and detailed subcategories"
    )
    logger.info("🎯 Categories: User RAG, Business RAG, Agency RAG, Development RAG")
    logger.info(
        "📊 Subcategories: Social, Email, AI, Channels, Tools, SEO, Programming, DevOps, etc."
    )
    logger.info(f"🌐 Available at: http://localhost:{config.base_port}")

    uvicorn.run(app, host="0.0.0.0", port=config.base_port)
