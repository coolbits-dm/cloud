#!/usr/bin/env python3
"""
CoolBits.ai 🏢 - Main Dashboard Server
Central dashboard for all CoolBits services and processes
"""

import json
import time
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
import psutil
import requests
from feature_flags import feature_flags

app = Flask(__name__)
CORS(app)


class CoolBitsServiceManager:
    """CoolBits Service Manager"""

    def __init__(self):
        self.company = "COOL BITS SRL 🏢"
        self.ceo = "Andrei"
        self.services = {
            "meta_platform": {
                "name": "Meta Platform",
                "port": 3003,
                "status": "unknown",
                "url": "http://localhost:3003",
                "description": "Meta Platform Integration Panel",
                "app_id": "825511663344104",
                "owner": "Andrei Cip",
            },
            "andy_agent": {
                "name": "Andy Agent",
                "port": 8101,
                "status": "unknown",
                "url": "http://localhost:8101",
                "description": "Personal 1:1 Agent for Andrei",
                "capabilities": ["code_generation", "project_analysis", "rag_system"],
            },
            "kim_agent": {
                "name": "Kim Agent",
                "port": 8102,
                "status": "unknown",
                "url": "http://localhost:8102",
                "description": "Reasoning & Analysis Agent",
                "capabilities": ["reasoning", "analysis", "conversational"],
            },
            "bits_orchestrator": {
                "name": "Bits Orchestrator",
                "port": 3001,
                "status": "unknown",
                "url": "http://localhost:3001",
                "description": "Bits Framework Orchestrator",
                "capabilities": ["multi_agent_routing", "bit_management"],
            },
            "coolbits_dashboard": {
                "name": "CoolBits Dashboard",
                "port": 3000,
                "status": "unknown",
                "url": "http://localhost:3000",
                "description": "Main CoolBits Dashboard",
                "capabilities": ["project_management", "ai_board"],
            },
        }

        # Start service monitoring
        self.monitor_services()

    def check_service_status(self, service_name, port):
        """Check if a service is running on a specific port"""
        try:
            # Check if port is listening
            for conn in psutil.net_connections():
                if conn.laddr.port == port and conn.status == "LISTEN":
                    return "running"
            return "stopped"
        except Exception:
            return "error"

    def monitor_services(self):
        """Monitor all services status"""
        for service_name, service_info in self.services.items():
            status = self.check_service_status(service_name, service_info["port"])
            self.services[service_name]["status"] = status

    def get_service_info(self, service_name):
        """Get detailed service information"""
        if service_name in self.services:
            service = self.services[service_name]
            # Try to get additional info from the service
            try:
                response = requests.get(f"{service['url']}/api/status", timeout=2)
                if response.status_code == 200:
                    service["api_status"] = response.json()
            except:
                service["api_status"] = None
            return service
        return None

    def start_service(self, service_name):
        """Start a service"""
        if service_name in self.services:
            service = self.services[service_name]
            # This would start the actual service
            # For now, just update status
            service["status"] = "starting"
            return {"status": "starting", "message": f"Starting {service['name']}..."}
        return {"status": "error", "message": "Service not found"}

    def stop_service(self, service_name):
        """Stop a service"""
        if service_name in self.services:
            service = self.services[service_name]
            # This would stop the actual service
            # For now, just update status
            service["status"] = "stopping"
            return {"status": "stopping", "message": f"Stopping {service['name']}..."}
        return {"status": "error", "message": "Service not found"}


# Initialize service manager
service_manager = CoolBitsServiceManager()

# HTML Template for the main dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CoolBits.ai 🏢 - Main Dashboard</title>
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

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.3rem;
            opacity: 0.9;
        }

        .company-info {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .company-info h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .info-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .info-card h3 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .service-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }

        .service-card:hover {
            transform: translateY(-5px);
        }

        .service-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .service-name {
            font-size: 1.4rem;
            font-weight: bold;
            color: #333;
        }

        .status-badge {
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: bold;
        }

        .status-running {
            background: #d4edda;
            color: #155724;
        }

        .status-stopped {
            background: #f8d7da;
            color: #721c24;
        }

        .status-starting {
            background: #fff3cd;
            color: #856404;
        }

        .status-stopping {
            background: #d1ecf1;
            color: #0c5460;
        }

        .status-unknown {
            background: #e2e3e5;
            color: #383d41;
        }

        .service-description {
            color: #666;
            margin-bottom: 15px;
        }

        .service-url {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin-bottom: 15px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }

        .service-actions {
            display: flex;
            gap: 10px;
        }

        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: bold;
            transition: background 0.3s;
        }

        .btn-primary {
            background: #667eea;
            color: white;
        }

        .btn-primary:hover {
            background: #5a6fd8;
        }

        .btn-danger {
            background: #dc3545;
            color: white;
        }

        .btn-danger:hover {
            background: #c82333;
        }

        .btn-success {
            background: #28a745;
            color: white;
        }

        .btn-success:hover {
            background: #218838;
        }

        .btn-secondary {
            background: #6c757d;
            color: white;
        }

        .btn-secondary:hover {
            background: #5a6268;
        }

        .logs-area {
            background: #1e1e1e;
            color: #00ff00;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            min-height: 200px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            overflow-y: auto;
            max-height: 300px;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: white;
            opacity: 0.8;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .services-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 CoolBits.ai 🏢</h1>
            <p>Main Dashboard - All Services & Processes</p>
        </div>

        <div class="company-info">
            <h2>🏢 Company Information</h2>
            <div class="info-grid">
                <div class="info-card">
                    <h3>Company</h3>
                    <p>COOL BITS SRL 🏢</p>
                </div>
                <div class="info-card">
                    <h3>CEO</h3>
                    <p>Andrei</p>
                </div>
                <div class="info-card">
                    <h3>Meta Owner</h3>
                    <p>Andrei Cip</p>
                </div>
                <div class="info-card">
                    <h3>Meta App ID</h3>
                    <p>825511663344104</p>
                </div>
            </div>
        </div>

        <div class="services-grid" id="servicesGrid">
            <!-- Services will be loaded here -->
        </div>

        <div class="logs-area" id="logsArea">
            [2025-09-07 06:05:00] CoolBits.ai 🏢 Main Dashboard Started
            [2025-09-07 06:05:00] Company: COOL BITS SRL 🏢
            [2025-09-07 06:05:00] CEO: Andrei
            [2025-09-07 06:05:00] Monitoring all services...
        </div>

        <div class="footer">
            <p>🏢 COOL BITS SRL 🏢 - Main Dashboard</p>
            <p>CEO: Andrei | Meta Owner: Andrei Cip | App ID: 825511663344104</p>
        </div>
    </div>

    <script>
        // Service management JavaScript
        function log(message) {
            const logsArea = document.getElementById('logsArea');
            const timestamp = new Date().toISOString().replace('T', ' ').substring(0, 19);
            logsArea.textContent += `[${timestamp}] ${message}\\n`;
            logsArea.scrollTop = logsArea.scrollHeight;
        }

        function updateServices() {
            fetch('/api/services/status')
                .then(response => response.json())
                .then(data => {
                    const servicesGrid = document.getElementById('servicesGrid');
                    servicesGrid.innerHTML = '';
                    
                    Object.entries(data.services).forEach(([key, service]) => {
                        const serviceCard = createServiceCard(key, service);
                        servicesGrid.appendChild(serviceCard);
                    });
                })
                .catch(error => {
                    log('Error updating services: ' + error.message);
                });
        }

        function createServiceCard(key, service) {
            const card = document.createElement('div');
            card.className = 'service-card';
            
            const statusClass = `status-${service.status}`;
            const statusText = service.status.charAt(0).toUpperCase() + service.status.slice(1);
            
            card.innerHTML = `
                <div class="service-header">
                    <div class="service-name">${service.name}</div>
                    <div class="status-badge ${statusClass}">${statusText}</div>
                </div>
                <div class="service-description">${service.description}</div>
                <div class="service-url">${service.url}</div>
                <div class="service-actions">
                    <button class="btn btn-primary" onclick="openService('${service.url}')">Open</button>
                    <button class="btn btn-success" onclick="startService('${key}')">Start</button>
                    <button class="btn btn-danger" onclick="stopService('${key}')">Stop</button>
                    <button class="btn btn-secondary" onclick="refreshService('${key}')">Refresh</button>
                </div>
            `;
            
            return card;
        }

        function openService(url) {
            window.open(url, '_blank');
            log('Opening service: ' + url);
        }

        function startService(serviceName) {
            fetch(`/api/services/${serviceName}/start`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    log(data.message);
                    updateServices();
                })
                .catch(error => {
                    log('Error starting service: ' + error.message);
                });
        }

        function stopService(serviceName) {
            fetch(`/api/services/${serviceName}/stop`, {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    log(data.message);
                    updateServices();
                })
                .catch(error => {
                    log('Error stopping service: ' + error.message);
                });
        }

        function refreshService(serviceName) {
            fetch(`/api/services/${serviceName}/info`)
                .then(response => response.json())
                .then(data => {
                    log('Refreshed service info: ' + serviceName);
                    updateServices();
                })
                .catch(error => {
                    log('Error refreshing service: ' + error.message);
                });
        }

        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            log('CoolBits.ai 🏢 Main Dashboard Loaded');
            updateServices();
            
            // Update services every 5 seconds
            setInterval(updateServices, 5000);
        });
    </script>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Serve the main dashboard"""
    return render_template_string(DASHBOARD_TEMPLATE)


@app.route("/api/feature-flags")
def get_feature_flags():
    """Get all feature flags"""
    return jsonify(
        {
            "flags": feature_flags.get_all_flags(),
            "enabled": feature_flags.get_enabled_flags(),
            "disabled": feature_flags.get_disabled_flags(),
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/feature-flags/<flag_name>", methods=["POST"])
def toggle_feature_flag(flag_name):
    """Toggle a feature flag"""
    try:
        action = request.json.get("action", "toggle")

        if action == "enable":
            success = feature_flags.enable(flag_name)
        elif action == "disable":
            success = feature_flags.disable(flag_name)
        elif action == "toggle":
            success = feature_flags.toggle(flag_name)
        else:
            return jsonify({"error": "Invalid action"}), 400

        if success:
            return jsonify(
                {
                    "flag": flag_name,
                    "enabled": feature_flags.is_enabled(flag_name),
                    "action": action,
                    "timestamp": datetime.now().isoformat(),
                }
            )
        else:
            return jsonify({"error": "Flag not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/health")
def health_check():
    """Standardized health check endpoint"""
    import platform
    import os

    # Get runtime info
    runtime_info = {}
    if os.path.exists(".runtime.json"):
        try:
            with open(".runtime.json", "r") as f:
                runtime_info = json.load(f)
        except:
            pass

    return jsonify(
        {
            "status": "healthy",
            "service": "CoolBits.ai Main Dashboard",
            "version": "1.0.0",
            "commitSha": "main",  # TODO: Get from git
            "buildTime": runtime_info.get("started_at", datetime.now().isoformat()),
            "node": platform.node(),
            "env": "production" if os.getenv("CI") == "1" else "development",
            "appMode": "web",
            "schemaVersion": "1.0",
            "uptimeSec": int(time.time() - os.path.getctime(".runtime.json"))
            if os.path.exists(".runtime.json")
            else 0,
            "port": 8080,
            "bridge_port": 8100,
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/services/status")
def get_services_status():
    """Get status of all services"""
    service_manager.monitor_services()
    return jsonify(
        {"services": service_manager.services, "timestamp": datetime.now().isoformat()}
    )


@app.route("/api/services/<service_name>/start", methods=["POST"])
def start_service(service_name):
    """Start a service"""
    result = service_manager.start_service(service_name)
    return jsonify(result)


@app.route("/api/services/<service_name>/stop", methods=["POST"])
def stop_service(service_name):
    """Stop a service"""
    result = service_manager.stop_service(service_name)
    return jsonify(result)


@app.route("/api/services/<service_name>/info")
def get_service_info(service_name):
    """Get detailed service information"""
    info = service_manager.get_service_info(service_name)
    if info:
        return jsonify(info)
    return jsonify({"error": "Service not found"}), 404


if __name__ == "__main__":
    print("🚀 CoolBits.ai 🏢 Main Dashboard Starting...")
    print("=" * 50)
    print(f"Company: {service_manager.company}")
    print(f"CEO: {service_manager.ceo}")
    print("=" * 50)
    print("🌐 Main Dashboard: http://localhost:8080")
    print("🔌 API Endpoints: http://localhost:8080/api/")
    print("=" * 50)

    app.run(host="0.0.0.0", port=8080, debug=True)
