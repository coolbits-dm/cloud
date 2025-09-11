#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy Chat Web Interface
SC COOL BITS SRL - Modern chat interface with WebSocket support
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

# Import our internal systems
from andy_internal_chat_system import (
    andy_chat_system,
    AndyChatMessage,
    create_chat_session,
)

app = FastAPI(title="Andy Chat Interface", version="1.0.0")


# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.append(websocket)

        if session_id not in self.session_connections:
            self.session_connections[session_id] = []
        self.session_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        if session_id in self.session_connections:
            if websocket in self.session_connections[session_id]:
                self.session_connections[session_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast_to_session(self, message: str, session_id: str):
        if session_id in self.session_connections:
            for connection in self.session_connections[session_id]:
                try:
                    await connection.send_text(message)
                except:
                    # Remove broken connections
                    self.session_connections[session_id].remove(connection)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    """Main chat interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Andy - Personal 1:1 Agent</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .chat-container {
                width: 90%;
                max-width: 800px;
                height: 90vh;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
                overflow: hidden;
            }
            
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                text-align: center;
                position: relative;
            }
            
            .chat-header h1 {
                font-size: 24px;
                margin-bottom: 5px;
            }
            
            .chat-header p {
                font-size: 14px;
                opacity: 0.9;
            }
            
            .status-indicator {
                position: absolute;
                top: 20px;
                right: 20px;
                width: 12px;
                height: 12px;
                background: #4CAF50;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.5; }
                100% { opacity: 1; }
            }
            
            .chat-messages {
                flex: 1;
                padding: 20px;
                overflow-y: auto;
                background: #f8f9fa;
            }
            
            .message {
                margin-bottom: 15px;
                display: flex;
                align-items: flex-start;
            }
            
            .message.user {
                justify-content: flex-end;
            }
            
            .message.andy {
                justify-content: flex-start;
            }
            
            .message-content {
                max-width: 70%;
                padding: 12px 16px;
                border-radius: 18px;
                word-wrap: break-word;
                position: relative;
            }
            
            .message.user .message-content {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 5px;
            }
            
            .message.andy .message-content {
                background: white;
                color: #333;
                border: 1px solid #e0e0e0;
                border-bottom-left-radius: 5px;
            }
            
            .message-time {
                font-size: 11px;
                opacity: 0.7;
                margin-top: 5px;
            }
            
            .message.user .message-time {
                text-align: right;
            }
            
            .message.andy .message-time {
                text-align: left;
            }
            
            .chat-input-container {
                padding: 20px;
                background: white;
                border-top: 1px solid #e0e0e0;
            }
            
            .chat-input-wrapper {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            .chat-input {
                flex: 1;
                padding: 12px 16px;
                border: 2px solid #e0e0e0;
                border-radius: 25px;
                font-size: 14px;
                outline: none;
                transition: border-color 0.3s;
            }
            
            .chat-input:focus {
                border-color: #667eea;
            }
            
            .send-button {
                padding: 12px 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                transition: transform 0.2s;
            }
            
            .send-button:hover {
                transform: translateY(-2px);
            }
            
            .send-button:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }
            
            .typing-indicator {
                display: none;
                padding: 10px 16px;
                color: #666;
                font-style: italic;
                font-size: 14px;
            }
            
            .typing-indicator.show {
                display: block;
            }
            
            .session-info {
                position: absolute;
                top: 20px;
                left: 20px;
                font-size: 12px;
                opacity: 0.8;
            }
            
            .welcome-message {
                text-align: center;
                color: #666;
                font-style: italic;
                margin: 20px 0;
            }
            
            .system-message {
                background: #e3f2fd;
                color: #1976d2;
                padding: 10px 16px;
                border-radius: 10px;
                margin: 10px 0;
                font-size: 14px;
                text-align: center;
            }
            
            @media (max-width: 768px) {
                .chat-container {
                    width: 95%;
                    height: 95vh;
                }
                
                .message-content {
                    max-width: 85%;
                }
                
                .chat-header h1 {
                    font-size: 20px;
                }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <div class="status-indicator"></div>
                <div class="session-info" id="sessionInfo">Session: Loading...</div>
                <h1>🤖 Andy - Personal 1:1 Agent</h1>
                <p>Your personal AI assistant for CoolBits.ai</p>
            </div>
            
            <div class="chat-messages" id="chatMessages">
                <div class="welcome-message">
                    👋 Hello Andrei! I'm Andy, your personal 1:1 agent. I have full access to all project information and can help you with anything related to CoolBits.ai, cbLM.ai, system monitoring, or any other aspect of our ecosystem.
                </div>
            </div>
            
            <div class="typing-indicator" id="typingIndicator">
                Andy is typing...
            </div>
            
            <div class="chat-input-container">
                <div class="chat-input-wrapper">
                    <input type="text" id="messageInput" class="chat-input" placeholder="Type your message here..." autocomplete="off">
                    <button id="sendButton" class="send-button">Send</button>
                </div>
            </div>
        </div>

        <script>
            let sessionId = null;
            let websocket = null;
            let isConnected = false;
            
            // Initialize chat session
            async function initializeChat() {
                try {
                    const response = await fetch('/api/create-session', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    
                    const data = await response.json();
                    sessionId = data.session_id;
                    document.getElementById('sessionInfo').textContent = `Session: ${sessionId.substring(0, 8)}...`;
                    
                    // Connect WebSocket
                    connectWebSocket();
                } catch (error) {
                    console.error('Failed to initialize chat:', error);
                    showSystemMessage('Failed to initialize chat session. Please refresh the page.');
                }
            }
            
            // Connect to WebSocket
            function connectWebSocket() {
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const wsUrl = `${protocol}//${window.location.host}/ws/${sessionId}`;
                
                websocket = new WebSocket(wsUrl);
                
                websocket.onopen = function(event) {
                    isConnected = true;
                    console.log('WebSocket connected');
                    showSystemMessage('Connected to Andy! You can start chatting.');
                };
                
                websocket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
                
                websocket.onclose = function(event) {
                    isConnected = false;
                    console.log('WebSocket disconnected');
                    showSystemMessage('Connection lost. Attempting to reconnect...');
                    
                    // Attempt to reconnect after 3 seconds
                    setTimeout(() => {
                        if (!isConnected) {
                            connectWebSocket();
                        }
                    }, 3000);
                };
                
                websocket.onerror = function(error) {
                    console.error('WebSocket error:', error);
                    showSystemMessage('Connection error. Please refresh the page.');
                };
            }
            
            // Handle incoming messages
            function handleMessage(data) {
                if (data.type === 'message') {
                    addMessage(data.sender, data.content, data.timestamp);
                } else if (data.type === 'typing') {
                    showTypingIndicator(data.typing);
                } else if (data.type === 'system') {
                    showSystemMessage(data.message);
                }
            }
            
            // Add message to chat
            function addMessage(sender, content, timestamp) {
                const chatMessages = document.getElementById('chatMessages');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender.toLowerCase()}`;
                
                const time = new Date(timestamp).toLocaleTimeString();
                
                messageDiv.innerHTML = `
                    <div class="message-content">
                        ${content}
                        <div class="message-time">${time}</div>
                    </div>
                `;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Show system message
            function showSystemMessage(message) {
                const chatMessages = document.getElementById('chatMessages');
                const systemDiv = document.createElement('div');
                systemDiv.className = 'system-message';
                systemDiv.textContent = message;
                
                chatMessages.appendChild(systemDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Show typing indicator
            function showTypingIndicator(show) {
                const indicator = document.getElementById('typingIndicator');
                if (show) {
                    indicator.classList.add('show');
                } else {
                    indicator.classList.remove('show');
                }
            }
            
            // Send message
            function sendMessage() {
                const messageInput = document.getElementById('messageInput');
                const message = messageInput.value.trim();
                
                if (message && isConnected) {
                    // Add user message to chat
                    addMessage('User', message, new Date().toISOString());
                    
                    // Send message via WebSocket
                    websocket.send(JSON.stringify({
                        type: 'message',
                        content: message,
                        session_id: sessionId
                    }));
                    
                    // Clear input
                    messageInput.value = '';
                    
                    // Show typing indicator
                    showTypingIndicator(true);
                }
            }
            
            // Event listeners
            document.getElementById('sendButton').addEventListener('click', sendMessage);
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            // Initialize chat when page loads
            window.addEventListener('load', initializeChat);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data["type"] == "message":
                # Show typing indicator
                await manager.broadcast_to_session(
                    json.dumps({"type": "typing", "typing": True}), session_id
                )

                # Process message through Andy's chat system
                user_message = message_data["content"]

                # Create chat message
                chat_message = AndyChatMessage(
                    sender="User", content=user_message, message_type="text"
                )

                # Process through Andy's chat system
                andy_response = await andy_chat_system.process_message(
                    session_id, chat_message
                )

                # Hide typing indicator
                await manager.broadcast_to_session(
                    json.dumps({"type": "typing", "typing": False}), session_id
                )

                # Send Andy's response
                await manager.broadcast_to_session(
                    json.dumps(
                        {
                            "type": "message",
                            "sender": "Andy",
                            "content": andy_response.content,
                            "timestamp": andy_response.timestamp.isoformat(),
                        }
                    ),
                    session_id,
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, session_id)


@app.post("/api/create-session")
async def create_session():
    """Create new chat session"""
    session_id = create_chat_session()
    return {"session_id": session_id, "status": "created"}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Get chat session data"""
    session_data = andy_chat_system.get_session(session_id)
    if session_data:
        return {
            "session": session_data.get_context(),
            "messages": session_data.get_messages(),
            "status": "active",
        }
    return {"error": "Session not found"}


@app.get("/api/status")
async def get_status():
    """Get system status"""
    return andy_chat_system.get_system_status()


if __name__ == "__main__":
    print("=" * 80)
    print("🎨 ANDY CHAT WEB INTERFACE")
    print("🏢 SC COOL BITS SRL - Modern Chat Interface")
    print("=" * 80)
    print("👤 CEO: Andrei")
    print("🤖 AI Assistant: Andy - Personal 1:1 Agent")
    print("📅 Contract Date: 2025-09-06")
    print("=" * 80)
    print("🌐 Starting Andy Chat Interface on port 8101")
    print("=" * 80)
    print("🔗 Chat Interface URL: http://localhost:8101")
    print("📋 API Status: http://localhost:8101/api/status")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8101)
