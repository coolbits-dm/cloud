#!/usr/bin/env python3
"""
🤖 CoolBits.ai RAG Admin Panel Server
Serves the RAG admin panel HTML interface

Author: oCopilot (oCursor)
Date: September 6, 2025
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="CoolBits.ai RAG Admin Panel")


# Serve the admin panel HTML
@app.get("/")
async def serve_admin_panel():
    """Serve the RAG admin panel"""
    return FileResponse("rag_admin_panel.html")


if __name__ == "__main__":
    print("🤖 Starting CoolBits.ai RAG Admin Panel Server")
    print("📚 Serving RAG admin panel interface")
    print("🌐 Available at: http://localhost:8098")

    uvicorn.run(app, host="0.0.0.0", port=8098)
