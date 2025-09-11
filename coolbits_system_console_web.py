#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai System Console Web Interface
SC COOL BITS SRL - Web interface for system monitoring
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime
import subprocess
import psutil
import json

app = FastAPI(title="CoolBits.ai System Console", version="1.0.0")


def get_nvidia_info():
    """Get nVidia GPU information"""
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,utilization.gpu,temperature.gpu,power.draw",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            gpu_info = result.stdout.strip().split(", ")
            return {
                "name": gpu_info[0],
                "memory_total": int(gpu_info[1]),
                "memory_used": int(gpu_info[2]),
                "utilization": int(gpu_info[3]),
                "temperature": int(gpu_info[4]),
                "power_draw": float(gpu_info[5]) if gpu_info[5] != "N/A" else 0,
                "status": "active",
            }
        else:
            return {"status": "error", "message": "nvidia-smi failed"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_cpu_info():
    """Get CPU information"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()

        return {
            "utilization": cpu_percent,
            "cores": cpu_count,
            "frequency": cpu_freq.current if cpu_freq else 0,
            "status": "active",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_memory_info():
    """Get memory information"""
    try:
        memory = psutil.virtual_memory()
        return {
            "total": memory.total // (1024**3),  # GB
            "used": memory.used // (1024**3),  # GB
            "available": memory.available // (1024**3),  # GB
            "utilization": memory.percent,
            "status": "active",
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/", response_class=HTMLResponse)
async def root():
    gpu_info = get_nvidia_info()
    cpu_info = get_cpu_info()
    memory_info = get_memory_info()

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>CoolBits.ai System Console</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            margin: 0; 
            padding: 20px; 
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
        }}
        .header {{ 
            background: rgba(255,255,255,0.1); 
            padding: 30px; 
            border-radius: 15px; 
            margin-bottom: 20px; 
            text-align: center;
        }}
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
        }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
            backdrop-filter: blur(10px);
        }}
        .card h3 {{
            color: #ffd700;
            margin-bottom: 15px;
        }}
        .status-item {{
            margin: 10px 0;
            padding: 10px;
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }}
        .status-label {{
            font-weight: bold;
            color: #4CAF50;
        }}
        .status-value {{
            float: right;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
        }}
        .gpu-progress {{ background: linear-gradient(90deg, #2196F3, #03A9F4); }}
        .cpu-progress {{ background: linear-gradient(90deg, #FF9800, #FFC107); }}
        .memory-progress {{ background: linear-gradient(90deg, #9C27B0, #E91E63); }}
        
        .refresh-btn {{
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 25px;
            cursor: pointer;
            font-weight: bold;
            margin: 10px 0;
        }}
        .refresh-btn:hover {{
            background: #45a049;
        }}
        
        .timestamp {{
            text-align: center;
            margin-top: 20px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖥️ CoolBits.ai System Console</h1>
            <p>🏢 SC COOL BITS SRL | 👤 CEO: Andrei | 🤖 AI Assistant: Cursor AI Assistant</p>
            <p>📅 Contract Date: 2025-09-06 | 🌐 Port: 8100</p>
            <button class="refresh-btn" onclick="location.reload()">🔄 Refresh Status</button>
        </div>
        
        <div class="main-content">
            <div class="card">
                <h3>🎮 NVIDIA GPU Status</h3>
                <div class="status-item">
                    <span class="status-label">Name:</span>
                    <span class="status-value">{gpu_info.get('name', 'N/A')}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Memory:</span>
                    <span class="status-value">{gpu_info.get('memory_used', 0)}MB / {gpu_info.get('memory_total', 0)}MB</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Utilization:</span>
                    <span class="status-value">{gpu_info.get('utilization', 0)}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill gpu-progress" style="width: {gpu_info.get('utilization', 0)}%"></div>
                </div>
                <div class="status-item">
                    <span class="status-label">Temperature:</span>
                    <span class="status-value">{gpu_info.get('temperature', 0)}°C</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Power Draw:</span>
                    <span class="status-value">{gpu_info.get('power_draw', 0):.1f}W</span>
                </div>
            </div>
            
            <div class="card">
                <h3>💻 CPU Status</h3>
                <div class="status-item">
                    <span class="status-label">Utilization:</span>
                    <span class="status-value">{cpu_info.get('utilization', 0):.1f}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill cpu-progress" style="width: {cpu_info.get('utilization', 0)}%"></div>
                </div>
                <div class="status-item">
                    <span class="status-label">Cores:</span>
                    <span class="status-value">{cpu_info.get('cores', 0)}</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Frequency:</span>
                    <span class="status-value">{cpu_info.get('frequency', 0):.0f}MHz</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Processor:</span>
                    <span class="status-value">AMD Ryzen 7 2700X</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🧠 Memory Status</h3>
                <div class="status-item">
                    <span class="status-label">Total:</span>
                    <span class="status-value">{memory_info.get('total', 0)}GB</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Used:</span>
                    <span class="status-value">{memory_info.get('used', 0)}GB</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Available:</span>
                    <span class="status-value">{memory_info.get('available', 0)}GB</span>
                </div>
                <div class="status-item">
                    <span class="status-label">Utilization:</span>
                    <span class="status-value">{memory_info.get('utilization', 0):.1f}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill memory-progress" style="width: {memory_info.get('utilization', 0)}%"></div>
                </div>
            </div>
        </div>
        
        <div class="timestamp">
            <p>🕒 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🚀 System Ready for AI Processing with CPU + GPU</p>
        </div>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds
        setInterval(() => {{
            location.reload();
        }}, 5000);
    </script>
</body>
</html>
    """


@app.get("/api/status")
async def status():
    return {
        "service": "System Console Web Interface",
        "company": "SC COOL BITS SRL",
        "ceo": "Andrei",
        "ai_assistant": "Cursor AI Assistant",
        "contract_date": "2025-09-06",
        "port": 8100,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "nvidia_gpu": get_nvidia_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "port": 8100}


if __name__ == "__main__":
    print("=" * 80)
    print("🖥️ COOLBITS.AI SYSTEM CONSOLE WEB INTERFACE")
    print("🏢 SC COOL BITS SRL - Port 8100")
    print("=" * 80)
    print("👤 CEO: Andrei")
    print("🤖 AI Assistant: Cursor AI Assistant")
    print("📅 Contract Date: 2025-09-06")
    print("🌐 Port: 8100")
    print("=" * 80)
    print("🔗 System Console URL: http://localhost:8100")
    print("📋 API Status: http://localhost:8100/api/status")
    print("=" * 80)
    print("🌐 Starting System Console Web Interface on port 8100")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8100, log_level="info")
