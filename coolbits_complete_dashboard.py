#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai Complete Dashboard Server
SC COOL BITS SRL - All Services & Agents Dashboard
"""

from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn


class CoolBitsCompleteDashboard:
    """Complete dashboard for all CoolBits.ai services and agents"""

    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.ai_assistant = "Cursor AI Assistant"
        self.contract_date = "2025-09-06"
        self.base_path = r"C:\Users\andre\Desktop\coolbits"
        self.port = 8090

        # Initialize FastAPI app
        self.app = FastAPI(
            title="CoolBits.ai Complete Dashboard",
            description="Complete dashboard for all services and agents",
            version="1.0.0",
        )

        self._setup_routes()

        # All services and agents
        self.all_services = {
            "core_services": {
                "bridge": {
                    "port": 8080,
                    "url": "http://localhost:8080",
                    "status": "active",
                    "description": "Main CoolBits bridge service",
                },
                "multi_agent_chat": {
                    "port": 8096,
                    "url": "http://localhost:8096",
                    "status": "active",
                    "description": "Multi-agent chat system",
                },
                "enhanced_multi_agent": {
                    "port": 8091,
                    "url": "http://localhost:8091",
                    "status": "active",
                    "description": "Enhanced multi-agent chat",
                },
                "agent_portal": {
                    "port": 8099,
                    "url": "http://localhost:8099",
                    "status": "active",
                    "description": "Individual agent portal",
                },
                "cursor_root": {
                    "port": 8082,
                    "url": "http://localhost:8082",
                    "status": "active",
                    "description": "Cursor AI Assistant Root Console",
                },
            },
            "rag_services": {
                "advanced_rag": {
                    "port": 8090,
                    "url": "http://localhost:8090",
                    "status": "active",
                    "description": "Advanced RAG system",
                },
                "multi_domain_rag": {
                    "port": 8092,
                    "url": "http://localhost:8092",
                    "status": "active",
                    "description": "Multi-domain RAG",
                },
                "functional_rag": {
                    "port": 8093,
                    "url": "http://localhost:8093",
                    "status": "active",
                    "description": "Functional RAG system",
                },
                "vertex_rag": {
                    "port": 8094,
                    "url": "http://localhost:8094",
                    "status": "active",
                    "description": "Vertex AI RAG",
                },
            },
            "admin_services": {
                "coolbits_admin": {
                    "port": 8085,
                    "url": "http://localhost:8085",
                    "status": "active",
                    "description": "CoolBits admin panel",
                },
                "rag_admin": {
                    "port": 8086,
                    "url": "http://localhost:8086",
                    "status": "active",
                    "description": "RAG admin panel",
                },
                "vertex_admin": {
                    "port": 8087,
                    "url": "http://localhost:8087",
                    "status": "active",
                    "description": "Vertex AI admin",
                },
            },
            "development_agents": {
                "frontend_agent": {
                    "port": 3001,
                    "url": "http://localhost:3001",
                    "status": "ready",
                    "description": "Frontend Development Agent",
                    "technologies": ["React", "Next.js", "TypeScript", "Tailwind CSS"],
                    "api_keys": ["ogpt01-frontend", "ogrok01-frontend"],
                },
                "backend_agent": {
                    "port": 8081,
                    "url": "http://localhost:8081",
                    "status": "ready",
                    "description": "Backend Development Agent",
                    "technologies": ["Python", "FastAPI", "Uvicorn", "PostgreSQL"],
                    "api_keys": ["ogpt02-backend", "ogrok02-backend"],
                },
                "devops_agent": {
                    "port": 8083,
                    "url": "http://localhost:8083",
                    "status": "ready",
                    "description": "DevOps Automation Agent",
                    "technologies": ["Docker", "GitHub Actions", "Windows 11"],
                    "api_keys": ["ogpt03-devops", "ogrok03-devops"],
                },
                "testing_agent": {
                    "port": 8088,
                    "url": "http://localhost:8088",
                    "status": "ready",
                    "description": "Quality Assurance Agent",
                    "technologies": ["Python", "Pytest", "Selenium"],
                    "api_keys": ["ogpt04-testing", "ogrok04-testing"],
                },
            },
            "cblm_services": {
                "cblm_main": {
                    "port": 8084,
                    "url": "http://localhost:8084",
                    "status": "planning",
                    "description": "cbLM.ai main platform",
                },
                "cblm_inference": {
                    "port": 8089,
                    "url": "http://localhost:8089",
                    "status": "planning",
                    "description": "cbLM.ai inference engine",
                },
                "cblm_training": {
                    "port": 8095,
                    "url": "http://localhost:8095",
                    "status": "planning",
                    "description": "cbLM.ai training pipeline",
                },
            },
        }

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self._get_dashboard_html()

        @self.app.get("/api/status")
        async def get_status():
            return {
                "company": self.company,
                "ceo": self.ceo,
                "ai_assistant": self.ai_assistant,
                "contract_date": self.contract_date,
                "dashboard_port": self.port,
                "timestamp": datetime.now().isoformat(),
                "services": self.all_services,
            }

        @self.app.get("/api/services")
        async def get_services():
            return self.all_services

        @self.app.post("/api/start_service/{service_name}")
        async def start_service(service_name: str):
            """Start a specific service"""
            try:
                # Find service in all categories
                service_info = None
                for category, services in self.all_services.items():
                    if service_name in services:
                        service_info = services[service_name]
                        break

                if not service_info:
                    raise HTTPException(
                        status_code=404, detail=f"Service {service_name} not found"
                    )

                # TODO: Implement actual service starting logic
                return {
                    "service": service_name,
                    "status": "starting",
                    "port": service_info["port"],
                    "url": service_info["url"],
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/stop_service/{service_name}")
        async def stop_service(service_name: str):
            """Stop a specific service"""
            try:
                # Find service in all categories
                service_info = None
                for category, services in self.all_services.items():
                    if service_name in services:
                        service_info = services[service_name]
                        break

                if not service_info:
                    raise HTTPException(
                        status_code=404, detail=f"Service {service_name} not found"
                    )

                # TODO: Implement actual service stopping logic
                return {
                    "service": service_name,
                    "status": "stopping",
                    "port": service_info["port"],
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def _get_dashboard_html(self) -> str:
        """Generate complete dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoolBits.ai Complete Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .header-content {
            max-width: 1400px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        
        .logo-icon {
            width: 50px;
            height: 50px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
        
        .logo-text h1 {
            font-size: 28px;
            color: #333;
            margin-bottom: 5px;
        }
        
        .logo-text p {
            color: #666;
            font-size: 14px;
        }
        
        .status-bar {
            display: flex;
            gap: 20px;
            align-items: center;
        }
        
        .status-item {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(102, 126, 234, 0.1);
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: #4CAF50;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 30px 20px;
        }
        
        .section {
            margin-bottom: 40px;
        }
        
        .section-title {
            font-size: 24px;
            font-weight: 600;
            color: white;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .section-icon {
            font-size: 28px;
        }
        
        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
        }
        
        .service-card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .service-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        
        .service-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }
        
        .service-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 16px;
        }
        
        .service-icon {
            font-size: 32px;
            margin-right: 12px;
        }
        
        .service-title {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            flex: 1;
        }
        
        .service-status {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .status-active {
            background: #E8F5E8;
            color: #2E7D32;
        }
        
        .status-ready {
            background: #FFF3E0;
            color: #F57C00;
        }
        
        .status-planning {
            background: #E3F2FD;
            color: #1976D2;
        }
        
        .service-description {
            color: #666;
            font-size: 14px;
            margin-bottom: 16px;
            line-height: 1.5;
        }
        
        .service-details {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 16px;
        }
        
        .detail-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        
        .detail-label {
            font-size: 12px;
            color: #999;
            font-weight: 500;
            text-transform: uppercase;
        }
        
        .detail-value {
            font-size: 14px;
            color: #333;
            font-weight: 500;
        }
        
        .service-actions {
            display: flex;
            gap: 8px;
        }
        
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }
        
        .btn-primary {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #f5f5f5;
            color: #666;
            border: 1px solid #ddd;
        }
        
        .btn-secondary:hover {
            background: #e9e9e9;
        }
        
        .btn-success {
            background: #4CAF50;
            color: white;
        }
        
        .btn-danger {
            background: #f44336;
            color: white;
        }
        
        .technologies {
            margin-top: 12px;
        }
        
        .tech-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        
        .tech-tag {
            background: rgba(102, 126, 234, 0.1);
            color: #667eea;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 500;
        }
        
        .api-keys {
            margin-top: 12px;
        }
        
        .api-key-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        
        .api-key-tag {
            background: rgba(118, 75, 162, 0.1);
            color: #764ba2;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 500;
        }
        
        .footer {
            text-align: center;
            padding: 30px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }
        
        .refresh-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border: none;
            border-radius: 50%;
            color: white;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(0, 0, 0, 0.3);
        }
        
        @media (max-width: 768px) {
            .services-grid {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                gap: 20px;
            }
            
            .status-bar {
                flex-wrap: wrap;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="logo">
                <div class="logo-icon">CB</div>
                <div class="logo-text">
                    <h1>CoolBits.ai Complete Dashboard</h1>
                    <p>SC COOL BITS SRL - All Services & Agents</p>
                </div>
            </div>
            <div class="status-bar">
                <div class="status-item">
                    <div class="status-dot"></div>
                    <span>System Online</span>
                </div>
                <div class="status-item">
                    <div class="status-dot"></div>
                    <span>RAG System Active</span>
                </div>
                <div class="status-item">
                    <div class="status-dot"></div>
                    <span>Multi-Agent Ready</span>
                </div>
                <div class="status-item">
                    <div class="status-dot"></div>
                    <span>Development Agents</span>
                </div>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">🏢</span>
                Core Services
            </h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🌉</span>
                            <span class="service-title">Bridge Service</span>
                        </div>
                        <span class="service-status status-active">Active</span>
                    </div>
                    <div class="service-description">Main CoolBits bridge service connecting all components</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8080</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Running</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <a href="http://localhost:8080" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('bridge')">🔄 Refresh</button>
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">💬</span>
                            <span class="service-title">Multi-Agent Chat</span>
                        </div>
                        <span class="service-status status-active">Active</span>
                    </div>
                    <div class="service-description">Advanced multi-agent chat system with AI coordination</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8096</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Running</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <a href="http://localhost:8096" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('multi_agent_chat')">🔄 Refresh</button>
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🤖</span>
                            <span class="service-title">Cursor Root Console</span>
                        </div>
                        <span class="service-status status-active">Active</span>
                    </div>
                    <div class="service-description">Cursor AI Assistant Root Console - CEO Level Access</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8082</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Access</span>
                            <span class="detail-value">ROOT/CEO</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <a href="http://localhost:8082" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('cursor_root')">🔄 Refresh</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">🧠</span>
                RAG Services
            </h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🔍</span>
                            <span class="service-title">Advanced RAG</span>
                        </div>
                        <span class="service-status status-active">Active</span>
                    </div>
                    <div class="service-description">Advanced Retrieval-Augmented Generation system</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8090</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Running</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <a href="http://localhost:8090" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('advanced_rag')">🔄 Refresh</button>
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🌐</span>
                            <span class="service-title">Multi-Domain RAG</span>
                        </div>
                        <span class="service-status status-active">Active</span>
                    </div>
                    <div class="service-description">Multi-domain RAG system for various knowledge areas</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8092</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Running</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <a href="http://localhost:8092" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('multi_domain_rag')">🔄 Refresh</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">💻</span>
                Development Agents
            </h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🎨</span>
                            <span class="service-title">Frontend Agent</span>
                        </div>
                        <span class="service-status status-ready">Ready</span>
                    </div>
                    <div class="service-description">Specialized agent for frontend development and UI/UX</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">3001</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Ready</span>
                        </div>
                    </div>
                    <div class="technologies">
                        <div class="detail-label">Technologies</div>
                        <div class="tech-tags">
                            <span class="tech-tag">React</span>
                            <span class="tech-tag">Next.js</span>
                            <span class="tech-tag">TypeScript</span>
                            <span class="tech-tag">Tailwind CSS</span>
                        </div>
                    </div>
                    <div class="api-keys">
                        <div class="detail-label">API Keys</div>
                        <div class="api-key-tags">
                            <span class="api-key-tag">ogpt01-frontend</span>
                            <span class="api-key-tag">ogrok01-frontend</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <button class="btn btn-success" onclick="startService('frontend_agent')">▶️ Start</button>
                        <a href="http://localhost:3001" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('frontend_agent')">🔄 Refresh</button>
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">⚙️</span>
                            <span class="service-title">Backend Agent</span>
                        </div>
                        <span class="service-status status-ready">Ready</span>
                    </div>
                    <div class="service-description">Specialized agent for backend development and API services</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8081</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Ready</span>
                        </div>
                    </div>
                    <div class="technologies">
                        <div class="detail-label">Technologies</div>
                        <div class="tech-tags">
                            <span class="tech-tag">Python</span>
                            <span class="tech-tag">FastAPI</span>
                            <span class="tech-tag">Uvicorn</span>
                            <span class="tech-tag">PostgreSQL</span>
                        </div>
                    </div>
                    <div class="api-keys">
                        <div class="detail-label">API Keys</div>
                        <div class="api-key-tags">
                            <span class="api-key-tag">ogpt02-backend</span>
                            <span class="api-key-tag">ogrok02-backend</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <button class="btn btn-success" onclick="startService('backend_agent')">▶️ Start</button>
                        <a href="http://localhost:8081" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('backend_agent')">🔄 Refresh</button>
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🚀</span>
                            <span class="service-title">DevOps Agent</span>
                        </div>
                        <span class="service-status status-ready">Ready</span>
                    </div>
                    <div class="service-description">Specialized agent for DevOps and infrastructure automation</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8083</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Ready</span>
                        </div>
                    </div>
                    <div class="technologies">
                        <div class="detail-label">Technologies</div>
                        <div class="tech-tags">
                            <span class="tech-tag">Docker</span>
                            <span class="tech-tag">GitHub Actions</span>
                            <span class="tech-tag">Windows 11</span>
                            <span class="tech-tag">PowerShell</span>
                        </div>
                    </div>
                    <div class="api-keys">
                        <div class="detail-label">API Keys</div>
                        <div class="api-key-tags">
                            <span class="api-key-tag">ogpt03-devops</span>
                            <span class="api-key-tag">ogrok03-devops</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <button class="btn btn-success" onclick="startService('devops_agent')">▶️ Start</button>
                        <a href="http://localhost:8083" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('devops_agent')">🔄 Refresh</button>
                    </div>
                </div>

                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🧪</span>
                            <span class="service-title">Testing Agent</span>
                        </div>
                        <span class="service-status status-ready">Ready</span>
                    </div>
                    <div class="service-description">Specialized agent for testing and quality assurance</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8088</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Ready</span>
                        </div>
                    </div>
                    <div class="technologies">
                        <div class="detail-label">Technologies</div>
                        <div class="tech-tags">
                            <span class="tech-tag">Python</span>
                            <span class="tech-tag">Pytest</span>
                            <span class="tech-tag">Selenium</span>
                            <span class="tech-tag">Postman</span>
                        </div>
                    </div>
                    <div class="api-keys">
                        <div class="detail-label">API Keys</div>
                        <div class="api-key-tags">
                            <span class="api-key-tag">ogpt04-testing</span>
                            <span class="api-key-tag">ogrok04-testing</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <button class="btn btn-success" onclick="startService('testing_agent')">▶️ Start</button>
                        <a href="http://localhost:8088" target="_blank" class="btn btn-primary">🌐 Open</a>
                        <button class="btn btn-secondary" onclick="refreshService('testing_agent')">🔄 Refresh</button>
                    </div>
                </div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">
                <span class="section-icon">🧠</span>
                cbLM.ai Services
            </h2>
            <div class="services-grid">
                <div class="service-card">
                    <div class="service-header">
                        <div style="display: flex; align-items: center;">
                            <span class="service-icon">🤖</span>
                            <span class="service-title">cbLM.ai Platform</span>
                        </div>
                        <span class="service-status status-planning">Planning</span>
                    </div>
                    <div class="service-description">Language model platform for SC COOL BITS SRL</div>
                    <div class="service-details">
                        <div class="detail-item">
                            <span class="detail-label">Port</span>
                            <span class="detail-value">8084</span>
                        </div>
                        <div class="detail-item">
                            <span class="detail-label">Status</span>
                            <span class="detail-value">Planning</span>
                        </div>
                    </div>
                    <div class="service-actions">
                        <button class="btn btn-secondary" onclick="setupCBLM()">🏗️ Setup</button>
                        <button class="btn btn-secondary" onclick="refreshService('cblm_main')">🔄 Refresh</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <button class="refresh-btn" onclick="refreshAll()" title="Refresh All Services">🔄</button>

    <div class="footer">
        <p>🏢 SC COOL BITS SRL | 👤 CEO: Andrei | 🤖 AI Assistant: Cursor AI Assistant | 📅 Contract: 2025-09-06</p>
        <p>Complete Dashboard - All Services & Agents Management</p>
    </div>

    <script>
        async function startService(serviceName) {
            try {
                const response = await fetch(`/api/start_service/${serviceName}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const result = await response.json();
                    alert(`Service ${serviceName} is starting on port ${result.port}`);
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    alert('Failed to start service');
                }
            } catch (error) {
                console.error('Error starting service:', error);
                alert('Error starting service');
            }
        }

        async function stopService(serviceName) {
            try {
                const response = await fetch(`/api/stop_service/${serviceName}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });
                
                if (response.ok) {
                    const result = await response.json();
                    alert(`Service ${serviceName} is stopping`);
                    setTimeout(() => {
                        location.reload();
                    }, 2000);
                } else {
                    alert('Failed to stop service');
                }
            } catch (error) {
                console.error('Error stopping service:', error);
                alert('Error stopping service');
            }
        }

        async function refreshService(serviceName) {
            try {
                const response = await fetch(`/api/services`);
                if (response.ok) {
                    const services = await response.json();
                    console.log('Services refreshed:', services);
                    alert(`Service ${serviceName} status refreshed`);
                }
            } catch (error) {
                console.error('Error refreshing service:', error);
            }
        }

        function refreshAll() {
            location.reload();
        }

        function setupCBLM() {
            alert('cbLM.ai setup will be initiated. This will create the complete language model platform structure.');
        }

        // Auto-refresh every 30 seconds
        setInterval(() => {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    console.log('Dashboard status updated:', data);
                })
                .catch(error => {
                    console.error('Error updating status:', error);
                });
        }, 30000);
    </script>
</body>
</html>
        """

    def initialize_dashboard(self):
        """Initialize the complete dashboard"""
        print("=" * 70)
        print("🌐 COOLBITS.AI COMPLETE DASHBOARD")
        print("🏢 SC COOL BITS SRL - All Services & Agents")
        print("=" * 70)
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print(f"📅 Contract Date: {self.contract_date}")
        print(f"🌐 Dashboard Port: {self.port}")
        print("=" * 70)
        print("🚀 Available Services:")
        print("  • Core Services: Bridge, Multi-Agent Chat, Root Console")
        print("  • RAG Services: Advanced RAG, Multi-Domain RAG")
        print("  • Development Agents: Frontend, Backend, DevOps, Testing")
        print("  • cbLM.ai Services: Language Model Platform")
        print("=" * 70)
        print(f"🔗 Dashboard URL: http://localhost:{self.port}")
        print(f"📋 API Status: http://localhost:{self.port}/api/status")
        print("=" * 70)


if __name__ == "__main__":
    dashboard = CoolBitsCompleteDashboard()
    dashboard.initialize_dashboard()

    print(f"🌐 Starting Complete Dashboard on port {dashboard.port}")
    print("=" * 70)

    uvicorn.run(dashboard.app, host="0.0.0.0", port=dashboard.port, log_level="info")
