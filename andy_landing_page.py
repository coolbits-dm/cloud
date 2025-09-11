#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Andy Landing Page
CoolBits.ai - Landing page with Google authentication
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

app = FastAPI(title="Andy Landing Page", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def get_andy_landing_page(request: Request):
    """Andy Landing Page with Google Authentication"""
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
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
            }
            
            .landing-container {
                max-width: 1200px;
                width: 90%;
                text-align: center;
                padding: 40px 20px;
            }
            
            .logo-section {
                margin-bottom: 60px;
            }
            
            .logo {
                font-size: 72px;
                font-weight: 700;
                margin-bottom: 20px;
                text-shadow: 0 4px 8px rgba(0,0,0,0.3);
            }
            
            .tagline {
                font-size: 24px;
                font-weight: 300;
                opacity: 0.9;
                margin-bottom: 10px;
            }
            
            .subtitle {
                font-size: 18px;
                opacity: 0.8;
                margin-bottom: 40px;
            }
            
            .domain-badge {
                display: inline-block;
                background: rgba(255,255,255,0.2);
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 600;
                margin-bottom: 40px;
                backdrop-filter: blur(10px);
            }
            
            .main-actions {
                display: flex;
                gap: 30px;
                justify-content: center;
                margin-bottom: 60px;
                flex-wrap: wrap;
            }
            
            .action-button {
                padding: 20px 40px;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
                min-width: 200px;
            }
            
            .primary-button {
                background: linear-gradient(135deg, #10a37f 0%, #1a7f64 100%);
                color: white;
                box-shadow: 0 8px 20px rgba(16, 163, 127, 0.3);
            }
            
            .primary-button:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 25px rgba(16, 163, 127, 0.4);
            }
            
            .secondary-button {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 2px solid rgba(255,255,255,0.3);
                backdrop-filter: blur(10px);
            }
            
            .secondary-button:hover {
                background: rgba(255,255,255,0.3);
                transform: translateY(-3px);
            }
            
            .features-section {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 30px;
                margin-bottom: 60px;
            }
            
            .feature-card {
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 16px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                transition: transform 0.3s ease;
            }
            
            .feature-card:hover {
                transform: translateY(-5px);
            }
            
            .feature-icon {
                font-size: 48px;
                margin-bottom: 20px;
            }
            
            .feature-title {
                font-size: 20px;
                font-weight: 600;
                margin-bottom: 15px;
            }
            
            .feature-description {
                font-size: 16px;
                opacity: 0.9;
                line-height: 1.6;
            }
            
            .video-section {
                margin-bottom: 60px;
            }
            
            .video-container {
                position: relative;
                width: 100%;
                max-width: 800px;
                margin: 0 auto;
                border-radius: 16px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0,0,0,0.3);
            }
            
            .video-placeholder {
                width: 100%;
                height: 450px;
                background: rgba(0,0,0,0.3);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                font-weight: 600;
                backdrop-filter: blur(10px);
            }
            
            .play-button {
                width: 80px;
                height: 80px;
                background: rgba(255,255,255,0.9);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 32px;
                color: #333;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .play-button:hover {
                transform: scale(1.1);
                background: white;
            }
            
            .auth-section {
                background: rgba(255,255,255,0.1);
                padding: 40px;
                border-radius: 16px;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255,255,255,0.2);
                max-width: 500px;
                margin: 0 auto;
            }
            
            .auth-title {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 20px;
            }
            
            .auth-description {
                font-size: 16px;
                opacity: 0.9;
                margin-bottom: 30px;
                line-height: 1.6;
            }
            
            .google-auth-button {
                width: 100%;
                padding: 16px 24px;
                background: white;
                color: #333;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 12px;
            }
            
            .google-auth-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }
            
            .google-icon {
                width: 20px;
                height: 20px;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%234285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="%2334A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="%23FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="%23EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>') no-repeat center;
                background-size: contain;
            }
            
            .footer {
                margin-top: 60px;
                padding-top: 40px;
                border-top: 1px solid rgba(255,255,255,0.2);
                opacity: 0.8;
            }
            
            .footer-text {
                font-size: 14px;
                margin-bottom: 10px;
            }
            
            .footer-links {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
            }
            
            .footer-link {
                color: white;
                text-decoration: none;
                opacity: 0.8;
                transition: opacity 0.3s ease;
            }
            
            .footer-link:hover {
                opacity: 1;
            }
            
            @media (max-width: 768px) {
                .logo {
                    font-size: 48px;
                }
                
                .tagline {
                    font-size: 20px;
                }
                
                .subtitle {
                    font-size: 16px;
                }
                
                .main-actions {
                    flex-direction: column;
                    align-items: center;
                }
                
                .action-button {
                    width: 100%;
                    max-width: 300px;
                }
                
                .features-section {
                    grid-template-columns: 1fr;
                }
                
                .video-container {
                    max-width: 100%;
                }
                
                .video-placeholder {
                    height: 250px;
                }
            }
        </style>
    </head>
    <body>
        <div class="landing-container">
            <!-- Logo Section -->
            <div class="logo-section">
                <div class="logo">🤖 Andy</div>
                <div class="tagline">Personal 1:1 Agent</div>
                <div class="subtitle">Your AI assistant across all platforms</div>
                <div class="domain-badge">andy.coolbits.ai</div>
            </div>
            
            <!-- Main Actions -->
            <div class="main-actions">
                <button class="action-button primary-button" onclick="talkToAndy()">
                    💬 Talk to Andy
                </button>
                <button class="action-button secondary-button" onclick="viewMore()">
                    📺 View More
                </button>
            </div>
            
            <!-- Features Section -->
            <div class="features-section">
                <div class="feature-card">
                    <div class="feature-icon">🏠</div>
                    <div class="feature-title">Localhost:8101</div>
                    <div class="feature-description">Main Andy pillar - oPython agent execution and root collaboration</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">☁️</div>
                    <div class="feature-title">Google Cloud</div>
                    <div class="feature-description">Gemini motor integration with full Google Cloud CLI access</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🤖</div>
                    <div class="feature-title">OpenAI Integration</div>
                    <div class="feature-description">Andy's OpenAI key for ChatGPT tab and API access</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🚀</div>
                    <div class="feature-title">xAI Integration</div>
                    <div class="feature-description">Andy's xAI key for Grok tab and API access</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">📱</div>
                    <div class="feature-title">Social Media</div>
                    <div class="feature-description">Facebook, Instagram, TikTok integration and management</div>
                </div>
                
                <div class="feature-card">
                    <div class="feature-icon">🛠️</div>
                    <div class="feature-title">Marketing Tools</div>
                    <div class="feature-description">All possible marketing, development, and business tools</div>
                </div>
            </div>
            
            <!-- Video Section -->
            <div class="video-section">
                <div class="video-container">
                    <div class="video-placeholder" id="videoPlaceholder">
                        <div class="play-button" onclick="playVideo()">▶</div>
                    </div>
                </div>
            </div>
            
            <!-- Authentication Section -->
            <div class="auth-section">
                <div class="auth-title">🔐 Secure Access</div>
                <div class="auth-description">
                    To access Andy's main console, please authenticate with your Google account. 
                    This ensures secure access to all Andy's capabilities across platforms.
                </div>
                <button class="google-auth-button" onclick="authenticateWithGoogle()">
                    <div class="google-icon"></div>
                    Continue with Google
                </button>
            </div>
            
            <!-- Footer -->
            <div class="footer">
                <div class="footer-text">© 2025 CoolBits.ai</div>
                <div class="footer-links">
                    <a href="#" class="footer-link">Privacy Policy</a>
                    <a href="#" class="footer-link">Terms of Service</a>
                    <a href="#" class="footer-link">Contact</a>
                    <a href="#" class="footer-link">Support</a>
                </div>
            </div>
        </div>

        <script>
            // Talk to Andy function
            function talkToAndy() {
                // Redirect to main console (port 8102)
                window.location.href = 'http://localhost:8102';
            }
            
            // View More function
            function viewMore() {
                // Show video or expand content
                const videoPlaceholder = document.getElementById('videoPlaceholder');
                videoPlaceholder.innerHTML = `
                    <iframe 
                        width="100%" 
                        height="100%" 
                        src="https://www.youtube.com/embed/dQw4w9WgXcQ" 
                        title="Andy Demo Video" 
                        frameborder="0" 
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                        allowfullscreen>
                    </iframe>
                `;
            }
            
            // Play video function
            function playVideo() {
                viewMore();
            }
            
            // Google authentication function
            function authenticateWithGoogle() {
                // Simulate Google authentication
                const button = document.querySelector('.google-auth-button');
                button.innerHTML = '<div class="google-icon"></div> Authenticating...';
                button.disabled = true;
                
                // Simulate authentication process
                setTimeout(() => {
                    button.innerHTML = '<div class="google-icon"></div> ✅ Authenticated';
                    
                    // Redirect to main console after authentication
                    setTimeout(() => {
                        window.location.href = 'http://localhost:8102';
                    }, 1000);
                }, 2000);
            }
            
            // Add some interactive effects
            document.addEventListener('DOMContentLoaded', function() {
                // Add hover effects to feature cards
                const featureCards = document.querySelectorAll('.feature-card');
                featureCards.forEach(card => {
                    card.addEventListener('mouseenter', function() {
                        this.style.transform = 'translateY(-5px) scale(1.02)';
                    });
                    
                    card.addEventListener('mouseleave', function() {
                        this.style.transform = 'translateY(0) scale(1)';
                    });
                });
                
                // Add click effects to buttons
                const buttons = document.querySelectorAll('.action-button');
                buttons.forEach(button => {
                    button.addEventListener('click', function() {
                        this.style.transform = 'translateY(-3px) scale(0.98)';
                        setTimeout(() => {
                            this.style.transform = 'translateY(-3px) scale(1)';
                        }, 150);
                    });
                });
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/api/status")
async def get_status():
    """Get landing page status"""
    return {
        "page": "Andy Landing Page",
        "port": 8101,
        "status": "active",
        "features": [
            "Google Authentication",
            "Talk to Andy Button",
            "View More Video",
            "Feature Cards",
            "Responsive Design",
        ],
        "redirects": {
            "main_console": "http://localhost:8102",
            "google_auth": "Simulated authentication",
        },
        "timestamp": datetime.now().isoformat(),
    }


if __name__ == "__main__":
    print("=" * 80)
    print("�� ANDY LANDING PAGE")
    print("🏢 CoolBits.ai - Landing Page with Google Auth")
    print("=" * 80)
    print("👤 CEO: Andrei")
    print("🤖 AI Assistant: Andy - Personal 1:1 Agent")
    print("📅 Contract Date: 2025-09-06")
    print("=" * 80)
    print("🌐 Starting Andy Landing Page on port 8101")
    print("=" * 80)
    print("🔗 Landing Page URL: http://localhost:8101")
    print("🔗 Main Console URL: http://localhost:8102")
    print("📋 API Status: http://localhost:8101/api/status")
    print("=" * 80)

    uvicorn.run(app, host="0.0.0.0", port=8101)
