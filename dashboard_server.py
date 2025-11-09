#!/usr/bin/env python3
"""
🌐 CoolBits.ai Dashboard Server
Serves the complete dashboard with all panels

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="CoolBits.ai Dashboard Server",
    description="Complete dashboard with all panels and systems",
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
async def dashboard():
    """Serve the main dashboard"""
    return FileResponse("coolbits_dashboard.html")


@app.get("/dashboard")
async def dashboard_alt():
    """Alternative dashboard route"""
    return FileResponse("coolbits_dashboard.html")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CoolBits.ai Dashboard Server",
        "version": "1.0.0",
        "endpoints": {"dashboard": "/", "health": "/health", "static": "/public"},
    }


if __name__ == "__main__":
    logger.info("🚀 Starting CoolBits.ai Dashboard Server")
    logger.info("📊 Serving complete dashboard with all panels")
    logger.info("🌐 Dashboard available at: http://localhost:8089")

    uvicorn.run(app, host="localhost", port=8089, log_level="info")
