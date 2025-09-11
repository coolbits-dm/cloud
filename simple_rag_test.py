#!/usr/bin/env python3
"""
🚀 CoolBits.ai Local RAG System - Simple Test Version
GPU-accelerated RAG system for RTX 2060

Author: oCopilot (oCursor)
Date: September 5, 2025
"""

import torch
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="CoolBits.ai Local RAG System", version="1.0.0")

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
    gpu_available = torch.cuda.is_available()
    gpu_info = {}

    if gpu_available:
        gpu_info = {
            "device_name": torch.cuda.get_device_name(0),
            "total_memory_gb": torch.cuda.get_device_properties(0).total_memory
            / (1024**3),
            "cuda_version": torch.version.cuda,
        }

    return {
        "status": "healthy",
        "gpu_available": gpu_available,
        "gpu_info": gpu_info,
        "pytorch_version": torch.__version__,
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CoolBits.ai Local RAG System",
        "status": "running",
        "gpu_available": torch.cuda.is_available(),
        "endpoints": {"health": "/health", "docs": "/docs"},
    }


if __name__ == "__main__":
    logger.info("🚀 Starting CoolBits.ai Local RAG System")
    logger.info(f"GPU Available: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        logger.info(f"GPU: {torch.cuda.get_device_name(0)}")
        logger.info(
            f"Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB"
        )

    uvicorn.run(app, host="localhost", port=8087, log_level="info")
