#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy.coolbits.ai Endpoint
SC COOL BITS SRL - Custom domain endpoint with Google Cloud integration
"""

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from typing import Dict, List

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

app = FastAPI(title="Andy.coolbits.ai", version="1.0.0")

# CORS middleware for custom domain
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
async def get_andy_domain_interface(request: Request):
    """Andy.coolbits.ai - Custom Domain Interface"""
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Andy - Personal 1:1 Agent | CoolBits.ai</title>
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
            
            .domain-badge {
                display: inline-block;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
                    <div class="sidebar-subtitle">Personal 1:1 Agent</div>
                    <div class="domain-badge">andy.coolbits.ai</div>
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
                        <div class="welcome-title">Welcome to Andy</div>
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


if __name__ == "__main__":
    print("=" * 80)
    print("🌐 ANDY.COOLBITS.AI ENDPOINT")
    print("🏢 SC COOL BITS SRL - Custom Domain Interface")
    print("=" * 80)
    print("👤 CEO: Andrei")
    print("🤖 AI Assistant: Andy - Personal 1:1 Agent")
    print("📅 Contract Date: 2025-09-06")
    print("=" * 80)
    print("🌐 Starting Andy.coolbits.ai on port 8101")
    print("=" * 80)
    print("🔗 Domain URL: http://andy.coolbits.ai")
    print("🔗 Local URL: http://localhost:8101")
    print("📋 API Status: http://localhost:8101/api/status")
    print("☁️ Google Cloud: http://localhost:8101/api/gcloud")
    print("🤖 Gemini CLI: http://localhost:8101/api/gemini")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8101)
