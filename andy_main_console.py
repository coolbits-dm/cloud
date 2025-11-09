#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy Main Console
CoolBits.ai - Main console ChatGPT/Grok/Gemini style
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime
from typing import Dict, List
import uuid

# Import our internal systems
from andy_internal_chat_system import (
    andy_chat_system,
    AndyChatMessage,
    create_chat_session,
)
from andy_google_cloud_endpoint import (
    process_gcloud_request,
    process_gemini_request,
)
from andy_auto_engine import andy_auto_engine
from andy_kim_local_rag import local_rag_system, RAGAgent, RAGQuery
from andy_setup_console import andy_setup_console, SetupCategory
from andy_kim_routing import routing_system

app = FastAPI(title="Andy Main Console", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    async def broadcast_to_session(self, message: str, session_id: str):
        if session_id in self.session_connections:
            for connection in self.session_connections[session_id]:
                try:
                    await connection.send_text(message)
                except:
                    self.session_connections[session_id].remove(connection)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def get_andy_main_console(request: Request):
    """Andy Main Console - ChatGPT/Grok/Gemini Style"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Andy - Main Console | CoolBits.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
                background-color: #343541;
                color: #ffffff;
                height: 100vh;
                overflow: hidden;
            }
            
            .app-container {
                display: flex;
                height: 100vh;
                width: 100vw;
            }
            
            /* Sidebar - ChatGPT/Grok/Gemini Style */
            .sidebar {
                width: 260px;
                background-color: #202123;
                border-right: 1px solid #4d4d4f;
                display: flex;
                flex-direction: column;
                height: 100vh;
                overflow: hidden;
            }
            
            .sidebar-header {
                padding: 20px;
                border-bottom: 1px solid #4d4d4f;
            }
            
            .sidebar-title {
                font-size: 18px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 5px;
            }
            
            .sidebar-subtitle {
                font-size: 14px;
                color: #8e8ea0;
            }
            
            .console-badge {
                display: inline-block;
                background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
                margin-top: 8px;
            }
            
            .new-chat-button {
                width: 100%;
                padding: 12px 20px;
                background-color: transparent;
                border: 1px solid #4d4d4f;
                border-radius: 6px;
                color: #ffffff;
                font-size: 14px;
                cursor: pointer;
                margin: 20px;
                transition: background-color 0.2s;
            }
            
            .new-chat-button:hover {
                background-color: #2a2b32;
            }
            
            .chat-history {
                flex: 1;
                overflow-y: auto;
                padding: 0 20px;
            }
            
            .chat-item {
                padding: 12px 16px;
                margin: 4px 0;
                border-radius: 6px;
                cursor: pointer;
                transition: background-color 0.2s;
                font-size: 14px;
                color: #8e8ea0;
            }
            
            .chat-item:hover {
                background-color: #2a2b32;
            }
            
            .chat-item.active {
                background-color: #2a2b32;
                color: #ffffff;
            }
            
            .sidebar-footer {
                padding: 20px;
                border-top: 1px solid #4d4d4f;
            }
            
            .user-info {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                background-color: #2a2b32;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .user-avatar {
                width: 32px;
                height: 32px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                color: white;
            }
            
            /* Main Chat Area */
            .main-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                height: 100vh;
                background-color: #343541;
            }
            
            .chat-header {
                padding: 20px;
                border-bottom: 1px solid #4d4d4f;
                background-color: #343541;
            }
            
            .chat-title {
                font-size: 20px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 5px;
            }
            
            .chat-subtitle {
                font-size: 14px;
                color: #8e8ea0;
            }
            
            .platform-indicators {
                display: flex;
                gap: 8px;
                margin-top: 8px;
            }
            
            .platform-badge {
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: 600;
            }
            
            .platform-badge.localhost {
                background-color: #10a37f;
                color: white;
            }
            
            .platform-badge.google-cloud {
                background-color: #4285f4;
                color: white;
            }
            
            .platform-badge.openai {
                background-color: #00a67e;
                color: white;
            }
            
            .platform-badge.xai {
                background-color: #000000;
                color: white;
            }
            
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background-color: #343541;
            }
            
            .message {
                margin-bottom: 24px;
                display: flex;
                gap: 16px;
            }
            
            .message-avatar {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 14px;
                flex-shrink: 0;
            }
            
            .message.user .message-avatar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            
            .message.andy .message-avatar {
                background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
                color: white;
            }
            
            .message-content {
                flex: 1;
                background-color: #444654;
                padding: 16px;
                border-radius: 8px;
                line-height: 1.6;
                font-size: 14px;
                color: #ffffff;
            }
            
            .message.user .message-content {
                background-color: #2a2b32;
            }
            
            .message-time {
                font-size: 12px;
                color: #8e8ea0;
                margin-top: 8px;
            }
            
            .typing-indicator {
                display: none;
                margin-bottom: 24px;
                padding: 16px;
                background-color: #444654;
                border-radius: 8px;
                color: #8e8ea0;
                font-style: italic;
            }
            
            .typing-indicator.show {
                display: block;
            }
            
            .typing-dots {
                display: inline-block;
                animation: typing 1.4s infinite;
            }
            
            @keyframes typing {
                0%, 60%, 100% { opacity: 0.3; }
                30% { opacity: 1; }
            }
            
            /* Input Area */
            .input-container {
                padding: 20px;
                background-color: #343541;
                border-top: 1px solid #4d4d4f;
            }
            
            .input-wrapper {
                position: relative;
                max-width: 800px;
                margin: 0 auto;
            }
            
            .chat-input {
                width: 100%;
                padding: 16px 20px;
                background-color: #40414f;
                border: 1px solid #4d4d4f;
                border-radius: 12px;
                color: #ffffff;
                font-size: 14px;
                outline: none;
                resize: none;
                min-height: 24px;
                max-height: 120px;
                line-height: 1.5;
            }
            
            .chat-input:focus {
                border-color: #10a37f;
            }
            
            .chat-input::placeholder {
                color: #8e8ea0;
            }
            
            .send-button {
                position: absolute;
                right: 8px;
                top: 50%;
                transform: translateY(-50%);
                width: 32px;
                height: 32px;
                background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
                border: none;
                border-radius: 6px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 16px;
                transition: transform 0.2s;
            }
            
            .send-button:hover {
                transform: translateY(-50%) scale(1.05);
            }
            
            .send-button:disabled {
                opacity: 0.5;
                cursor: not-allowed;
                transform: translateY(-50%);
            }
            
            /* Welcome Message */
            .welcome-message {
                text-align: center;
                padding: 40px 20px;
                color: #8e8ea0;
            }
            
            .welcome-title {
                font-size: 24px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 16px;
            }
            
            .welcome-subtitle {
                font-size: 16px;
                margin-bottom: 24px;
            }
            
            .welcome-features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin-top: 32px;
            }
            
            .feature-card {
                background-color: #2a2b32;
                padding: 20px;
                border-radius: 8px;
                border: 1px solid #4d4d4f;
            }
            
            .feature-title {
                font-size: 16px;
                font-weight: 600;
                color: #ffffff;
                margin-bottom: 8px;
            }
            
            .feature-description {
                font-size: 14px;
                color: #8e8ea0;
            }
            
            /* Scrollbar Styling */
            ::-webkit-scrollbar {
                width: 6px;
            }
            
            ::-webkit-scrollbar-track {
                background: #2a2b32;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #4d4d4f;
                border-radius: 3px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #6d6d6f;
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .sidebar {
                    width: 100%;
                    position: absolute;
                    z-index: 1000;
                    transform: translateX(-100%);
                    transition: transform 0.3s;
                }
                
                .sidebar.open {
                    transform: translateX(0);
                }
                
                .main-content {
                    width: 100%;
                }
                
                .welcome-features {
                    grid-template-columns: 1fr;
                }
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Sidebar -->
            <div class="sidebar" id="sidebar">
                <div class="sidebar-header">
                    <div class="sidebar-title">🤖 Andy</div>
                    <div class="sidebar-subtitle">Main Console</div>
                    <div class="console-badge">Port 8102</div>
                </div>
                
                <button class="new-chat-button" onclick="startNewChat()">
                    + New Chat
                </button>
                
                <div class="chat-history" id="chatHistory">
                    <!-- Chat history will be populated here -->
                </div>
                
                <div class="sidebar-footer">
                    <div class="user-info">
                        <div class="user-avatar">A</div>
                        <div>
                            <div style="font-weight: 600;">Andrei</div>
                            <div style="font-size: 12px; color: #8e8ea0;">CEO, CoolBits.ai</div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Main Content -->
            <div class="main-content">
                <div class="chat-header">
                    <div class="chat-title" id="chatTitle">New Chat</div>
                    <div class="chat-subtitle" id="chatSubtitle">Start a conversation with Andy</div>
                    <div class="platform-indicators">
                        <div class="platform-badge localhost">Localhost:8101</div>
                        <div class="platform-badge google-cloud">Google Cloud</div>
                        <div class="platform-badge openai">OpenAI</div>
                        <div class="platform-badge xai">xAI</div>
                    </div>
                </div>
                
                <div class="chat-messages" id="chatMessages">
                    <div class="welcome-message" id="welcomeMessage">
                        <div class="welcome-title">Welcome to Andy Main Console</div>
                        <div class="welcome-subtitle">Your personal 1:1 AI agent across all platforms</div>
                        
                        <div class="welcome-features">
                            <div class="feature-card">
                                <div class="feature-title">🏠 Localhost:8101</div>
                                <div class="feature-description">Main Andy pillar - oPython agent execution and root collaboration</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-title">☁️ Google Cloud</div>
                                <div class="feature-description">Gemini motor integration with full Google Cloud CLI access</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-title">🤖 OpenAI Integration</div>
                                <div class="feature-description">Andy's OpenAI key for ChatGPT tab and API access</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-title">🚀 xAI Integration</div>
                                <div class="feature-description">Andy's xAI key for Grok tab and API access</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-title">📱 Social Media</div>
                                <div class="feature-description">Facebook, Instagram, TikTok integration and management</div>
                            </div>
                            <div class="feature-card">
                                <div class="feature-title">🛠️ Marketing Tools</div>
                                <div class="feature-description">All possible marketing, development, and business tools</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="typing-indicator" id="typingIndicator">
                    Andy is typing<span class="typing-dots">...</span>
                </div>
                
                <div class="input-container">
                    <div class="input-wrapper">
                        <textarea 
                            id="messageInput" 
                            class="chat-input" 
                            placeholder="Message Andy across all platforms..." 
                            rows="1"
                            autocomplete="off"
                        ></textarea>
                        <button id="sendButton" class="send-button" onclick="sendMessage()">
                            ➤
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            let sessionId = null;
            let websocket = null;
            let isConnected = false;
            let currentChatTitle = "New Chat";
            
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
                    hideWelcomeMessage();
                };
                
                websocket.onmessage = function(event) {
                    const data = JSON.parse(event.data);
                    handleMessage(data);
                };
                
                websocket.onclose = function(event) {
                    isConnected = false;
                    console.log('WebSocket disconnected');
                    
                    // Attempt to reconnect after 3 seconds
                    setTimeout(() => {
                        if (!isConnected) {
                            connectWebSocket();
                        }
                    }, 3000);
                };
                
                websocket.onerror = function(error) {
                    console.error('WebSocket error:', error);
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
                const avatar = sender === 'User' ? 'A' : '🤖';
                
                messageDiv.innerHTML = `
                    <div class="message-avatar">${avatar}</div>
                    <div class="message-content">
                        ${content}
                        <div class="message-time">${time}</div>
                    </div>
                `;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
                
                // Update chat title if it's the first message
                if (currentChatTitle === "New Chat" && sender === 'User') {
                    currentChatTitle = content.substring(0, 50) + (content.length > 50 ? '...' : '');
                    document.getElementById('chatTitle').textContent = currentChatTitle;
                    addToChatHistory(currentChatTitle);
                }
            }
            
            // Show system message
            function showSystemMessage(message) {
                const chatMessages = document.getElementById('chatMessages');
                const systemDiv = document.createElement('div');
                systemDiv.style.cssText = 'text-align: center; color: #8e8ea0; font-style: italic; margin: 20px 0;';
                systemDiv.textContent = message;
                
                chatMessages.appendChild(systemDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Show/hide typing indicator
            function showTypingIndicator(show) {
                const indicator = document.getElementById('typingIndicator');
                if (show) {
                    indicator.classList.add('show');
                } else {
                    indicator.classList.remove('show');
                }
            }
            
            // Hide welcome message
            function hideWelcomeMessage() {
                const welcomeMessage = document.getElementById('welcomeMessage');
                if (welcomeMessage) {
                    welcomeMessage.style.display = 'none';
                }
            }
            
            // Add to chat history
            function addToChatHistory(title) {
                const chatHistory = document.getElementById('chatHistory');
                const chatItem = document.createElement('div');
                chatItem.className = 'chat-item';
                chatItem.textContent = title;
                chatItem.onclick = () => loadChat(title);
                
                chatHistory.insertBefore(chatItem, chatHistory.firstChild);
            }
            
            // Load chat
            function loadChat(title) {
                // Remove active class from all items
                document.querySelectorAll('.chat-item').forEach(item => {
                    item.classList.remove('active');
                });
                
                // Add active class to clicked item
                event.target.classList.add('active');
                
                // Update chat title
                currentChatTitle = title;
                document.getElementById('chatTitle').textContent = title;
            }
            
            // Start new chat
            function startNewChat() {
                // Clear current chat
                document.getElementById('chatMessages').innerHTML = '';
                document.getElementById('welcomeMessage').style.display = 'block';
                
                // Reset title
                currentChatTitle = "New Chat";
                document.getElementById('chatTitle').textContent = currentChatTitle;
                document.getElementById('chatSubtitle').textContent = "Start a conversation with Andy";
                
                // Create new session
                initializeChat();
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
            
            // Auto-resize textarea
            function autoResize(textarea) {
                textarea.style.height = 'auto';
                textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
            }
            
            // Event listeners
            document.getElementById('sendButton').addEventListener('click', sendMessage);
            document.getElementById('messageInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });
            
            document.getElementById('messageInput').addEventListener('input', function() {
                autoResize(this);
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

                # Process message through Andy's Auto Engine first
                auto_context = await andy_auto_engine.process_prompt(
                    "andrei", session_id, user_message
                )

                # Create chat message with Auto Engine response
                chat_message = AndyChatMessage(
                    sender="User",
                    content=user_message,
                    message_type="text",
                    metadata={
                        "auto_processing": {
                            "level": auto_context.processing_level.value,
                            "confidence": auto_context.confidence_score,
                            "auto_response": auto_context.response,
                        }
                    },
                )

                # Process through Andy's chat system with Auto context
                andy_response = await andy_chat_system.process_message(
                    session_id, chat_message
                )

                # Enhance response with Auto Engine context
                enhanced_response = f"{andy_response.content}\n\n🤖 Auto Engine Analysis:\nLevel: {auto_context.processing_level.value}\nConfidence: {auto_context.confidence_score:.2f}\n\n{auto_context.response}"

                # Hide typing indicator
                await manager.broadcast_to_session(
                    json.dumps({"type": "typing", "typing": False}), session_id
                )

                # Send Andy's enhanced response
                await manager.broadcast_to_session(
                    json.dumps(
                        {
                            "type": "message",
                            "sender": "Andy",
                            "content": enhanced_response,
                            "timestamp": andy_response.timestamp.isoformat(),
                            "auto_processing": {
                                "level": auto_context.processing_level.value,
                                "confidence": auto_context.confidence_score,
                            },
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


@app.post("/api/gcloud")
async def gcloud_endpoint(request: Request):
    """Google Cloud CLI endpoint"""
    data = await request.json()
    result = await process_gcloud_request(data)
    return result


@app.post("/api/gemini")
async def gemini_endpoint(request: Request):
    """Gemini CLI endpoint"""
    data = await request.json()
    result = await process_gemini_request(data)
    return result


@app.post("/api/auto-process")
async def auto_process_request(request: Request):
    """Auto process request through Andy Auto Engine"""
    try:
        data = await request.json()
        user_id = data.get("user_id", "andrei")
        session_id = data.get("session_id", str(uuid.uuid4()))
        prompt = data.get("prompt", "")

        if not prompt:
            return {"error": "Prompt is required"}

        # Process through Auto Engine
        context = await andy_auto_engine.process_prompt(user_id, session_id, prompt)

        return {
            "success": True,
            "response": context.response,
            "processing_level": context.processing_level.value,
            "confidence_score": context.confidence_score,
            "metadata": context.metadata,
            "session_id": session_id,
        }

    except Exception as e:
        return {"error": f"Auto processing failed: {str(e)}"}


@app.get("/api/auto-stats")
async def get_auto_stats():
    """Get Auto Engine processing statistics"""
    try:
        stats = await andy_auto_engine.get_processing_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": f"Failed to get stats: {str(e)}"}


@app.post("/api/auto-knowledge")
async def add_auto_knowledge(request: Request):
    """Add knowledge to Auto Engine"""
    try:
        data = await request.json()
        topic = data.get("topic", "")
        content = data.get("content", "")
        source = data.get("source", "manual")
        relevance_score = data.get("relevance_score", 0.8)

        if not topic or not content:
            return {"error": "Topic and content are required"}

        await andy_auto_engine.add_knowledge(topic, content, source, relevance_score)

        return {
            "success": True,
            "message": "Knowledge added successfully",
            "topic": topic,
        }

    except Exception as e:
        return {"error": f"Failed to add knowledge: {str(e)}"}


@app.get("/api/auto-search")
async def search_auto_knowledge(query: str = ""):
    """Search Auto Engine knowledge base"""
    try:
        if not query:
            return {"error": "Query parameter is required"}

        results = await andy_auto_engine.search_knowledge(query)

        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results),
        }

    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


@app.post("/api/rag-query")
async def rag_query_endpoint(request: Request):
    """RAG query endpoint"""
    try:
        data = await request.json()
        query = data.get("query", "")
        agent = data.get("agent", "andy")
        max_results = data.get("max_results", 5)
        similarity_threshold = data.get("similarity_threshold", 0.7)

        if not query:
            return {"error": "Query is required"}

        # Convert agent string to enum
        rag_agent = RAGAgent.ANDY if agent.lower() == "andy" else RAGAgent.KIM

        # Create RAG query
        rag_query = RAGQuery(
            query=query,
            agent=rag_agent,
            context={"api_request": True},
            max_results=max_results,
            similarity_threshold=similarity_threshold,
        )

        # Execute RAG query
        results = await local_rag_system.query_rag(rag_query)

        # Format results
        formatted_results = [
            {
                "id": result.document.id,
                "content": result.document.content,
                "metadata": result.document.metadata,
                "similarity_score": result.similarity_score,
                "relevance_score": result.relevance_score,
                "agent": result.document.agent.value,
            }
            for result in results
        ]

        return {
            "success": True,
            "query": query,
            "agent": agent,
            "results": formatted_results,
            "count": len(formatted_results),
        }

    except Exception as e:
        return {"error": f"RAG query failed: {str(e)}"}


@app.get("/api/rag-stats")
async def get_rag_stats():
    """Get RAG system statistics"""
    try:
        stats = await local_rag_system.get_rag_stats()
        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": f"Failed to get RAG stats: {str(e)}"}


@app.post("/api/rag-add-knowledge")
async def add_rag_knowledge(request: Request):
    """Add knowledge to RAG system"""
    try:
        data = await request.json()
        content = data.get("content", "")
        metadata = data.get("metadata", {})
        agent = data.get("agent", "andy")
        category = data.get("category", "general")

        if not content:
            return {"error": "Content is required"}

        # Convert agent string to enum
        rag_agent = RAGAgent.ANDY if agent.lower() == "andy" else RAGAgent.KIM

        # Add to RAG system
        local_rag_system.add_document(
            content=content, metadata=metadata, agent=rag_agent, category=category
        )

        return {
            "success": True,
            "message": "Knowledge added successfully",
            "agent": agent,
            "category": category,
        }

    except Exception as e:
        return {"error": f"Failed to add knowledge: {str(e)}"}


@app.get("/api/rag-search")
async def search_rag_knowledge(
    query: str = "", agent: str = "andy", max_results: int = 5
):
    """Search RAG knowledge base"""
    try:
        if not query:
            return {"error": "Query parameter is required"}

        # Convert agent string to enum
        rag_agent = RAGAgent.ANDY if agent.lower() == "andy" else RAGAgent.KIM

        # Search knowledge
        results = await local_rag_system.search_knowledge(query, rag_agent, max_results)

        return {
            "success": True,
            "query": query,
            "agent": agent,
            "results": results,
            "count": len(results),
        }

    except Exception as e:
        return {"error": f"Search failed: {str(e)}"}


@app.get("/api/setup-status")
async def get_setup_status():
    """Get setup console status"""
    try:
        status = await andy_setup_console.get_setup_status()
        return {
            "success": True,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": f"Failed to get setup status: {str(e)}"}


@app.get("/api/setup-tasks")
async def get_setup_tasks(category: str = ""):
    """Get setup tasks"""
    try:
        if category:
            # Get tasks by category
            setup_category = SetupCategory(category)
            tasks = await andy_setup_console.get_tasks_by_category(setup_category)
        else:
            # Get all tasks
            tasks = []
            for cat in SetupCategory:
                cat_tasks = await andy_setup_console.get_tasks_by_category(cat)
                tasks.extend(cat_tasks)

        return {
            "success": True,
            "category": category or "all",
            "tasks": tasks,
            "count": len(tasks),
        }
    except Exception as e:
        return {"error": f"Failed to get setup tasks: {str(e)}"}


@app.post("/api/setup-execute")
async def execute_setup_task(request: Request):
    """Execute a setup task"""
    try:
        data = await request.json()
        task_id = data.get("task_id", "")

        if not task_id:
            return {"error": "Task ID is required"}

        # Execute task
        result = await andy_setup_console.execute_task(task_id)

        return {
            "success": True,
            "task_id": task_id,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"error": f"Failed to execute task: {str(e)}"}


@app.post("/api/setup-reset")
async def reset_setup():
    """Reset all setup tasks"""
    try:
        await andy_setup_console.reset_setup()

        return {
            "success": True,
            "message": "Setup reset completed",
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        return {"error": f"Failed to reset setup: {str(e)}"}


@app.get("/api/setup-report")
async def get_setup_report():
    """Get setup report"""
    try:
        report = await andy_setup_console.export_setup_report()

        return {"success": True, "report": report}

    except Exception as e:
        return {"error": f"Failed to get setup report: {str(e)}"}


@app.get("/routing-info")
async def get_routing_info():
    """Get complete routing information"""
    try:
        info = routing_system.get_routing_info()
        return {
            "success": True,
            "routing_info": info,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"error": f"Failed to get routing info: {str(e)}"}


@app.get("/andy/setup")
async def andy_setup_console():
    """Andy Setup Console"""
    return await setup_console_page("andy")


@app.get("/andy/chat")
async def andy_chat_interface():
    """Andy Chat Interface"""
    return await chat_interface_page("andy")


@app.get("/andy/model/auto")
async def andy_auto_model():
    """Andy Auto Model (Default)"""
    return await model_interface_page("andy", "auto")


@app.get("/andy/model/xai/grok")
async def andy_xai_grok():
    """Andy XAI Grok Model"""
    return await model_interface_page("andy", "xai", "grok")


@app.get("/andy/model/openai/gpt")
async def andy_openai_gpt():
    """Andy OpenAI GPT Model"""
    return await model_interface_page("andy", "openai", "gpt")


@app.get("/andy/model/google/gemini")
async def andy_google_gemini():
    """Andy Google Gemini Model"""
    return await model_interface_page("andy", "google", "gemini")


@app.get("/andy/model/cursor/ocursor")
async def andy_cursor_ocursor():
    """Andy Cursor oCursor Model"""
    return await model_interface_page("andy", "cursor", "ocursor")


@app.get("/kim/setup")
async def kim_setup_console():
    """Kim Setup Console"""
    return await setup_console_page("kim")


@app.get("/kim/chat")
async def kim_chat_interface():
    """Kim Chat Interface"""
    return await chat_interface_page("kim")


@app.get("/kim/reasoning")
async def kim_reasoning_interface():
    """Kim Reasoning Interface"""
    return await reasoning_interface_page("kim")


@app.get("/kim/model/auto")
async def kim_auto_model():
    """Kim Auto Model (Default)"""
    return await model_interface_page("kim", "auto")


@app.get("/kim/model/xai/grok")
async def kim_xai_grok():
    """Kim XAI Grok Model"""
    return await model_interface_page("kim", "xai", "grok")


@app.get("/kim/model/openai/gpt")
async def kim_openai_gpt():
    """Kim OpenAI GPT Model"""
    return await model_interface_page("kim", "openai", "gpt")


@app.get("/kim/model/google/gemini")
async def kim_google_gemini():
    """Kim Google Gemini Model"""
    return await model_interface_page("kim", "google", "gemini")


@app.get("/kim/model/cursor/ocursor")
async def kim_cursor_ocursor():
    """Kim Cursor oCursor Model"""
    return await model_interface_page("kim", "cursor", "ocursor")


async def setup_console_page(agent: str):
    """Generic setup console page"""
    html_content = (
        f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent.title()} Setup Console - CoolBits.ai</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .header p {{
                font-size: 1.2rem;
                opacity: 0.9;
            }}
            
            .agent-info {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
                text-align: center;
            }}
            
            .agent-name {{
                font-size: 2rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 10px;
            }}
            
            .agent-description {{
                color: #718096;
                font-size: 1.1rem;
            }}
            
            .navigation {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            
            .nav-card {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease;
                cursor: pointer;
            }}
            
            .nav-card:hover {{
                transform: translateY(-5px);
            }}
            
            .nav-icon {{
                font-size: 2rem;
                margin-bottom: 15px;
            }}
            
            .nav-title {{
                font-size: 1.2rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 10px;
            }}
            
            .nav-description {{
                color: #718096;
                font-size: 0.9rem;
            }}
            
            .btn {{
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
                margin: 5px;
            }}
            
            .btn-primary {{
                background: #667eea;
                color: white;
            }}
            
            .btn-primary:hover {{
                background: #5a67d8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 {agent.title()} Setup Console</h1>
                <p>CoolBits.ai - Configuration and Setup Management</p>
            </div>
            
            <div class="agent-info">
                <div class="agent-name">{agent.title()}</div>
                <div class="agent-description">
                    {"Personal AI Assistant" if agent == "andy" else "Reasoning and Analysis Partner"}
                </div>
            </div>
            
            <div class="navigation">
                <div class="nav-card" onclick="window.location.href='/{agent}/chat'">
                    <div class="nav-icon">💬</div>
                    <div class="nav-title">Chat Interface</div>
                    <div class="nav-description">Start chatting with {agent.title()}</div>
                </div>
                
                <div class="nav-card" onclick="window.location.href='/{agent}/model/auto'">
                    <div class="nav-icon">🤖</div>
                    <div class="nav-title">Auto Model</div>
                    <div class="nav-description">Default intelligent model</div>
                </div>
                
                """
        + (
            """
                <div class="nav-card" onclick="window.location.href='/kim/reasoning'">
                    <div class="nav-icon">🧠</div>
                    <div class="nav-title">Reasoning</div>
                    <div class="nav-description">Advanced reasoning interface</div>
                </div>
                """
            if agent == "kim"
            else ""
        )
        + """
                
                <div class="nav-card" onclick="window.location.href='/{agent}/model/xai/grok'">
                    <div class="nav-icon">⚡</div>
                    <div class="nav-title">XAI Grok</div>
                    <div class="nav-description">Real-time processing</div>
                </div>
                
                <div class="nav-card" onclick="window.location.href='/{agent}/model/openai/gpt'">
                    <div class="nav-icon">🔮</div>
                    <div class="nav-title">OpenAI GPT</div>
                    <div class="nav-description">General purpose AI</div>
                </div>
                
                <div class="nav-card" onclick="window.location.href='/{agent}/model/google/gemini'">
                    <div class="nav-icon">💎</div>
                    <div class="nav-title">Google Gemini</div>
                    <div class="nav-description">Multimodal processing</div>
                </div>
                
                <div class="nav-card" onclick="window.location.href='/{agent}/model/cursor/ocursor'">
                    <div class="nav-icon">🎯</div>
                    <div class="nav-title">Cursor oCursor</div>
                    <div class="nav-description">Development focused</div>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    )
    return HTMLResponse(content=html_content)


async def chat_interface_page(agent: str):
    """Generic chat interface page"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent.title()} Chat - CoolBits.ai</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .chat-container {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                min-height: 500px;
            }}
            
            .chat-messages {{
                height: 400px;
                overflow-y: auto;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                background: #f7fafc;
            }}
            
            .message {{
                margin-bottom: 15px;
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 80%;
            }}
            
            .message.user {{
                background: #667eea;
                color: white;
                margin-left: auto;
            }}
            
            .message.assistant {{
                background: #e2e8f0;
                color: #2d3748;
            }}
            
            .input-container {{
                display: flex;
                gap: 10px;
            }}
            
            .message-input {{
                flex: 1;
                padding: 15px;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
            }}
            
            .send-btn {{
                padding: 15px 25px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
            }}
            
            .send-btn:hover {{
                background: #5a67d8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💬 {agent.title()} Chat Interface</h1>
                <p>CoolBits.ai - Chat with {agent.title()}</p>
            </div>
            
            <div class="chat-container">
                <div class="chat-messages" id="chatMessages">
                    <div class="message assistant">
                        Hello! I'm {agent.title()}, your AI assistant. How can I help you today?
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" class="message-input" id="messageInput" placeholder="Type your message here...">
                    <button class="send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <script>
            function sendMessage() {{
                const input = document.getElementById('messageInput');
                const messages = document.getElementById('chatMessages');
                
                if (input.value.trim()) {{
                    // Add user message
                    const userMessage = document.createElement('div');
                    userMessage.className = 'message user';
                    userMessage.textContent = input.value;
                    messages.appendChild(userMessage);
                    
                    // Add assistant response
                    const assistantMessage = document.createElement('div');
                    assistantMessage.className = 'message assistant';
                    assistantMessage.textContent = `{agent.title()} is processing your message...`;
                    messages.appendChild(assistantMessage);
                    
                    // Clear input
                    input.value = '';
                    
                    // Scroll to bottom
                    messages.scrollTop = messages.scrollHeight;
                }}
            }}
            
            document.getElementById('messageInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    sendMessage();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


async def reasoning_interface_page(agent: str):
    """Kim reasoning interface page"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent.title()} Reasoning - CoolBits.ai</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .reasoning-container {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                min-height: 500px;
            }}
            
            .reasoning-steps {{
                height: 400px;
                overflow-y: auto;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                background: #f7fafc;
            }}
            
            .step {{
                margin-bottom: 15px;
                padding: 15px;
                border-radius: 10px;
                background: #e2e8f0;
                border-left: 4px solid #667eea;
            }}
            
            .step-title {{
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 5px;
            }}
            
            .step-content {{
                color: #718096;
            }}
            
            .input-container {{
                display: flex;
                gap: 10px;
            }}
            
            .reasoning-input {{
                flex: 1;
                padding: 15px;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
            }}
            
            .analyze-btn {{
                padding: 15px 25px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
            }}
            
            .analyze-btn:hover {{
                background: #5a67d8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 {agent.title()} Reasoning Interface</h1>
                <p>CoolBits.ai - Advanced Reasoning and Analysis</p>
            </div>
            
            <div class="reasoning-container">
                <div class="reasoning-steps" id="reasoningSteps">
                    <div class="step">
                        <div class="step-title">Step 1: Problem Analysis</div>
                        <div class="step-content">Ready to analyze complex problems and provide strategic reasoning.</div>
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" class="reasoning-input" id="reasoningInput" placeholder="Describe the problem or situation to analyze...">
                    <button class="analyze-btn" onclick="analyzeProblem()">Analyze</button>
                </div>
            </div>
        </div>
        
        <script>
            function analyzeProblem() {{
                const input = document.getElementById('reasoningInput');
                const steps = document.getElementById('reasoningSteps');
                
                if (input.value.trim()) {{
                    // Add analysis steps
                    const steps_data = [
                        {{
                            title: "Problem Understanding",
                            content: `Analyzing: "${{input.value}}"`
                        }},
                        {{
                            title: "Context Analysis",
                            content: "Examining context and constraints..."
                        }},
                        {{
                            title: "Strategic Thinking",
                            content: "Developing strategic approach..."
                        }},
                        {{
                            title: "Recommendation",
                            content: "Providing comprehensive recommendation..."
                        }}
                    ];
                    
                    steps.innerHTML = '';
                    
                    steps_data.forEach((step, index) => {{
                        const stepElement = document.createElement('div');
                        stepElement.className = 'step';
                        stepElement.innerHTML = `
                            <div class="step-title">Step ${{index + 1}}: ${{step.title}}</div>
                            <div class="step-content">${{step.content}}</div>
                        `;
                        steps.appendChild(stepElement);
                    }});
                    
                    // Clear input
                    input.value = '';
                }}
            }}
            
            document.getElementById('reasoningInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    analyzeProblem();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


async def model_interface_page(agent: str, provider: str, model_type: str = None):
    """Generic model interface page"""
    model_name = (
        f"{provider.title()} {model_type.title()}"
        if model_type
        else f"{provider.title()} Model"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{agent.title()} {model_name} - CoolBits.ai</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }}
            
            .header h1 {{
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }}
            
            .model-container {{
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                min-height: 500px;
            }}
            
            .model-info {{
                text-align: center;
                margin-bottom: 30px;
                padding: 20px;
                background: #f7fafc;
                border-radius: 10px;
            }}
            
            .model-name {{
                font-size: 1.5rem;
                font-weight: 600;
                color: #2d3748;
                margin-bottom: 10px;
            }}
            
            .model-description {{
                color: #718096;
            }}
            
            .chat-container {{
                height: 400px;
                overflow-y: auto;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                padding: 20px;
                margin-bottom: 20px;
                background: #f7fafc;
            }}
            
            .message {{
                margin-bottom: 15px;
                padding: 10px 15px;
                border-radius: 10px;
                max-width: 80%;
            }}
            
            .message.user {{
                background: #667eea;
                color: white;
                margin-left: auto;
            }}
            
            .message.assistant {{
                background: #e2e8f0;
                color: #2d3748;
            }}
            
            .input-container {{
                display: flex;
                gap: 10px;
            }}
            
            .message-input {{
                flex: 1;
                padding: 15px;
                border: 1px solid #e2e8f0;
                border-radius: 10px;
                font-size: 1rem;
            }}
            
            .send-btn {{
                padding: 15px 25px;
                background: #667eea;
                color: white;
                border: none;
                border-radius: 10px;
                font-weight: 600;
                cursor: pointer;
            }}
            
            .send-btn:hover {{
                background: #5a67d8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 {agent.title()} {model_name}</h1>
                <p>CoolBits.ai - {model_name} Interface</p>
            </div>
            
            <div class="model-container">
                <div class="model-info">
                    <div class="model-name">{model_name}</div>
                    <div class="model-description">
                        {"Intelligent model selection based on context" if provider == "auto" else f"{provider.title()} {model_type.title() if model_type else 'Model'} for {agent.title()}"}
                    </div>
                </div>
                
                <div class="chat-container" id="chatMessages">
                    <div class="message assistant">
                        Hello! I'm {agent.title()} using {model_name}. How can I help you today?
                    </div>
                </div>
                
                <div class="input-container">
                    <input type="text" class="message-input" id="messageInput" placeholder="Type your message here...">
                    <button class="send-btn" onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <script>
            function sendMessage() {{
                const input = document.getElementById('messageInput');
                const messages = document.getElementById('chatMessages');
                
                if (input.value.trim()) {{
                    // Add user message
                    const userMessage = document.createElement('div');
                    userMessage.className = 'message user';
                    userMessage.textContent = input.value;
                    messages.appendChild(userMessage);
                    
                    // Add assistant response
                    const assistantMessage = document.createElement('div');
                    assistantMessage.className = 'message assistant';
                    assistantMessage.textContent = `{agent.title()} ({model_name}) is processing your message...`;
                    messages.appendChild(assistantMessage);
                    
                    // Clear input
                    input.value = '';
                    
                    // Scroll to bottom
                    messages.scrollTop = messages.scrollHeight;
                }}
            }}
            
            document.getElementById('messageInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') {{
                    sendMessage();
                }}
            }});
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/setup")
async def legacy_setup_console_page():
    """Setup console page"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Andy Setup Console - CoolBits.ai</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 40px;
                color: white;
            }
            
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .header p {
                font-size: 1.2rem;
                opacity: 0.9;
            }
            
            .setup-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }
            
            .setup-card {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                transition: transform 0.3s ease;
            }
            
            .setup-card:hover {
                transform: translateY(-5px);
            }
            
            .card-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 15px;
            }
            
            .card-title {
                font-size: 1.3rem;
                font-weight: 600;
                color: #2d3748;
            }
            
            .status-badge {
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
                text-transform: uppercase;
            }
            
            .status-not-started { background: #e2e8f0; color: #4a5568; }
            .status-in-progress { background: #fef5e7; color: #d69e2e; }
            .status-completed { background: #f0fff4; color: #38a169; }
            .status-failed { background: #fed7d7; color: #e53e3e; }
            
            .card-description {
                color: #718096;
                margin-bottom: 20px;
                line-height: 1.5;
            }
            
            .card-actions {
                display: flex;
                gap: 10px;
            }
            
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                text-align: center;
            }
            
            .btn-primary {
                background: #667eea;
                color: white;
            }
            
            .btn-primary:hover {
                background: #5a67d8;
            }
            
            .btn-secondary {
                background: #e2e8f0;
                color: #4a5568;
            }
            
            .btn-secondary:hover {
                background: #cbd5e0;
            }
            
            .btn-success {
                background: #38a169;
                color: white;
            }
            
            .btn-success:hover {
                background: #2f855a;
            }
            
            .progress-section {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }
            
            .progress-bar {
                width: 100%;
                height: 20px;
                background: #e2e8f0;
                border-radius: 10px;
                overflow: hidden;
                margin: 15px 0;
            }
            
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, #667eea, #764ba2);
                transition: width 0.3s ease;
                border-radius: 10px;
            }
            
            .progress-text {
                text-align: center;
                font-weight: 600;
                color: #2d3748;
            }
            
            .actions-section {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                text-align: center;
            }
            
            .actions-section h3 {
                margin-bottom: 20px;
                color: #2d3748;
            }
            
            .action-buttons {
                display: flex;
                gap: 15px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .loading {
                display: none;
                text-align: center;
                margin: 20px 0;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .result-section {
                background: white;
                border-radius: 15px;
                padding: 25px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                margin-top: 20px;
                display: none;
            }
            
            .result-section h3 {
                margin-bottom: 15px;
                color: #2d3748;
            }
            
            .result-content {
                background: #f7fafc;
                padding: 15px;
                border-radius: 8px;
                font-family: monospace;
                white-space: pre-wrap;
                max-height: 300px;
                overflow-y: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔧 Andy Setup Console</h1>
                <p>CoolBits.ai - Configuration and Setup Management</p>
            </div>
            
            <div class="progress-section">
                <h3>Setup Progress</h3>
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                </div>
                <div class="progress-text" id="progressText">0% Complete</div>
            </div>
            
            <div class="setup-grid" id="setupGrid">
                <!-- Setup cards will be loaded here -->
            </div>
            
            <div class="actions-section">
                <h3>Setup Actions</h3>
                <div class="action-buttons">
                    <button class="btn btn-primary" onclick="executeAllTasks()">Execute All Tasks</button>
                    <button class="btn btn-secondary" onclick="resetSetup()">Reset Setup</button>
                    <button class="btn btn-success" onclick="generateReport()">Generate Report</button>
                </div>
            </div>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Processing setup tasks...</p>
            </div>
            
            <div class="result-section" id="resultSection">
                <h3>Task Result</h3>
                <div class="result-content" id="resultContent"></div>
            </div>
        </div>
        
        <script>
            let setupTasks = [];
            
            async function loadSetupStatus() {
                try {
                    const response = await fetch('/api/setup-status');
                    const data = await response.json();
                    
                    if (data.success) {
                        updateProgress(data.status);
                    }
                } catch (error) {
                    console.error('Failed to load setup status:', error);
                }
            }
            
            async function loadSetupTasks() {
                try {
                    const response = await fetch('/api/setup-tasks');
                    const data = await response.json();
                    
                    if (data.success) {
                        setupTasks = data.tasks;
                        renderSetupCards();
                    }
                } catch (error) {
                    console.error('Failed to load setup tasks:', error);
                }
            }
            
            function updateProgress(status) {
                const progressFill = document.getElementById('progressFill');
                const progressText = document.getElementById('progressText');
                
                progressFill.style.width = status.progress_percentage + '%';
                progressText.textContent = `${status.progress_percentage.toFixed(1)}% Complete (${status.completed_tasks}/${status.total_tasks} tasks)`;
            }
            
            function renderSetupCards() {
                const grid = document.getElementById('setupGrid');
                grid.innerHTML = '';
                
                setupTasks.forEach(task => {
                    const card = document.createElement('div');
                    card.className = 'setup-card';
                    card.innerHTML = `
                        <div class="card-header">
                            <div class="card-title">${task.name}</div>
                            <div class="status-badge status-${task.status}">${task.status}</div>
                        </div>
                        <div class="card-description">${task.description}</div>
                        <div class="card-actions">
                            <button class="btn btn-primary" onclick="executeTask('${task.id}')" ${task.status === 'completed' ? 'disabled' : ''}>
                                ${task.status === 'completed' ? 'Completed' : 'Execute'}
                            </button>
                            <button class="btn btn-secondary" onclick="viewTaskDetails('${task.id}')">Details</button>
                        </div>
                    `;
                    grid.appendChild(card);
                });
            }
            
            async function executeTask(taskId) {
                showLoading(true);
                
                try {
                    const response = await fetch('/api/setup-execute', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ task_id: taskId })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        showResult(data.result);
                        await loadSetupStatus();
                        await loadSetupTasks();
                    } else {
                        showResult({ error: data.error });
                    }
                } catch (error) {
                    showResult({ error: error.message });
                } finally {
                    showLoading(false);
                }
            }
            
            async function executeAllTasks() {
                showLoading(true);
                
                for (const task of setupTasks) {
                    if (task.status !== 'completed') {
                        await executeTask(task.id);
                        await new Promise(resolve => setTimeout(resolve, 1000));
                    }
                }
                
                showLoading(false);
            }
            
            async function resetSetup() {
                if (confirm('Are you sure you want to reset all setup tasks?')) {
                    showLoading(true);
                    
                    try {
                        const response = await fetch('/api/setup-reset', {
                            method: 'POST'
                        });
                        
                        const data = await response.json();
                        
                        if (data.success) {
                            await loadSetupStatus();
                            await loadSetupTasks();
                        }
                    } catch (error) {
                        console.error('Failed to reset setup:', error);
                    } finally {
                        showLoading(false);
                    }
                }
            }
            
            async function generateReport() {
                try {
                    const response = await fetch('/api/setup-report');
                    const data = await response.json();
                    
                    if (data.success) {
                        showResult(data.report);
                    }
                } catch (error) {
                    console.error('Failed to generate report:', error);
                }
            }
            
            function viewTaskDetails(taskId) {
                const task = setupTasks.find(t => t.id === taskId);
                if (task) {
                    showResult(task);
                }
            }
            
            function showLoading(show) {
                document.getElementById('loading').style.display = show ? 'block' : 'none';
            }
            
            function showResult(result) {
                const resultSection = document.getElementById('resultSection');
                const resultContent = document.getElementById('resultContent');
                
                resultContent.textContent = JSON.stringify(result, null, 2);
                resultSection.style.display = 'block';
            }
            
            // Load data on page load
            document.addEventListener('DOMContentLoaded', () => {
                loadSetupStatus();
                loadSetupTasks();
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    print("=" * 80)
    print("�� ANDY MAIN CONSOLE")
    print("🏢 CoolBits.ai - Main Console ChatGPT/Grok/Gemini Style")
    print("=" * 80)
    print("👤 CEO: Andrei")
    print("🤖 AI Assistant: Andy - Personal 1:1 Agent")
    print("📅 Contract Date: 2025-09-06")
    print("=" * 80)
    print("🌐 Starting Andy Main Console on port 8102")
    print("=" * 80)
    print("🔗 Main Console URL: http://localhost:8102")
    print("🔗 Landing Page URL: http://localhost:8101")
    print("📋 API Status: http://localhost:8102/api/status")
    print("☁️ Google Cloud: http://localhost:8102/api/gcloud")
    print("🤖 Gemini CLI: http://localhost:8102/api/gemini")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8102)
