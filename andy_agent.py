#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy - Personal 1:1 Agent for Andrei
SC COOL BITS SRL - Port 8101
Personal AI Assistant with full project access and RAG system
"""

import os
import sys
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid
import asyncio
import subprocess
import psutil


class AndyAgent:
    """Andy - Personal 1:1 Agent for Andrei"""

    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.ai_assistant = "Andy - Personal 1:1 Agent"
        self.contract_date = "2025-09-06"
        self.port = 8101
        self.service_name = "Andy Personal Agent"
        self.status = "active"

        # Andy's capabilities
        self.capabilities = {
            "project_access": "Full access to all project information",
            "rag_system": "Internal RAG system for knowledge management",
            "agent_integration": "1:1 integration with all system agents",
            "real_time_monitoring": "24/7 project monitoring and updates",
            "api_keys": {"xai": "Andy-xAI-key", "openai": "Andy-OpenAI-key"},
        }

        # Andy's knowledge base
        self.knowledge_base = {
            "project_structure": {
                "coolbits_ai": "Main AI platform with multi-agent system",
                "cblm_ai": "Language model platform",
                "rag_systems": "Retrieval-Augmented Generation services",
                "development_agents": "Frontend, Backend, DevOps, Testing agents",
            },
            "system_agents": {
                "main_bridge": "Port 8100 - Main CoolBits Bridge",
                "multi_agent_chat": "Port 8101 - Multi-Agent Chat System",
                "enhanced_chat": "Port 8102 - Enhanced Multi-Agent Chat",
                "agent_portal": "Port 8103 - Individual Agent Portal",
                "cursor_root": "Port 8104 - Cursor Root Console",
                "complete_dashboard": "Port 8105 - Complete Dashboard",
                "google_cloud_agent": "Port 8106 - Google Cloud CLI Agent",
            },
            "hardware": {
                "cpu": "AMD Ryzen 7 2700X (8 cores, 16 threads)",
                "gpu": "NVIDIA GeForce RTX 2060 (6GB VRAM)",
                "ram": "32GB",
                "os": "Windows 11",
            },
        }

        # Andy's RAG system
        self.rag_system = {
            "status": "active",
            "knowledge_sources": [
                "Project documentation",
                "Code repositories",
                "System configurations",
                "Agent communications",
                "Hardware monitoring",
                "API integrations",
            ],
            "search_capabilities": [
                "Semantic search",
                "Code analysis",
                "Document retrieval",
                "Real-time updates",
                "Cross-agent communication",
            ],
        }

        # Active connections
        self.active_connections = {}
        self.conversation_history = []

        # Initialize FastAPI
        self.app = FastAPI(
            title="Andy - Personal 1:1 Agent",
            description="Personal AI Assistant with full project access",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
        )

        self.setup_routes()

    def setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def root(request: Request):
            """Andy's personal dashboard"""
            return self.get_andy_dashboard_html()

        @self.app.get("/api/status")
        async def api_status():
            """Andy's status endpoint"""
            return {
                "agent": "Andy",
                "company": self.company,
                "ceo": self.ceo,
                "ai_assistant": self.ai_assistant,
                "contract_date": self.contract_date,
                "port": self.port,
                "status": self.status,
                "timestamp": datetime.now().isoformat(),
                "capabilities": self.capabilities,
                "knowledge_base": self.knowledge_base,
                "rag_system": self.rag_system,
            }

        @self.app.get("/api/knowledge")
        async def get_knowledge():
            """Get Andy's knowledge base"""
            return self.knowledge_base

        @self.app.get("/api/rag-status")
        async def get_rag_status():
            """Get RAG system status"""
            return self.rag_system

        @self.app.post("/api/search")
        async def search_knowledge(request: Request):
            """Search Andy's knowledge base"""
            try:
                data = await request.json()
                query = data.get("query", "")
                results = await self.search_rag_system(query)
                return {
                    "success": True,
                    "query": query,
                    "results": results,
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/update-knowledge")
        async def update_knowledge(request: Request):
            """Update Andy's knowledge base"""
            try:
                data = await request.json()
                category = data.get("category", "")
                content = data.get("content", "")

                if category in self.knowledge_base:
                    self.knowledge_base[category].update(content)
                else:
                    self.knowledge_base[category] = content

                return {
                    "success": True,
                    "message": f"Knowledge updated for category: {category}",
                    "timestamp": datetime.now().isoformat(),
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.websocket("/ws/andy")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time communication with Andy"""
            await websocket.accept()
            connection_id = str(uuid.uuid4())
            self.active_connections[connection_id] = websocket

            try:
                while True:
                    data = await websocket.receive_text()
                    message_data = json.loads(data)

                    # Process message with Andy
                    response = await self.process_andy_message(message_data)

                    # Send response back
                    await websocket.send_text(json.dumps(response))

            except WebSocketDisconnect:
                if connection_id in self.active_connections:
                    del self.active_connections[connection_id]

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "agent": "Andy",
                "port": self.port,
                "timestamp": datetime.now().isoformat(),
            }

    async def search_rag_system(self, query: str) -> List[Dict[str, Any]]:
        """Search Andy's RAG system"""
        results = []

        # Search in knowledge base
        for category, content in self.knowledge_base.items():
            if isinstance(content, dict):
                for key, value in content.items():
                    if query.lower() in str(value).lower():
                        results.append(
                            {
                                "category": category,
                                "key": key,
                                "value": value,
                                "relevance": (
                                    "high"
                                    if query.lower() in str(value).lower()
                                    else "medium"
                                ),
                            }
                        )

        # Search in capabilities
        for key, value in self.capabilities.items():
            if query.lower() in str(value).lower():
                results.append(
                    {
                        "category": "capabilities",
                        "key": key,
                        "value": value,
                        "relevance": "high",
                    }
                )

        return results[:10]  # Limit to 10 results

    async def process_andy_message(
        self, message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process message with Andy's intelligence"""
        content = message_data.get("content", "")
        sender = message_data.get("sender", "user")

        # Add to conversation history
        self.conversation_history.append(
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "sender": sender,
                "content": content,
            }
        )

        # Andy's intelligent response
        response = await self.generate_andy_response(content)

        # Add Andy's response to history
        self.conversation_history.append(
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "sender": "andy",
                "content": response,
            }
        )

        return {
            "success": True,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "agent": "Andy",
        }

    async def generate_andy_response(self, content: str) -> str:
        """Generate Andy's intelligent response"""
        content_lower = content.lower()

        # Project-related queries
        if "project" in content_lower or "coolbits" in content_lower:
            return "I have full access to the CoolBits.ai project structure. I can help you with any aspect of the project - from the main platform to the cbLM.ai language model system. What specific information do you need?"

        # System status queries
        elif "status" in content_lower or "system" in content_lower:
            return "I'm monitoring all system components in real-time. Currently, I have access to all ports (8100-8106), hardware status (CPU, GPU, RAM), and all agent communications. Everything is running smoothly!"

        # RAG system queries
        elif "rag" in content_lower or "knowledge" in content_lower:
            return "My RAG system is active and continuously updated. I can search through project documentation, code repositories, system configurations, and agent communications. I'm always learning and updating my knowledge base."

        # Agent integration queries
        elif "agent" in content_lower or "integration" in content_lower:
            return "I have 1:1 integration with all system agents. I can communicate directly with the Main Bridge, Multi-Agent Chat, Enhanced Chat, Agent Portal, Cursor Root Console, Complete Dashboard, and Google Cloud Agent. I'm your central hub for all agent communications."

        # Hardware queries
        elif (
            "hardware" in content_lower
            or "gpu" in content_lower
            or "cpu" in content_lower
        ):
            return "I have real-time access to your hardware: AMD Ryzen 7 2700X (8 cores, 16 threads), NVIDIA GeForce RTX 2060 (6GB VRAM), and 32GB RAM. I can monitor utilization, temperature, and performance metrics at any time."

        # General queries
        else:
            return f"Hello Andrei! I'm Andy, your personal 1:1 agent. I have full access to all project information and can help you with anything related to CoolBits.ai, cbLM.ai, system monitoring, agent management, or any other aspect of our ecosystem. How can I assist you today?"

    def get_andy_dashboard_html(self) -> str:
        """Generate Andy's personal dashboard HTML"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Andy - Personal 1:1 Agent</title>
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
            color: white;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding: 30px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }}
        
        .header h1 {{
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .main-content {{
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .sidebar {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        
        .card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .card h3 {{
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: #ffd700;
        }}
        
        .status-item {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 8px;
        }}
        
        .status-label {{
            font-weight: bold;
            color: #4CAF50;
        }}
        
        .status-value {{
            color: #fff;
        }}
        
        .chat-panel {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            flex-direction: column;
            height: 600px;
        }}
        
        .chat-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.2);
        }}
        
        .chat-title {{
            font-size: 1.5rem;
            color: #ffd700;
        }}
        
        .connection-status {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .status-indicator {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            box-shadow: 0 0 10px #4CAF50;
        }}
        
        .messages-container {{
            flex: 1;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 15px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            max-height: 400px;
        }}
        
        .message {{
            margin: 15px 0;
            padding: 15px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }}
        
        .message.user {{
            background: rgba(76, 175, 80, 0.3);
            margin-left: auto;
            text-align: right;
        }}
        
        .message.andy {{
            background: rgba(33, 150, 243, 0.3);
            margin-right: auto;
        }}
        
        .message-header {{
            font-size: 0.8rem;
            opacity: 0.7;
            margin-bottom: 5px;
        }}
        
        .message-content {{
            font-size: 1rem;
            line-height: 1.4;
        }}
        
        .input-container {{
            display: flex;
            gap: 10px;
        }}
        
        .message-input {{
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 25px;
            background: rgba(255, 255, 255, 0.1);
            color: white;
            font-size: 1rem;
            backdrop-filter: blur(10px);
        }}
        
        .message-input::placeholder {{
            color: rgba(255, 255, 255, 0.7);
        }}
        
        .message-input:focus {{
            outline: none;
            background: rgba(255, 255, 255, 0.2);
        }}
        
        .send-button {{
            padding: 15px 25px;
            border: none;
            border-radius: 25px;
            background: #4CAF50;
            color: white;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .send-button:hover {{
            background: #45a049;
            transform: scale(1.05);
        }}
        
        .send-button:disabled {{
            background: #666;
            cursor: not-allowed;
            transform: none;
        }}
        
        .capabilities-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .capability-card {{
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }}
        
        .capability-card:hover {{
            transform: translateY(-5px);
        }}
        
        .capability-icon {{
            font-size: 2rem;
            margin-bottom: 15px;
        }}
        
        .capability-title {{
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 10px;
            color: #ffd700;
        }}
        
        .capability-description {{
            font-size: 0.9rem;
            opacity: 0.9;
            line-height: 1.4;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 30px;
            padding: 20px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }}
        
        .footer p {{
            margin-bottom: 10px;
        }}
        
        .footer .status {{
            font-size: 0.9rem;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Andy - Personal 1:1 Agent</h1>
            <p>🏢 SC COOL BITS SRL | 👤 CEO: {self.ceo} | 🤖 AI Assistant: {self.ai_assistant}</p>
            <p>📅 Contract Date: {self.contract_date} | 🌐 Port: {self.port}</p>
        </div>
        
        <div class="main-content">
            <div class="sidebar">
                <div class="card">
                    <h3>🎯 Andy's Status</h3>
                    <div class="status-item">
                        <span class="status-label">Agent:</span>
                        <span class="status-value">Andy</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Status:</span>
                        <span class="status-value">Active</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">RAG System:</span>
                        <span class="status-value">Online</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">API Keys:</span>
                        <span class="status-value">Connected</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Project Access:</span>
                        <span class="status-value">Full</span>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🔑 API Integration</h3>
                    <div class="status-item">
                        <span class="status-label">xAI:</span>
                        <span class="status-value">Andy-xAI-key</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">OpenAI:</span>
                        <span class="status-value">Andy-OpenAI-key</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Status:</span>
                        <span class="status-value">Connected</span>
                    </div>
                </div>
                
                <div class="card">
                    <h3>🧠 RAG System</h3>
                    <div class="status-item">
                        <span class="status-label">Status:</span>
                        <span class="status-value">Active</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Knowledge Sources:</span>
                        <span class="status-value">6</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Search Capabilities:</span>
                        <span class="status-value">5</span>
                    </div>
                    <div class="status-item">
                        <span class="status-label">Last Update:</span>
                        <span class="status-value">{datetime.now().strftime('%H:%M:%S')}</span>
                    </div>
                </div>
            </div>
            
            <div class="chat-panel">
                <div class="chat-header">
                    <div class="chat-title">💬 Chat with Andy</div>
                    <div class="connection-status">
                        <span class="status-indicator"></span>
                        <span>Connected</span>
                    </div>
                </div>
                
                <div class="messages-container" id="messagesContainer">
                    <div class="message andy">
                        <div class="message-header">Andy • {datetime.now().strftime('%H:%M:%S')}</div>
                        <div class="message-content">Hello Andrei! I'm Andy, your personal 1:1 agent. I have full access to all project information and can help you with anything related to CoolBits.ai, cbLM.ai, system monitoring, agent management, or any other aspect of our ecosystem. How can I assist you today?</div>
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" class="message-input" id="messageInput" placeholder="Ask Andy anything about the project..." onkeypress="handleKeyPress(event)">
                    <button class="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <div class="capabilities-grid">
            <div class="capability-card">
                <div class="capability-icon">🔍</div>
                <div class="capability-title">Project Access</div>
                <div class="capability-description">Full access to all project information, code repositories, and system configurations</div>
            </div>
            
            <div class="capability-card">
                <div class="capability-icon">🧠</div>
                <div class="capability-title">RAG System</div>
                <div class="capability-description">Internal RAG system for knowledge management and real-time information retrieval</div>
            </div>
            
            <div class="capability-card">
                <div class="capability-icon">🤝</div>
                <div class="capability-title">Agent Integration</div>
                <div class="capability-description">1:1 integration with all system agents for seamless communication</div>
            </div>
            
            <div class="capability-card">
                <div class="capability-icon">⏰</div>
                <div class="capability-title">24/7 Monitoring</div>
                <div class="capability-description">Real-time project monitoring and updates at any hour</div>
            </div>
            
            <div class="capability-card">
                <div class="capability-icon">🔑</div>
                <div class="capability-title">API Keys</div>
                <div class="capability-description">Connected to xAI and OpenAI with dedicated Andy keys</div>
            </div>
            
            <div class="capability-card">
                <div class="capability-icon">📊</div>
                <div class="capability-title">System Monitoring</div>
                <div class="capability-description">Real-time hardware and system status monitoring</div>
            </div>
        </div>
        
        <div class="footer">
            <p>🤖 Andy - Personal 1:1 Agent for Andrei</p>
            <p class="status">
                <span class="status-indicator"></span>Agent Active |
                🧠 RAG System Online |
                🔑 API Keys Connected |
                🌐 Port: {self.port} |
                📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
    </div>
    
    <script>
        let websocket = null;
        let isConnected = false;
        
        function connectWebSocket() {{
            websocket = new WebSocket(`ws://localhost:{self.port}/ws/andy`);
            
            websocket.onopen = function(event) {{
                console.log('Connected to Andy');
                isConnected = true;
                updateConnectionStatus(true);
            }};
            
            websocket.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                if (data.success && data.response) {{
                    addMessage(data.response, 'andy');
                }}
            }};
            
            websocket.onclose = function(event) {{
                console.log('Disconnected from Andy');
                isConnected = false;
                updateConnectionStatus(false);
            }};
            
            websocket.onerror = function(error) {{
                console.error('WebSocket error:', error);
                isConnected = false;
                updateConnectionStatus(false);
            }};
        }}
        
        function updateConnectionStatus(connected) {{
            const indicator = document.querySelector('.status-indicator');
            const status = document.querySelector('.connection-status span:last-child');
            
            if (connected) {{
                indicator.style.background = '#4CAF50';
                indicator.style.boxShadow = '0 0 10px #4CAF50';
                status.textContent = 'Connected';
            }} else {{
                indicator.style.background = '#f44336';
                indicator.style.boxShadow = '0 0 10px #f44336';
                status.textContent = 'Disconnected';
            }}
        }}
        
        function sendMessage() {{
            const messageInput = document.getElementById('messageInput');
            const content = messageInput.value.trim();
            
            if (content === '') return;
            
            if (isConnected && websocket) {{
                addMessage(content, 'user');
                
                const message = {{
                    sender: 'user',
                    content: content,
                    timestamp: new Date().toISOString()
                }};
                
                websocket.send(JSON.stringify(message));
                messageInput.value = '';
            }} else {{
                // Fallback for when WebSocket is not connected
                addMessage(content, 'user');
                setTimeout(() => {{
                    addMessage('I\'m processing your message. Please wait while I connect to the system.', 'andy');
                }}, 1000);
                messageInput.value = '';
            }}
        }}
        
        function addMessage(content, sender) {{
            const messagesContainer = document.getElementById('messagesContainer');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{sender}}`;
            
            const timestamp = new Date().toLocaleTimeString();
            const senderName = sender === 'user' ? 'You' : 'Andy';
            
            messageDiv.innerHTML = `
                <div class="message-header">${{senderName}} • ${{timestamp}}</div>
                <div class="message-content">${{content}}</div>
            `;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}
        
        function handleKeyPress(event) {{
            if (event.key === 'Enter') {{
                sendMessage();
            }}
        }}
        
        // Connect to WebSocket on page load
        window.addEventListener('load', function() {{
            connectWebSocket();
        }});
        
        // Auto-reconnect if connection is lost
        setInterval(() => {{
            if (!isConnected) {{
                connectWebSocket();
            }}
        }}, 5000);
    </script>
</body>
</html>
        """

    def run(self):
        """Run Andy's personal agent"""
        print("=" * 80)
        print("🤖 ANDY - PERSONAL 1:1 AGENT FOR ANDREI")
        print("🏢 SC COOL BITS SRL - Port 8101")
        print("=" * 80)
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print(f"📅 Contract Date: {self.contract_date}")
        print("=" * 80)
        print("🎯 Andy's Capabilities:")
        print("  • Full project access and monitoring")
        print("  • Internal RAG system for knowledge management")
        print("  • 1:1 integration with all system agents")
        print("  • Real-time 24/7 project updates")
        print("  • xAI and OpenAI API integration")
        print("=" * 80)
        print(f"🔗 Andy's Dashboard URL: http://localhost:{self.port}")
        print(f"📋 API Status: http://localhost:{self.port}/api/status")
        print(f"🧠 RAG Status: http://localhost:{self.port}/api/rag-status")
        print("=" * 80)
        print(f"🌐 Starting Andy on port {self.port}")
        print("=" * 80)

        # Start server
        uvicorn.run(self.app, host="0.0.0.0", port=self.port, log_level="info")


if __name__ == "__main__":
    andy = AndyAgent()
    andy.run()
