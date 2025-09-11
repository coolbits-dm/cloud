#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai Main Bridge Service - Port 8100
SC COOL BITS SRL - Simple bridge service
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="CoolBits.ai Main Bridge", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>CoolBits.ai Main Bridge</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            margin: 0; 
            padding: 20px; 
        }}
        .container {{ 
            max-width: 800px; 
            margin: 0 auto; 
            text-align: center; 
        }}
        .header {{ 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 20px; 
        }}
        .services {{ 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
        }}
        .service-item {{
            background: rgba(255,255,255,0.1);
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CoolBits.ai Main Bridge</h1>
            <p>🏢 SC COOL BITS SRL | 👤 CEO: Andrei | 🤖 AI Assistant: Cursor AI Assistant</p>
            <p>📅 Contract Date: 2025-09-06 | 🌐 Port: 8100</p>
        </div>
        <div class="services">
            <h3>🌐 Available Services</h3>
            <div class="service-item">
                <strong>Main CoolBits Bridge</strong><br>
                <small>Port 8100 - Active</small>
            </div>
            <div class="service-item">
                <strong>Multi-Agent Chat System</strong><br>
                <small>Port 8101 - Ready</small>
            </div>
            <div class="service-item">
                <strong>Enhanced Multi-Agent Chat</strong><br>
                <small>Port 8102 - Ready</small>
            </div>
            <div class="service-item">
                <strong>Individual Agent Portal</strong><br>
                <small>Port 8103 - Ready</small>
            </div>
            <div class="service-item">
                <strong>Cursor Root Console</strong><br>
                <small>Port 8104 - Ready</small>
            </div>
            <div class="service-item">
                <strong>Complete Dashboard</strong><br>
                <small>Port 8105 - Ready</small>
            </div>
            <div class="service-item">
                <strong>Google Cloud Agent</strong><br>
                <small>Port 8106 - Ready</small>
            </div>
            <p style="margin-top: 20px;">
                <strong>Status:</strong> Active | 
                <strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
    </div>
</body>
</html>
    """


@app.get("/api/status")
async def status():
    return {
        "service": "Main CoolBits Bridge",
        "company": "SC COOL BITS SRL",
        "ceo": "Andrei",
        "ai_assistant": "Cursor AI Assistant",
        "contract_date": "2025-09-06",
        "port": 8100,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "port": 8100}


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 COOLBITS.AI MAIN BRIDGE SERVICE")
    print("🏢 SC COOL BITS SRL - Port 8100")
    print("=" * 80)
    print("👤 CEO: Andrei")
    print("🤖 AI Assistant: Cursor AI Assistant")
    print("📅 Contract Date: 2025-09-06")
    print("🌐 Port: 8100")
    print("=" * 80)
    print("🔗 Main Bridge URL: http://localhost:8100")
    print("📋 API Status: http://localhost:8100/api/status")
    print("=" * 80)
    print("🌐 Starting Main Bridge on port 8100")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8100, log_level="info")
