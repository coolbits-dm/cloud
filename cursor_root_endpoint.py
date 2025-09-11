#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor AI Assistant Root Endpoint
SC COOL BITS SRL - CEO Console
Port: 8082 (Root Access)
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Cursor AI Assistant Root Endpoint",
    description="Primary technical console for SC COOL BITS SRL",
    version="1.0.0",
)


class CursorRootConsole:
    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.ai_assistant = "Cursor AI Assistant"
        self.machine = "Windows 11"
        self.base_path = r"C:\Users\andre\Desktop\coolbits"
        self.contract_date = "2025-09-06"
        self.access_level = "ROOT/CEO"
        self.port = 8082

        # 4 Main Pillars Architecture
        self.main_pillars = {
            "user": {
                "name": "User Panel",
                "icon": "👤",
                "description": "Personal AI, Social Tools, Emails, Productivity",
                "services": [
                    "personal_ai",
                    "social_tools",
                    "email_management",
                    "productivity",
                ],
            },
            "business": {
                "name": "Business Panel",
                "icon": "🏢",
                "description": "Channels, Tools, SEO, Analytics",
                "services": ["channels", "business_tools", "seo", "analytics"],
            },
            "agency": {
                "name": "Agency Panel",
                "icon": "🎯",
                "description": "Clients, Projects, Creative, Operations",
                "services": ["clients", "projects", "creative", "operations"],
            },
            "development": {
                "name": "Development Panel",
                "icon": "💻",
                "description": "Frontend, Backend, DevOps, Testing",
                "services": ["frontend", "backend", "devops", "testing"],
            },
        }

        # Services matrix
        self.services = {
            "bridge": {
                "port": 8080,
                "url": "http://localhost:8080",
                "status": "running",
            },
            "multi_agent_chat": {
                "port": 8096,
                "url": "http://localhost:8096",
                "status": "stopped",
            },
            "enhanced_multi_agent": {
                "port": 8091,
                "url": "http://localhost:8091",
                "status": "stopped",
            },
            "agent_portal": {
                "port": 8099,
                "url": "http://localhost:8099",
                "status": "stopped",
            },
            "rag_system": {
                "port": 8090,
                "url": "http://localhost:8090",
                "status": "stopped",
            },
            "rag_admin": {
                "port": 8098,
                "url": "http://localhost:8098",
                "status": "stopped",
            },
            "api_cost_dashboard": {
                "port": 8095,
                "url": "http://localhost:8095",
                "status": "stopped",
            },
            "andrei_endpoint": {
                "port": 8081,
                "url": "http://localhost:8081",
                "status": "stopped",
            },
        }


# Initialize console
console = CursorRootConsole()


@app.get("/", response_class=HTMLResponse)
async def root_dashboard():
    """Main root dashboard for Cursor AI Assistant"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cursor AI Assistant - Root Console</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .header {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                padding: 20px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                border-bottom: 3px solid #667eea;
            }}
            
            .header-content {{
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            
            .logo {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            
            .logo-icon {{
                width: 50px;
                height: 50px;
                background: linear-gradient(45deg, #667eea, #764ba2);
                border-radius: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                color: white;
                font-weight: bold;
            }}
            
            .logo-text h1 {{
                font-size: 28px;
                color: #333;
                margin-bottom: 5px;
            }}
            
            .logo-text p {{
                color: #666;
                font-size: 14px;
            }}
            
            .status-badges {{
                display: flex;
                gap: 10px;
            }}
            
            .badge {{
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 5px;
            }}
            
            .badge.online {{
                background: #d4edda;
                color: #155724;
            }}
            
            .badge.root {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .main-container {{
                max-width: 1200px;
                margin: 40px auto;
                padding: 0 20px;
            }}
            
            .section {{
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                margin-bottom: 30px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            
            .section-title {{
                font-size: 24px;
                margin-bottom: 20px;
                color: #333;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .pillars-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .pillar-card {{
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                border-radius: 15px;
                padding: 25px;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                border: 2px solid transparent;
            }}
            
            .pillar-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 15px 35px rgba(0,0,0,0.1);
                border-color: #667eea;
            }}
            
            .pillar-header {{
                display: flex;
                align-items: center;
                gap: 15px;
                margin-bottom: 15px;
            }}
            
            .pillar-icon {{
                font-size: 32px;
                width: 60px;
                height: 60px;
                background: rgba(255, 255, 255, 0.8);
                border-radius: 15px;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            
            .pillar-title {{
                font-size: 20px;
                font-weight: 700;
                color: #333;
            }}
            
            .pillar-desc {{
                color: #666;
                margin-bottom: 15px;
                line-height: 1.5;
            }}
            
            .services-list {{
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }}
            
            .service-tag {{
                background: rgba(102, 126, 234, 0.1);
                color: #667eea;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 500;
            }}
            
            .services-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
            }}
            
            .service-card {{
                background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
                border-radius: 15px;
                padding: 20px;
                transition: transform 0.3s ease;
            }}
            
            .service-card:hover {{
                transform: translateY(-3px);
            }}
            
            .service-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }}
            
            .service-name {{
                font-weight: 700;
                color: #333;
            }}
            
            .service-status {{
                padding: 4px 12px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: 600;
            }}
            
            .status-running {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status-stopped {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .service-url {{
                color: #667eea;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
            }}
            
            .service-url:hover {{
                text-decoration: underline;
            }}
            
            .footer {{
                text-align: center;
                padding: 20px;
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
            }}
            
            .contract-info {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 30px;
            }}
            
            .contract-title {{
                font-size: 22px;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .contract-details {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-bottom: 20px;
            }}
            
            .contract-item {{
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
            }}
            
            .contract-item strong {{
                display: block;
                margin-bottom: 5px;
                font-size: 14px;
                opacity: 0.9;
            }}
            
            .contract-item span {{
                font-size: 16px;
                font-weight: 600;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div class="logo">
                    <div class="logo-icon">CA</div>
                    <div class="logo-text">
                        <h1>Cursor AI Assistant</h1>
                        <p>Root Console - SC COOL BITS SRL</p>
                    </div>
                </div>
                <div class="status-badges">
                    <div class="badge online">
                        <span>🟢</span>
                        <span>ONLINE</span>
                    </div>
                    <div class="badge root">
                        <span>🔐</span>
                        <span>ROOT ACCESS</span>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="main-container">
            <div class="contract-info">
                <div class="contract-title">
                    <span>📋</span>
                    <span>Contract Details</span>
                </div>
                <div class="contract-details">
                    <div class="contract-item">
                        <strong>Company</strong>
                        <span>{console.company}</span>
                    </div>
                    <div class="contract-item">
                        <strong>CEO</strong>
                        <span>{console.ceo}</span>
                    </div>
                    <div class="contract-item">
                        <strong>AI Assistant</strong>
                        <span>{console.ai_assistant}</span>
                    </div>
                    <div class="contract-item">
                        <strong>Contract Date</strong>
                        <span>{console.contract_date}</span>
                    </div>
                    <div class="contract-item">
                        <strong>Access Level</strong>
                        <span>{console.access_level}</span>
                    </div>
                    <div class="contract-item">
                        <strong>Port</strong>
                        <span>{console.port}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span>🏗️</span>
                    <span>Main Pillars Architecture</span>
                </div>
                <div class="pillars-grid">
    """

    # Add pillars
    for pillar_key, pillar_info in console.main_pillars.items():
        html_content += f"""
                    <div class="pillar-card">
                        <div class="pillar-header">
                            <div class="pillar-icon">{pillar_info['icon']}</div>
                            <div class="pillar-title">{pillar_info['name']}</div>
                        </div>
                        <div class="pillar-desc">{pillar_info['description']}</div>
                        <div class="services-list">
        """
        for service in pillar_info["services"]:
            html_content += f'<span class="service-tag">{service}</span>'

        html_content += """
                        </div>
                    </div>
        """

    html_content += """
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">
                    <span>🚀</span>
                    <span>Services Status</span>
                </div>
                <div class="services-grid">
    """

    # Add services
    for service_name, service_info in console.services.items():
        status_class = (
            "status-running"
            if service_info["status"] == "running"
            else "status-stopped"
        )
        html_content += f"""
                    <div class="service-card">
                        <div class="service-header">
                            <div class="service-name">{service_name.replace('_', ' ').title()}</div>
                            <div class="service-status {status_class}">{service_info['status'].upper()}</div>
                        </div>
                        <div>
                            <div>Port: {service_info['port']}</div>
                            <a href="{service_info['url']}" target="_blank" class="service-url">{service_info['url']}</a>
                        </div>
                    </div>
        """

    html_content += """
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 Cursor AI Assistant - Primary Technical Console for SC COOL BITS SRL</p>
            <p>Contract Active: 2025-09-06 | Access Level: ROOT/CEO</p>
        </div>
        
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => {
                location.reload();
            }, 30000);
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_content)


@app.get("/api/status")
async def get_status():
    """Get system status"""
    return {
        "company": console.company,
        "ceo": console.ceo,
        "ai_assistant": console.ai_assistant,
        "contract_date": console.contract_date,
        "access_level": console.access_level,
        "port": console.port,
        "timestamp": datetime.now().isoformat(),
        "status": "online",
    }


@app.get("/api/pillars")
async def get_pillars():
    """Get main pillars architecture"""
    return {"pillars": console.main_pillars, "timestamp": datetime.now().isoformat()}


@app.get("/api/services")
async def get_services():
    """Get services status"""
    return {"services": console.services, "timestamp": datetime.now().isoformat()}


@app.get("/api/contract")
async def get_contract():
    """Get contract details"""
    return {
        "contract": {
            "company": console.company,
            "ceo": console.ceo,
            "ai_assistant": console.ai_assistant,
            "contract_date": console.contract_date,
            "access_level": console.access_level,
            "base_path": console.base_path,
            "machine": console.machine,
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Cursor AI Assistant Root Console",
        "version": "1.0.0",
        "access_level": "ROOT/CEO",
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 CURSOR AI ASSISTANT ROOT CONSOLE")
    print("🏢 SC COOL BITS SRL - CEO Endpoint")
    print("=" * 70)
    print(f"🔐 Access Level: {console.access_level}")
    print(f"👤 CEO: {console.ceo}")
    print(f"📁 Base Directory: {console.base_path}")
    print(f"📅 Contract Date: {console.contract_date}")
    print("=" * 70)
    print(f"🌐 Root Dashboard: http://localhost:{console.port}")
    print(f"🔍 Health Check: http://localhost:{console.port}/health")
    print(f"📋 API Status: http://localhost:{console.port}/api/status")
    print(f"🏗️ API Pillars: http://localhost:{console.port}/api/pillars")
    print(f"🚀 API Services: http://localhost:{console.port}/api/services")
    print(f"📄 API Contract: http://localhost:{console.port}/api/contract")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=console.port, log_level="info")
