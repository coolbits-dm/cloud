#!/usr/bin/env python3
"""
Agent Discovery Service
Local/LAN discovery & agents.yaml synthesis
"""

import argparse
import logging
import socket
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AgentDiscovery:
    def __init__(self, config_path="config/board.agents.yaml"):
        self.config_path = config_path
        self.discovered_agents = []

    def scan_local_ports(self):
        """Scan local ports for potential agents"""
        logger.info("🔍 Scanning local ports...")

        common_ports = [8080, 8081, 8765, 8766, 9000, 9001]
        local_agents = []

        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(("127.0.0.1", port))

                if result == 0:
                    # Port is open, try to identify service
                    agent_info = self.identify_service(port)
                    if agent_info:
                        local_agents.append(agent_info)
                        logger.info(
                            f"✅ Found agent on port {port}: {agent_info['name']}"
                        )

                sock.close()

            except Exception as e:
                logger.debug(f"Port {port} scan error: {e}")

        return local_agents

    def identify_service(self, port):
        """Try to identify service running on port"""
        try:
            # Try to connect and get basic info
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect(("127.0.0.1", port))

            # Send basic HTTP request
            sock.send(b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n")
            response = sock.recv(1024).decode("utf-8", errors="ignore")

            sock.close()

            # Parse response for service identification
            if "oCopilot" in response or "Cursor" in response:
                return {
                    "id": f"ocursor-{port}",
                    "name": "oCursor",
                    "type": "LLM",
                    "host": "127.0.0.1",
                    "port": port,
                    "protocols": ["ocim-ws-0.1", "http-json"],
                    "heartbeat_url": f"ws://127.0.0.1:{port}/heartbeat",
                    "status": "unknown",
                    "capabilities": ["mic", "camera"],
                    "tags": ["offline", "local"],
                    "last_seen": None,
                }
            elif "FastAPI" in response or "uvicorn" in response:
                return {
                    "id": f"fastapi-{port}",
                    "name": "FastAPI Service",
                    "type": "API",
                    "host": "127.0.0.1",
                    "port": port,
                    "protocols": ["http-json"],
                    "heartbeat_url": f"http://127.0.0.1:{port}/health",
                    "status": "unknown",
                    "capabilities": ["api"],
                    "tags": ["local"],
                    "last_seen": None,
                }

        except Exception as e:
            logger.debug(f"Service identification error for port {port}: {e}")

        return None

    def scan_lan_subnet(self):
        """Scan LAN subnet for potential agents"""
        logger.info("🌐 Scanning LAN subnet...")

        # Get local IP
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            subnet = ".".join(local_ip.split(".")[:-1]) + "."

            logger.info(f"📡 Scanning subnet: {subnet}0/24")

            # Scan common ports on subnet
            lan_agents = []
            for i in range(1, 255):
                ip = subnet + str(i)
                if ip == local_ip:
                    continue

                # Quick ping test
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5)
                    result = sock.connect_ex((ip, 8080))

                    if result == 0:
                        agent_info = {
                            "id": f"lan-{ip.replace('.', '-')}",
                            "name": f"LAN Agent {ip}",
                            "type": "Unknown",
                            "host": ip,
                            "port": 8080,
                            "protocols": ["http-json"],
                            "heartbeat_url": f"http://{ip}:8080/health",
                            "status": "unknown",
                            "capabilities": ["api"],
                            "tags": ["lan", "remote"],
                            "last_seen": None,
                        }
                        lan_agents.append(agent_info)
                        logger.info(f"✅ Found LAN agent: {ip}")

                    sock.close()

                except Exception:
                    pass

        except Exception as e:
            logger.error(f"LAN scan error: {e}")

        return lan_agents

    def discover_agents(self):
        """Main discovery process"""
        logger.info("🎯 Starting agent discovery...")

        # Scan local ports
        local_agents = self.scan_local_ports()

        # Scan LAN subnet
        lan_agents = self.scan_lan_subnet()

        # Combine results
        self.discovered_agents = local_agents + lan_agents

        logger.info(
            f"📊 Discovery complete: {len(self.discovered_agents)} agents found"
        )

        return self.discovered_agents

    def write_agents_yaml(self):
        """Write discovered agents to YAML file"""
        try:
            agents_data = {"agents": self.discovered_agents}

            with open(self.config_path, "w") as f:
                yaml.dump(agents_data, f, default_flow_style=False)

            logger.info(
                f"📝 Written {len(self.discovered_agents)} agents to {self.config_path}"
            )

        except Exception as e:
            logger.error(f"Error writing agents.yaml: {e}")

    def sync_library(self):
        """Sync with board.library.yaml"""
        try:
            library_path = "config/board.library.yaml"

            # Load existing library
            if Path(library_path).exists():
                with open(library_path, "r") as f:
                    library_data = yaml.safe_load(f)
            else:
                library_data = {"version": 1, "agents": []}

            # Update agents from discovery
            library_data["agents"] = []
            for agent in self.discovered_agents:
                library_agent = {
                    "id": agent["id"],
                    "name": agent["name"],
                    "tip_ai": agent["type"],
                    "functii": agent["capabilities"],
                    "sync_status": "pending",
                    "endpoints": {
                        "control": agent["heartbeat_url"],
                        "heartbeat": agent["heartbeat_url"],
                    },
                }
                library_data["agents"].append(library_agent)

            # Write updated library
            with open(library_path, "w") as f:
                yaml.dump(library_data, f, default_flow_style=False)

            logger.info(f"📚 Synced library with {len(self.discovered_agents)} agents")

        except Exception as e:
            logger.error(f"Error syncing library: {e}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Agent Discovery Service")
    parser.add_argument(
        "--write", action="store_true", help="Write discovered agents to YAML"
    )
    parser.add_argument(
        "--sync-library", action="store_true", help="Sync with board.library.yaml"
    )

    args = parser.parse_args()

    discovery = AgentDiscovery()

    # Run discovery
    discovery.discover_agents()

    # Write results if requested
    if args.write:
        discovery.write_agents_yaml()

    # Sync library if requested
    if args.sync_library:
        discovery.sync_library()

    logger.info("✅ Agent discovery completed")


if __name__ == "__main__":
    main()
