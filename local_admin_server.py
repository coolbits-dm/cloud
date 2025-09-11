#!/usr/bin/env python3
"""
CoolBits.ai Local Admin Panel Server
Service Management and Control System
"""

import yaml
import json
import subprocess
import psutil
import time
import os
import signal
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="CoolBits.ai Local Admin Panel", version="1.0.0")


# Load services configuration
def load_services_config():
    """Load services configuration from YAML file"""
    try:
        with open("services_config.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return {"services": {}, "categories": {}, "system": {}}


config = load_services_config()
services = config.get("services", {})
categories = config.get("categories", {})
system_config = config.get("system", {})


# Service management
class ServiceManager:
    def __init__(self):
        self.running_services = {}
        self.service_processes = {}

    def get_service_status(self, service_id: str) -> Dict:
        """Get status of a service"""
        service = services.get(service_id)
        if not service:
            return {"status": "not_found", "error": "Service not found"}

        # Check if process is running
        is_running = self.is_service_running(service_id)

        # Check if port is in use
        port_in_use = self.is_port_in_use(service.get("port", 0))

        return {
            "service_id": service_id,
            "name": service.get("name", "Unknown"),
            "status": "running" if is_running else "stopped",
            "port": service.get("port", 0),
            "port_in_use": port_in_use,
            "pid": self.service_processes.get(service_id),
            "uptime": self.get_uptime(service_id),
            "last_started": self.running_services.get(service_id, {}).get("started_at"),
            "category": service.get("category", "unknown"),
            "description": service.get("description", ""),
            "dependencies": service.get("dependencies", []),
        }

    def is_service_running(self, service_id: str) -> bool:
        """Check if service is running"""
        service = services.get(service_id)
        if not service:
            return False

        # Check if port is in use (more reliable than PID tracking)
        return self.is_port_in_use(service.get("port", 0))

    def is_port_in_use(self, port: int) -> bool:
        """Check if port is in use"""
        if port == 0:
            return False

        for conn in psutil.net_connections():
            if conn.laddr.port == port:
                return True
        return False

    def get_uptime(self, service_id: str) -> Optional[str]:
        """Get service uptime"""
        if service_id not in self.running_services:
            return None

        started_at = self.running_services[service_id].get("started_at")
        if not started_at:
            return None

        try:
            start_time = datetime.fromisoformat(started_at)
            uptime = datetime.now() - start_time
            return str(uptime).split(".")[0]  # Remove microseconds
        except:
            return None

    def start_service(self, service_id: str) -> Dict:
        """Start a service"""
        service = services.get(service_id)
        if not service:
            return {"success": False, "error": "Service not found"}

        if self.is_service_running(service_id):
            return {"success": False, "error": "Service already running"}

        # Check dependencies
        dependencies = service.get("dependencies", [])
        for dep in dependencies:
            if not self.is_service_running(dep):
                return {"success": False, "error": f"Dependency {dep} is not running"}

        try:
            # Start the service
            python_path = system_config.get("python_path", "python")
            file_path = service.get("file")

            if not os.path.exists(file_path):
                return {
                    "success": False,
                    "error": f"Service file {file_path} not found",
                }

            # Start process
            process = subprocess.Popen(
                [python_path, file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
                ),
            )

            # Store process info
            self.service_processes[service_id] = process.pid
            self.running_services[service_id] = {
                "started_at": datetime.now().isoformat(),
                "pid": process.pid,
                "port": service.get("port", 0),
            }

            # Wait a bit to check if service started successfully
            time.sleep(3)

            # Check if port is now in use (more reliable than process.poll())
            if self.is_port_in_use(service.get("port", 0)):
                return {
                    "success": True,
                    "message": f"Service {service_id} started successfully",
                    "pid": process.pid,
                }
            else:
                # Clean up if service failed to start
                if service_id in self.service_processes:
                    del self.service_processes[service_id]
                if service_id in self.running_services:
                    del self.running_services[service_id]
                return {
                    "success": False,
                    "error": "Service failed to start - port not listening",
                }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def stop_service(self, service_id: str) -> Dict:
        """Stop a service"""
        if not self.is_service_running(service_id):
            return {"success": False, "error": "Service is not running"}

        service = services.get(service_id)
        if not service:
            return {"success": False, "error": "Service not found"}

        port = service.get("port", 0)

        try:
            # Find process by port (more reliable)
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == "LISTENING":
                    try:
                        process = psutil.Process(conn.pid)
                        process.terminate()

                        # Wait for graceful shutdown
                        try:
                            process.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            # Force kill if graceful shutdown fails
                            process.kill()

                        # Clean up
                        if service_id in self.service_processes:
                            del self.service_processes[service_id]
                        if service_id in self.running_services:
                            del self.running_services[service_id]

                        return {
                            "success": True,
                            "message": f"Service {service_id} stopped successfully",
                        }
                    except psutil.NoSuchProcess:
                        # Process already dead
                        return {
                            "success": True,
                            "message": f"Service {service_id} was already stopped",
                        }
                    except Exception as e:
                        return {
                            "success": False,
                            "error": f"Error stopping process: {str(e)}",
                        }

            return {"success": False, "error": "No process found listening on port"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def restart_service(self, service_id: str) -> Dict:
        """Restart a service"""
        # Stop first
        stop_result = self.stop_service(service_id)
        if not stop_result["success"] and "not running" not in stop_result["error"]:
            return stop_result

        # Wait a bit
        time.sleep(2)

        # Start again
        return self.start_service(service_id)

    def get_all_services_status(self) -> Dict:
        """Get status of all services"""
        result = {}
        for service_id in services.keys():
            result[service_id] = self.get_service_status(service_id)
        return result


# Initialize service manager
service_manager = ServiceManager()


# API Models
class ServiceAction(BaseModel):
    action: str  # start, stop, restart
    service_id: str


# API Endpoints
@app.get("/", response_class=HTMLResponse)
async def admin_panel():
    """Serve the admin panel HTML"""
    try:
        with open("local_admin_panel.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Admin Panel not found</h1>", status_code=404)


@app.get("/api/services")
async def get_all_services():
    """Get all services with their status"""
    return {
        "services": service_manager.get_all_services_status(),
        "categories": categories,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/services/{service_id}")
async def get_service_status(service_id: str):
    """Get status of a specific service"""
    status = service_manager.get_service_status(service_id)
    if status["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Service not found")
    return status


@app.post("/api/services/{service_id}/action")
async def service_action(service_id: str, action: ServiceAction):
    """Perform action on a service"""
    if action.action == "start":
        result = service_manager.start_service(service_id)
    elif action.action == "stop":
        result = service_manager.stop_service(service_id)
    elif action.action == "restart":
        result = service_manager.restart_service(service_id)
    else:
        raise HTTPException(status_code=400, detail="Invalid action")

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@app.get("/api/system/health")
async def system_health():
    """Get system health information"""
    return {
        "timestamp": datetime.now().isoformat(),
        "running_services": len(
            [
                s
                for s in service_manager.get_all_services_status().values()
                if s["status"] == "running"
            ]
        ),
        "total_services": len(services),
        "system_info": {
            "python_path": system_config.get("python_path", "python"),
            "log_level": system_config.get("log_level", "info"),
        },
    }


@app.post("/api/system/start-all")
async def start_all_services():
    """Start all auto-start services"""
    results = {}
    for service_id, service in services.items():
        if service.get("auto_start", False):
            result = service_manager.start_service(service_id)
            results[service_id] = result
    return results


@app.post("/api/system/stop-all")
async def stop_all_services():
    """Stop all running services"""
    results = {}
    for service_id in services.keys():
        if service_manager.is_service_running(service_id):
            result = service_manager.stop_service(service_id)
            results[service_id] = result
    return results


if __name__ == "__main__":
    print("🚀 Starting CoolBits.ai Local Admin Panel...")
    print("🌐 Access: http://localhost:8100")
    print("📊 Service Management Active!")

    uvicorn.run(app, host="0.0.0.0", port=8100, log_level="info")
