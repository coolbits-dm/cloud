#!/usr/bin/env python3
"""
CoolBits.ai - Service Manager
Manages all CoolBits services and processes
"""

import subprocess
import time
import json
import os
import sys
from datetime import datetime


class CoolBitsServiceManager:
    """CoolBits Service Manager"""

    def __init__(self):
        self.company = "COOL BITS SRL"
        self.ceo = "Andrei"
        self.services = {
            "main_dashboard": {
                "name": "Main Dashboard",
                "port": 8080,
                "script": "coolbits_main_dashboard.py",
                "description": "CoolBits.ai Main Dashboard",
            },
            "meta_platform": {
                "name": "Meta Platform",
                "port": 3003,
                "script": "meta_platform_server.py",
                "description": "Meta Platform Integration",
            },
            "andy_agent": {
                "name": "Andy Agent",
                "port": 8101,
                "script": "andy_agent_server.py",
                "description": "Personal 1:1 Agent for Andrei",
            },
            "kim_agent": {
                "name": "Kim Agent",
                "port": 8102,
                "script": "kim_agent_server.py",
                "description": "Reasoning & Analysis Agent",
            },
            "bits_orchestrator": {
                "name": "Bits Orchestrator",
                "port": 3001,
                "script": "bits_orchestrator_server.py",
                "description": "Bits Framework Orchestrator",
            },
        }

        self.running_processes = {}

    def start_service(self, service_name):
        """Start a service"""
        if service_name not in self.services:
            return {"status": "error", "message": "Service not found"}

        service = self.services[service_name]

        try:
            # Check if service is already running
            if service_name in self.running_processes:
                return {
                    "status": "already_running",
                    "message": f"{service['name']} is already running",
                }

            # Start the service
            print(f"🚀 Starting {service['name']}...")
            process = subprocess.Popen(
                [sys.executable, service["script"]],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.running_processes[service_name] = process

            # Wait a moment to check if it started successfully
            time.sleep(2)

            if process.poll() is None:
                return {
                    "status": "started",
                    "message": f"{service['name']} started successfully on port {service['port']}",
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to start {service['name']}",
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error starting {service['name']}: {str(e)}",
            }

    def stop_service(self, service_name):
        """Stop a service"""
        if service_name not in self.services:
            return {"status": "error", "message": "Service not found"}

        service = self.services[service_name]

        try:
            if service_name in self.running_processes:
                process = self.running_processes[service_name]
                process.terminate()
                process.wait(timeout=5)
                del self.running_processes[service_name]
                return {
                    "status": "stopped",
                    "message": f"{service['name']} stopped successfully",
                }
            else:
                return {
                    "status": "not_running",
                    "message": f"{service['name']} is not running",
                }

        except Exception as e:
            return {
                "status": "error",
                "message": f"Error stopping {service['name']}: {str(e)}",
            }

    def start_all_services(self):
        """Start all services"""
        results = {}

        print("🚀 Starting all CoolBits services...")
        print("=" * 50)
        print(f"Company: {self.company}")
        print(f"CEO: {self.ceo}")
        print("=" * 50)

        for service_name in self.services:
            result = self.start_service(service_name)
            results[service_name] = result
            print(f"{service_name}: {result['status']} - {result['message']}")
            time.sleep(1)  # Small delay between starts

        return results

    def stop_all_services(self):
        """Stop all services"""
        results = {}

        print("🛑 Stopping all CoolBits services...")
        print("=" * 50)

        for service_name in list(self.running_processes.keys()):
            result = self.stop_service(service_name)
            results[service_name] = result
            print(f"{service_name}: {result['status']} - {result['message']}")

        return results

    def get_status(self):
        """Get status of all services"""
        status = {}

        for service_name, service in self.services.items():
            is_running = service_name in self.running_processes
            process = self.running_processes.get(service_name)

            status[service_name] = {
                "name": service["name"],
                "port": service["port"],
                "description": service["description"],
                "running": is_running,
                "pid": process.pid if process and process.poll() is None else None,
                "url": f"http://localhost:{service['port']}",
            }

        return status

    def save_status(self):
        """Save current status to file"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "company": self.company,
            "ceo": self.ceo,
            "services": self.get_status(),
        }

        with open("coolbits_services_status.json", "w") as f:
            json.dump(status, f, indent=2)

        print("📁 Status saved to: coolbits_services_status.json")


def main():
    """Main function"""
    manager = CoolBitsServiceManager()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "start":
            if len(sys.argv) > 2:
                service_name = sys.argv[2]
                result = manager.start_service(service_name)
                print(f"{service_name}: {result['status']} - {result['message']}")
            else:
                manager.start_all_services()

        elif command == "stop":
            if len(sys.argv) > 2:
                service_name = sys.argv[2]
                result = manager.stop_service(service_name)
                print(f"{service_name}: {result['status']} - {result['message']}")
            else:
                manager.stop_all_services()

        elif command == "status":
            status = manager.get_status()
            print("📊 CoolBits Services Status:")
            print("=" * 50)
            for service_name, info in status.items():
                status_text = "🟢 Running" if info["running"] else "🔴 Stopped"
                print(f"{info['name']}: {status_text} (Port: {info['port']})")
                if info["running"]:
                    print(f"  URL: {info['url']}")
                    print(f"  PID: {info['pid']}")
                print()

        elif command == "save":
            manager.save_status()

        else:
            print("❌ Unknown command. Use: start, stop, status, save")

    else:
        # Interactive mode
        print("🚀 CoolBits.ai Service Manager")
        print("=" * 50)
        print(f"Company: {manager.company}")
        print(f"CEO: {manager.ceo}")
        print("=" * 50)
        print("Commands:")
        print("  start [service] - Start service or all services")
        print("  stop [service]  - Stop service or all services")
        print("  status          - Show status of all services")
        print("  save            - Save current status")
        print("=" * 50)

        while True:
            try:
                # Non-interactive mode check
                if os.getenv("CI") == "1" or os.getenv("NO_COLOR") == "1":
                    print(
                        "🔧 Non-interactive mode: Service manager running in background"
                    )
                    time.sleep(60)  # Sleep for 1 minute then check again
                    continue

                command = input("Enter command (or 'quit' to exit): ").strip().lower()

                if command == "quit":
                    break
                elif command == "start":
                    manager.start_all_services()
                elif command == "stop":
                    manager.stop_all_services()
                elif command == "status":
                    status = manager.get_status()
                    print("📊 CoolBits Services Status:")
                    for service_name, info in status.items():
                        status_text = "🟢 Running" if info["running"] else "🔴 Stopped"
                        print(f"{info['name']}: {status_text} (Port: {info['port']})")
                elif command == "save":
                    manager.save_status()
                else:
                    print("❌ Unknown command")

            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break


if __name__ == "__main__":
    main()
