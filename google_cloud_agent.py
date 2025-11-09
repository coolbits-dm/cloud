# cbLM Logo Integration
# Favicon: favicon.ico, cb-16x16.png, cb-32x32.png
# Profile Pictures: profile-*.png
# Company: COOL BITS SRL 🏢 🏢
# CEO: Andrei
# AI Assistant: oCursor

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Cloud CLI Agent
SC COOL BITS SRL 🏢 🏢 - Local Google Cloud Integration Agent
"""

import os
import json
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, Any
from pathlib import Path
from fastapi import FastAPI, HTTPException
import uvicorn


class GoogleCloudAgent:
    """Agent for Google Cloud CLI integration and local cloud management"""

    def __init__(self):
        self.company = "SC COOL BITS SRL 🏢 🏢"
        self.ceo = "Andrei"
        self.ai_assistant = "Cursor AI Assistant"
        self.contract_date = "2025-09-06"
        self.base_path = Path(r"C:\Users\andre\Desktop\coolbits")
        self.port = 8091

        # Hardware specifications
        self.hardware_specs = {
            "cpu": "Windows 11 CPU - Available for processing",
            "gpu": "Windows 11 GPU - Available for AI/ML processing",
            "storage": "Windows 11 Storage - Available for data storage",
            "memory": "Windows 11 RAM - Available for processing",
            "network": "Windows 11 Network - Available for cloud connectivity",
        }

        # Google Cloud configuration
        self.gcloud_config = {
            "project_id": "coolbits-ai",
            "region": "us-central1",
            "zone": "us-central1-a",
            "service_account": "coolbits-service-account",
            "bucket_name": "coolbits-storage-bucket",
        }

        # Initialize FastAPI app
        self.app = FastAPI(
            title="Google Cloud CLI Agent",
            description="Local Google Cloud integration and management",
            version="1.0.0",
        )

        self._setup_routes()

        # Check Google Cloud CLI availability
        self.gcloud_available = self._check_gcloud_cli()

    def _check_gcloud_cli(self) -> bool:
        """Check if Google Cloud CLI is installed and configured"""
        try:
            result = subprocess.run(
                ["gcloud", "--version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                print("✅ Google Cloud CLI is available")
                return True
            else:
                print("❌ Google Cloud CLI not found")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("❌ Google Cloud CLI not installed")
            return False

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.get("/")
        async def root():
            return {
                "agent": "Google Cloud CLI Agent",
                "company": self.company,
                "ceo": self.ceo,
                "ai_assistant": self.ai_assistant,
                "port": self.port,
                "gcloud_available": self.gcloud_available,
                "hardware_specs": self.hardware_specs,
                "status": "active",
            }

        @self.app.get("/api/status")
        async def get_status():
            return {
                "agent": "Google Cloud CLI Agent",
                "company": self.company,
                "ceo": self.ceo,
                "ai_assistant": self.ai_assistant,
                "contract_date": self.contract_date,
                "port": self.port,
                "gcloud_available": self.gcloud_available,
                "hardware_specs": self.hardware_specs,
                "gcloud_config": self.gcloud_config,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.get("/api/hardware")
        async def get_hardware_status():
            """Get current hardware utilization"""
            try:
                # Get CPU usage
                cpu_result = subprocess.run(
                    ["wmic", "cpu", "get", "loadpercentage", "/value"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                # Get memory usage
                memory_result = subprocess.run(
                    [
                        "wmic",
                        "OS",
                        "get",
                        "TotalVisibleMemorySize,FreePhysicalMemory",
                        "/value",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                # Get disk usage
                disk_result = subprocess.run(
                    ["wmic", "logicaldisk", "get", "size,freespace,caption", "/value"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                return {
                    "cpu_info": (
                        cpu_result.stdout if cpu_result.returncode == 0 else "N/A"
                    ),
                    "memory_info": (
                        memory_result.stdout if memory_result.returncode == 0 else "N/A"
                    ),
                    "disk_info": (
                        disk_result.stdout if disk_result.returncode == 0 else "N/A"
                    ),
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                return {"error": str(e), "timestamp": datetime.now().isoformat()}

        @self.app.post("/api/gcloud/command")
        async def execute_gcloud_command(request: Dict[str, Any]):
            """Execute Google Cloud CLI command"""
            try:
                if not self.gcloud_available:
                    raise HTTPException(
                        status_code=400, detail="Google Cloud CLI not available"
                    )

                command = request.get("command", "")
                if not command:
                    raise HTTPException(status_code=400, detail="No command provided")

                # Execute gcloud command
                result = subprocess.run(
                    ["gcloud"] + command.split(),
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(self.base_path),
                )

                return {
                    "command": f"gcloud {command}",
                    "returncode": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "timestamp": datetime.now().isoformat(),
                }

            except subprocess.TimeoutExpired:
                raise HTTPException(status_code=408, detail="Command timeout")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/gcloud/projects")
        async def list_gcloud_projects():
            """List Google Cloud projects"""
            try:
                if not self.gcloud_available:
                    raise HTTPException(
                        status_code=400, detail="Google Cloud CLI not available"
                    )

                result = subprocess.run(
                    ["gcloud", "projects", "list", "--format=json"],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                if result.returncode == 0:
                    projects = json.loads(result.stdout) if result.stdout else []
                    return {
                        "projects": projects,
                        "count": len(projects),
                        "timestamp": datetime.now().isoformat(),
                    }
                else:
                    return {
                        "error": result.stderr,
                        "timestamp": datetime.now().isoformat(),
                    }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/gcloud/auth")
        async def authenticate_gcloud(request: Dict[str, Any]):
            """Authenticate with Google Cloud"""
            try:
                if not self.gcloud_available:
                    raise HTTPException(
                        status_code=400, detail="Google Cloud CLI not available"
                    )

                auth_type = request.get("auth_type", "login")

                if auth_type == "login":
                    # Open browser for authentication
                    webbrowser.open("https://accounts.google.com/signin")
                    return {
                        "message": "Please complete authentication in browser",
                        "auth_url": "https://accounts.google.com/signin",
                        "timestamp": datetime.now().isoformat(),
                    }
                elif auth_type == "service_account":
                    key_file = request.get("key_file")
                    if not key_file:
                        raise HTTPException(
                            status_code=400, detail="Service account key file required"
                        )

                    result = subprocess.run(
                        [
                            "gcloud",
                            "auth",
                            "activate-service-account",
                            "--key-file",
                            key_file,
                        ],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )

                    return {
                        "command": f"gcloud auth activate-service-account --key-file {key_file}",
                        "returncode": result.returncode,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "timestamp": datetime.now().isoformat(),
                    }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/favicon.ico")
        async def favicon():
            """Serve favicon.ico"""
            try:
                favicon_path = os.path.join(str(self.base_path), "favicon.ico")
                if os.path.exists(favicon_path):
                    from fastapi.responses import FileResponse

                    return FileResponse(favicon_path, media_type="image/x-icon")
                else:
                    raise HTTPException(status_code=404, detail="Favicon not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/logo/{size}")
        async def get_logo(size: str):
            """Get logo in specified size"""
            try:
                logo_path = os.path.join(str(self.base_path), f"cb-{size}x{size}.png")
                if os.path.exists(logo_path):
                    from fastapi.responses import FileResponse

                    return FileResponse(logo_path, media_type="image/png")
                else:
                    raise HTTPException(
                        status_code=404, detail=f"Logo size {size}x{size} not found"
                    )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/profile/{entity}")
        async def get_profile_picture(entity: str):
            """Get profile picture for entity"""
            try:
                profile_path = os.path.join(
                    str(self.base_path), f"profile-{entity}.png"
                )
                if os.path.exists(profile_path):
                    from fastapi.responses import FileResponse

                    return FileResponse(profile_path, media_type="image/png")
                else:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Profile picture for {entity} not found",
                    )
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/gcloud/setup")
        async def setup_gcloud_project(request: Dict[str, Any]):
            """Setup Google Cloud project for CoolBits.ai"""
            try:
                if not self.gcloud_available:
                    raise HTTPException(
                        status_code=400, detail="Google Cloud CLI not available"
                    )

                project_id = request.get("project_id", self.gcloud_config["project_id"])

                # Set project
                result1 = subprocess.run(
                    ["gcloud", "config", "set", "project", project_id],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                # Enable required APIs
                apis = [
                    "compute.googleapis.com",
                    "storage.googleapis.com",
                    "aiplatform.googleapis.com",
                    "bigquery.googleapis.com",
                ]

                results = []
                for api in apis:
                    result = subprocess.run(
                        ["gcloud", "services", "enable", api],
                        capture_output=True,
                        text=True,
                        timeout=15,
                    )
                    results.append(
                        {
                            "api": api,
                            "returncode": result.returncode,
                            "stdout": result.stdout,
                            "stderr": result.stderr,
                        }
                    )

                return {
                    "project_id": project_id,
                    "project_set": {
                        "returncode": result1.returncode,
                        "stdout": result1.stdout,
                        "stderr": result1.stderr,
                    },
                    "apis_enabled": results,
                    "timestamp": datetime.now().isoformat(),
                }

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def initialize_agent(self):
        """Initialize the Google Cloud CLI agent"""
        print("=" * 70)
        print("☁️ GOOGLE CLOUD CLI AGENT")
        print("🏢 SC COOL BITS SRL 🏢 🏢 - Local Cloud Integration")
        print("=" * 70)
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print(f"📅 Contract Date: {self.contract_date}")
        print(f"🌐 Port: {self.port}")
        print("=" * 70)
        print("🖥️ HARDWARE SPECIFICATIONS:")
        for spec, description in self.hardware_specs.items():
            print(f"  • {spec.upper()}: {description}")
        print("=" * 70)
        print("☁️ GOOGLE CLOUD CONFIGURATION:")
        for key, value in self.gcloud_config.items():
            print(f"  • {key}: {value}")
        print("=" * 70)
        print(
            f"🔧 Google Cloud CLI: {'✅ Available' if self.gcloud_available else '❌ Not Available'}"
        )
        print("=" * 70)
        print("🚀 AVAILABLE COMMANDS:")
        print("  • Hardware monitoring and utilization")
        print("  • Google Cloud project management")
        print("  • Cloud resource provisioning")
        print("  • AI/ML service integration")
        print("  • Storage and compute management")
        print("=" * 70)
        print(f"🔗 Agent URL: http://localhost:{self.port}")
        print(f"📋 API Status: http://localhost:{self.port}/api/status")
        print(f"🖥️ Hardware: http://localhost:{self.port}/api/hardware")
        print("=" * 70)

    def get_hardware_utilization(self) -> Dict[str, Any]:
        """Get current hardware utilization"""
        try:
            # CPU usage
            cpu_result = subprocess.run(
                ["wmic", "cpu", "get", "loadpercentage", "/value"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Memory usage
            memory_result = subprocess.run(
                [
                    "wmic",
                    "OS",
                    "get",
                    "TotalVisibleMemorySize,FreePhysicalMemory",
                    "/value",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            # Disk usage
            disk_result = subprocess.run(
                ["wmic", "logicaldisk", "get", "size,freespace,caption", "/value"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            return {
                "cpu": cpu_result.stdout if cpu_result.returncode == 0 else "N/A",
                "memory": (
                    memory_result.stdout if memory_result.returncode == 0 else "N/A"
                ),
                "disk": disk_result.stdout if disk_result.returncode == 0 else "N/A",
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def execute_gcloud_command(self, command: str) -> Dict[str, Any]:
        """Execute Google Cloud CLI command"""
        try:
            if not self.gcloud_available:
                return {"error": "Google Cloud CLI not available"}

            result = subprocess.run(
                ["gcloud"] + command.split(),
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.base_path),
            )

            return {
                "command": f"gcloud {command}",
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat(),
            }

        except subprocess.TimeoutExpired:
            return {"error": "Command timeout", "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    agent = GoogleCloudAgent()
    agent.initialize_agent()

    print(f"🌐 Starting Google Cloud CLI Agent on port {agent.port}")
    print("=" * 70)

    uvicorn.run(agent.app, host="0.0.0.0", port=agent.port, log_level="info")
