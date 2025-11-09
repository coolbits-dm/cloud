#!/usr/bin/env python3
"""
CoolBits.ai Unified Dashboard Server
Serves the main dashboard with hierarchical panel system
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="CoolBits.ai Unified Dashboard",
    description="Unified dashboard system with hierarchical panels",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main unified dashboard"""
    try:
        with open("coolbits_unified_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found</h1>", status_code=404)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "CoolBits.ai Unified Dashboard",
        "version": "1.0.0",
        "panels": ["User", "Business", "Agency", "Development"],
    }


@app.get("/api/panels")
async def get_panels():
    """Get available panels structure"""
    return {
        "panels": {
            "user": {
                "name": "User Panel",
                "description": "Personal user experience and interface management",
                "subpanels": {
                    "personal-ai": {
                        "name": "Personal AI",
                        "description": "Personal AI assistants and tools",
                        "items": [
                            "ChatGPT Personal RAG",
                            "Grok Personal RAG",
                            "Claude Personal RAG",
                            "Gemini Personal RAG",
                        ],
                    },
                    "social": {
                        "name": "Social Tools",
                        "description": "Social media platforms and content",
                        "items": [
                            "Facebook RAG",
                            "TikTok RAG",
                            "X RAG",
                            "LinkedIn RAG",
                            "YouTube RAG",
                        ],
                    },
                    "email": {
                        "name": "Emails",
                        "description": "Email services and communication",
                        "items": [
                            "Gmail RAG",
                            "Outlook RAG",
                            "Personal Email RAG",
                            "Business Email RAG",
                        ],
                    },
                    "productivity": {
                        "name": "Productivity Tools",
                        "description": "Productivity and organization tools",
                        "items": [
                            "Notion RAG",
                            "Obsidian RAG",
                            "Todoist RAG",
                            "Calendar RAG",
                        ],
                    },
                },
            },
            "business": {
                "name": "Business Panel",
                "description": "Business strategy and operations management",
                "subpanels": {
                    "channels": {
                        "name": "Marketing Channels",
                        "description": "Advertising and marketing channels",
                        "items": [
                            "Google Ads RAG",
                            "Meta Ads RAG",
                            "TikTok Ads RAG",
                            "LinkedIn Ads RAG",
                            "X Ads RAG",
                        ],
                    },
                    "tools": {
                        "name": "Business Tools",
                        "description": "Business intelligence and tools",
                        "items": [
                            "GA4 RAG",
                            "Google Analytics RAG",
                            "Google Search Console RAG",
                            "Google My Business RAG",
                        ],
                    },
                    "seo": {
                        "name": "SEO Tools",
                        "description": "Search engine optimization tools",
                        "items": [
                            "SEMrush RAG",
                            "Ahrefs RAG",
                            "Moz RAG",
                            "Screaming Frog RAG",
                        ],
                    },
                    "analytics": {
                        "name": "Analytics",
                        "description": "Business analytics and reporting",
                        "items": [
                            "Google Analytics RAG",
                            "Google Data Studio RAG",
                            "Tableau RAG",
                            "Power BI RAG",
                        ],
                    },
                },
            },
            "agency": {
                "name": "Agency Panel",
                "description": "Agency operations and client management",
                "subpanels": {
                    "clients": {
                        "name": "Client Management",
                        "description": "Client relationship and project management",
                        "items": [
                            "Client Database RAG",
                            "CRM RAG",
                            "Project Tracking RAG",
                            "Communication RAG",
                        ],
                    },
                    "projects": {
                        "name": "Project Management",
                        "description": "Project planning and execution",
                        "items": [
                            "Project Planning RAG",
                            "Task Management RAG",
                            "Timeline RAG",
                            "Resource Management RAG",
                        ],
                    },
                    "creative": {
                        "name": "Creative Tools",
                        "description": "Creative design and content tools",
                        "items": [
                            "Design Tools RAG",
                            "Content Creation RAG",
                            "Brand Management RAG",
                            "Asset Library RAG",
                        ],
                    },
                    "operations": {
                        "name": "Operations",
                        "description": "Agency operations and processes",
                        "items": [
                            "Workflow RAG",
                            "Quality Control RAG",
                            "Team Management RAG",
                            "Performance RAG",
                        ],
                    },
                },
            },
            "development": {
                "name": "Development Panel",
                "description": "Technical development and code management",
                "subpanels": {
                    "frontend": {
                        "name": "Frontend Development",
                        "description": "Frontend technologies and frameworks",
                        "items": [
                            "React RAG",
                            "Vue RAG",
                            "Angular RAG",
                            "HTML/CSS RAG",
                            "JavaScript RAG",
                        ],
                    },
                    "backend": {
                        "name": "Backend Development",
                        "description": "Backend technologies and APIs",
                        "items": [
                            "Node.js RAG",
                            "Python RAG",
                            "FastAPI RAG",
                            "Django RAG",
                            "Express RAG",
                        ],
                    },
                    "devops": {
                        "name": "DevOps",
                        "description": "Development operations and deployment",
                        "items": [
                            "Docker RAG",
                            "Kubernetes RAG",
                            "CI/CD RAG",
                            "AWS RAG",
                            "Google Cloud RAG",
                        ],
                    },
                    "testing": {
                        "name": "Testing",
                        "description": "Testing frameworks and methodologies",
                        "items": [
                            "Unit Testing RAG",
                            "Integration Testing RAG",
                            "E2E Testing RAG",
                            "Performance Testing RAG",
                        ],
                    },
                },
            },
        }
    }


if __name__ == "__main__":
    print("🚀 Starting CoolBits.ai Unified Dashboard Server...")
    print("📊 Dashboard: http://localhost:8080")
    print("🔍 Health Check: http://localhost:8080/health")
    print("📋 API: http://localhost:8080/api/panels")

    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")
