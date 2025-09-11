#!/usr/bin/env python3
"""
🎛️ CoolBits.ai Vertex AI Compatible RAG Administration Panel Server
Serves the Vertex AI compatible admin panel

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CoolBits.ai Vertex AI Compatible RAG Administration Panel",
    description="Administration panel for Vertex AI compatible RAG system",
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

# Mount static files
app.mount("/public", StaticFiles(directory="public"), name="public")


@app.get("/")
async def admin_panel():
    """Serve the Vertex AI compatible RAG administration panel"""
    return FileResponse("vertex_ai_admin_panel.html")


@app.get("/admin")
async def admin_panel_alt():
    """Alternative admin panel route"""
    return FileResponse("vertex_ai_admin_panel.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CoolBits.ai Vertex AI Compatible RAG Administration Panel",
        "version": "1.0.0",
        "features": [
            "Vertex AI Compatible Vector Search",
            "FAISS Indexing",
            "Real-time Embeddings",
            "Similarity Search",
            "Document Management",
            "Live Chat with Vector Enhancement",
        ],
        "vertex_ai_compatible": True,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/entities")
async def get_entities():
    """Get all RAG entities from Vertex AI system"""
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8094/domains") as resp:
                data = await resp.json()
                return data
    except Exception as e:
        logger.error(f"Error fetching entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/entity/{entity_id}")
async def get_entity(entity_id: str):
    """Get specific entity details"""
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:8094/domains/{entity_id}"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise HTTPException(status_code=404, detail="Entity not found")
    except Exception as e:
        logger.error(f"Error fetching entity {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/entity/{entity_id}/documents")
async def get_entity_documents(entity_id: str):
    """Get documents for specific entity"""
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:8094/domains/{entity_id}/documents"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise HTTPException(status_code=404, detail="Entity not found")
    except Exception as e:
        logger.error(f"Error fetching documents for {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/entity/{entity_id}/vector-search")
async def vector_search_entity(entity_id: str, search_data: Dict[str, Any]):
    """Perform vector search on specific entity"""
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://localhost:8094/domains/{entity_id}/vector-search",
                json=search_data,
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise HTTPException(status_code=400, detail="Vector search failed")
    except Exception as e:
        logger.error(f"Error performing vector search on {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/entity/{entity_id}/add-document")
async def add_document(entity_id: str, document_data: Dict[str, str]):
    """Add document to specific entity"""
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"http://localhost:8094/domains/{entity_id}/add-document",
                json=document_data,
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise HTTPException(
                        status_code=400, detail="Failed to add document"
                    )
    except Exception as e:
        logger.error(f"Error adding document to {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/entity/{entity_id}/vector-stats")
async def get_vector_stats(entity_id: str):
    """Get vector search statistics for specific entity"""
    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"http://localhost:8094/domains/{entity_id}/vector-stats"
            ) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    raise HTTPException(status_code=404, detail="Entity not found")
    except Exception as e:
        logger.error(f"Error fetching vector stats for {entity_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_system_stats():
    """Get system-wide statistics"""
    try:
        import aiohttp

        stats = {}

        async with aiohttp.ClientSession() as session:
            # Get Vertex AI RAG system stats
            async with session.get("http://localhost:8094/health") as resp:
                if resp.status == 200:
                    stats["vertex_rag"] = await resp.json()

            # Get domains count
            async with session.get("http://localhost:8094/domains") as resp:
                if resp.status == 200:
                    domains_data = await resp.json()
                    stats["domains"] = {
                        "total": len(domains_data["domains"]),
                        "active": len(
                            [
                                d
                                for d in domains_data["domains"]
                                if d["status"] == "active"
                            ]
                        ),
                    }

        return {
            "system_stats": stats,
            "vertex_ai_compatible": True,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error fetching system stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    logger.info("🎛️ Starting CoolBits.ai Vertex AI Compatible RAG Administration Panel")
    logger.info("📊 Complete GUI for managing Vertex AI compatible RAG entities")
    logger.info("🔍 Vector search with FAISS indexing")
    logger.info("💬 Live chat with vector enhancement")
    logger.info("🌐 Available at: http://localhost:8095")

    uvicorn.run(app, host="localhost", port=8095, log_level="info")
