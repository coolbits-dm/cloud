#!/usr/bin/env python3
"""
CoolBits.ai ↔ cblm.ai Agent Bridge Communication Module
Handles offline communication between all agent instances
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentBridge:
    """Bridge for communication between CoolBits.ai and cblm.ai agents"""

    def __init__(self, config_path: str = "coolbits_cblm_bridge.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.message_queue = []
        self.agents_status = {}
        self.running = False

    def load_config(self) -> Dict[str, Any]:
        """Load bridge configuration"""
        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Configuration file {self.config_path} not found")
            return {}

    def start_bridge(self):
        """Start the bridge communication system"""
        logger.info("🌉 Starting CoolBits.ai ↔ cblm.ai Agent Bridge")
        self.running = True

        # Initialize agent statuses
        for agent_type, agents in self.config.get("agents", {}).items():
            for agent_name, agent_config in agents.items():
                self.agents_status[agent_name] = {
                    "status": agent_config.get("status", "unknown"),
                    "last_seen": datetime.now().isoformat(),
                    "message_count": 0,
                }

        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_agents)
        monitor_thread.daemon = True
        monitor_thread.start()

        logger.info("✅ Bridge communication system started")

    def stop_bridge(self):
        """Stop the bridge communication system"""
        logger.info("🛑 Stopping Agent Bridge")
        self.running = False

    def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """Send message between agents"""
        message_data = {
            "timestamp": datetime.now().isoformat(),
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "id": f"{int(time.time() * 1000)}",
        }

        self.message_queue.append(message_data)

        # Update agent status
        if from_agent in self.agents_status:
            self.agents_status[from_agent]["last_seen"] = datetime.now().isoformat()
            self.agents_status[from_agent]["message_count"] += 1

        logger.info(f"📤 Message sent: {from_agent} → {to_agent}")
        return message_data["id"]

    def get_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get messages for specific agent"""
        messages = [msg for msg in self.message_queue if msg["to"] == agent_name]
        return messages

    def get_bridge_status(self) -> Dict[str, Any]:
        """Get current bridge status"""
        return {
            "bridge_status": "active" if self.running else "stopped",
            "agents": self.agents_status,
            "message_queue_size": len(self.message_queue),
            "config_loaded": bool(self.config),
            "timestamp": datetime.now().isoformat(),
        }

    def _monitor_agents(self):
        """Monitor agent health and communication"""
        while self.running:
            try:
                # Check agent health
                current_time = datetime.now()
                for agent_name, status in self.agents_status.items():
                    last_seen = datetime.fromisoformat(status["last_seen"])
                    time_diff = (current_time - last_seen).total_seconds()

                    if time_diff > 300:  # 5 minutes
                        status["status"] = "disconnected"
                        logger.warning(f"⚠️ Agent {agent_name} appears disconnected")

                time.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"Error in agent monitoring: {e}")
                time.sleep(30)


# Agent communication functions
def communicate_with_ocopilot_windows(message: str) -> str:
    """Communicate with oCopilot (Windows Copilot)"""
    return f"oCopilot (Windows): Received - {message}"


def communicate_with_ocopilot_chatgpt(message: str) -> str:
    """Communicate with oCopilot (ChatGPT Agent)"""
    return f"oCopilot (ChatGPT): Processed - {message}"


def communicate_with_ocopilot_grok(message: str) -> str:
    """Communicate with oCopilot (Grok Agent)"""
    return f"oCopilot (Grok): Analyzed - {message}"


def communicate_with_cblm_core(message: str) -> str:
    """Communicate with cblm.ai Core Agent"""
    return f"cblm.ai Core: Responded - {message}"


# Main bridge instance
bridge = AgentBridge()

if __name__ == "__main__":
    # Start the bridge
    bridge.start_bridge()

    try:
        # Example communication
        bridge.send_message(
            "ocopilot_chatgpt",
            "ocopilot_grok",
            {"type": "analysis_request", "data": "System status check"},
        )

        bridge.send_message(
            "ocopilot_windows",
            "cblm_core",
            {"type": "system_info", "data": "Windows 11 + RTX 2060 + CUDA 12.6"},
        )

        # Keep running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        bridge.stop_bridge()
        logger.info("Bridge stopped by user")
