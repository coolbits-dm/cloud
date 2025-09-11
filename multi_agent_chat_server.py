#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CoolBits.ai Multi-Agent Chat System - Port 8101
SC COOL BITS SRL - Simple multi-agent chat
"""

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from datetime import datetime

app = FastAPI(title="CoolBits.ai Multi-Agent Chat", version="1.0.0")


@app.get("/", response_class=HTMLResponse)
async def root():
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>CoolBits.ai Multi-Agent Chat</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            margin: 0; 
            padding: 20px; 
        }}
        .container {{ 
            max-width: 1000px; 
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
            grid-template-columns: 1fr 2fr;
            gap: 20px;
        }}
        .agents-panel {{ 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
        }}
        .chat-panel {{ 
            background: rgba(255,255,255,0.1); 
            padding: 20px; 
            border-radius: 15px; 
        }}
        .agent-item {{
            background: rgba(255,255,255,0.1);
            margin: 10px 0;
            padding: 15px;
            border-radius: 10px;
            cursor: pointer;
        }}
        .agent-item:hover {{
            background: rgba(255,255,255,0.2);
        }}
        .messages {{
            background: rgba(0,0,0,0.2);
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 15px;
            max-height: 300px;
            overflow-y: auto;
        }}
        .message {{
            margin: 10px 0;
            padding: 10px;
            border-radius: 10px;
        }}
        .message.user {{
            background: rgba(76,175,80,0.3);
            text-align: right;
        }}
        .message.ai {{
            background: rgba(33,150,243,0.3);
        }}
        .input-container {{
            display: flex;
            gap: 10px;
        }}
        .message-input {{
            flex: 1;
            padding: 12px;
            border: none;
            border-radius: 25px;
            background: rgba(255,255,255,0.1);
            color: white;
        }}
        .send-button {{
            padding: 12px 25px;
            border: none;
            border-radius: 25px;
            background: #4CAF50;
            color: white;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💬 CoolBits.ai Multi-Agent Chat</h1>
            <p>🏢 SC COOL BITS SRL | 👤 CEO: Andrei | 🤖 AI Assistant: Cursor AI Assistant</p>
            <p>📅 Contract Date: 2025-09-06 | 🌐 Port: 8101</p>
        </div>
        
        <div class="main-content">
            <div class="agents-panel">
                <h3>🤖 Available Agents</h3>
                <div class="agent-item" onclick="selectAgent('ceo')">
                    <strong>CEO Agent</strong><br>
                    <small>Chief Executive Officer</small>
                </div>
                <div class="agent-item" onclick="selectAgent('cto')">
                    <strong>CTO Agent</strong><br>
                    <small>Chief Technology Officer</small>
                </div>
                <div class="agent-item" onclick="selectAgent('frontend')">
                    <strong>Frontend Developer</strong><br>
                    <small>Frontend Development</small>
                </div>
                <div class="agent-item" onclick="selectAgent('backend')">
                    <strong>Backend Developer</strong><br>
                    <small>Backend Development</small>
                </div>
                <div class="agent-item" onclick="selectAgent('devops')">
                    <strong>DevOps Engineer</strong><br>
                    <small>DevOps & Infrastructure</small>
                </div>
                <div class="agent-item" onclick="selectAgent('qa')">
                    <strong>QA Engineer</strong><br>
                    <small>Quality Assurance</small>
                </div>
            </div>
            
            <div class="chat-panel">
                <h3>💬 Multi-Agent Discussion</h3>
                <div class="messages" id="messages">
                    <div class="message ai">
                        Welcome to CoolBits.ai Multi-Agent Chat System! Select agents from the left panel and start an intelligent discussion.
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" class="message-input" id="messageInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                    <button class="send-button" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let selectedAgents = [];
        
        function selectAgent(agentId) {{
            const agentItem = event.target.closest('.agent-item');
            if (agentItem.classList.contains('selected')) {{
                agentItem.classList.remove('selected');
                selectedAgents = selectedAgents.filter(id => id !== agentId);
            }} else {{
                agentItem.classList.add('selected');
                selectedAgents.push(agentId);
            }}
            updateChatTitle();
        }}
        
        function updateChatTitle() {{
            const chatTitle = document.querySelector('.chat-panel h3');
            if (selectedAgents.length === 0) {{
                chatTitle.textContent = '💬 Multi-Agent Discussion';
            }} else {{
                chatTitle.textContent = `💬 Discussion with ${{selectedAgents.length}} agent(s)`;
            }}
        }}
        
        function sendMessage() {{
            const messageInput = document.getElementById('messageInput');
            const content = messageInput.value.trim();
            
            if (content === '') return;
            
            addMessage(content, 'user');
            messageInput.value = '';
            
            // Simulate AI response
            setTimeout(() => {{
                addMessage('Thank you for your message! I am here to facilitate intelligent discussions between our agents.', 'ai');
            }}, 1000);
        }}
        
        function addMessage(content, sender) {{
            const messagesContainer = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${{sender}}`;
            messageDiv.textContent = content;
            
            messagesContainer.appendChild(messageDiv);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }}
        
        function handleKeyPress(event) {{
            if (event.key === 'Enter') {{
                sendMessage();
            }}
        }}
    </script>
</body>
</html>
    """


@app.get("/api/status")
async def status():
    return {
        "service": "Multi-Agent Chat System",
        "company": "SC COOL BITS SRL",
        "ceo": "Andrei",
        "ai_assistant": "Cursor AI Assistant",
        "contract_date": "2025-09-06",
        "port": 8101,
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "port": 8101}


if __name__ == "__main__":
    print("=" * 80)
    print("💬 COOLBITS.AI MULTI-AGENT CHAT SYSTEM")
    print("🏢 SC COOL BITS SRL - Port 8101")
    print("=" * 80)
    print("👤 CEO: Andrei")
    print("🤖 AI Assistant: Cursor AI Assistant")
    print("📅 Contract Date: 2025-09-06")
    print("🌐 Port: 8101")
    print("=" * 80)
    print("🔗 Chat Interface URL: http://localhost:8101")
    print("📋 API Status: http://localhost:8101/api/status")
    print("=" * 80)
    print("🌐 Starting Multi-Agent Chat System on port 8101")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8101, log_level="info")
