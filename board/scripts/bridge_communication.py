#!/usr/bin/env python3
"""
Bridge Communication Service
WebSocket bridge + registry + heartbeat for oCopilot Board Orchestrator
"""

import asyncio
import json
import logging
import websockets
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class BoardBridge:
    def __init__(self, config_path="config/board.agents.yaml"):
        self.config_path = config_path
        self.agents = {}
        self.connections = {}
        self.running = False

    async def register_agent(self, websocket, message):
        """Register a new agent"""
        agent_id = message.get("id")
        agent_meta = message.get("meta", {})

        self.agents[agent_id] = {
            "id": agent_id,
            "name": agent_meta.get("name", agent_id),
            "type": agent_meta.get("type", "unknown"),
            "protocols": agent_meta.get("protocols", []),
            "capabilities": agent_meta.get("capabilities", []),
            "tags": agent_meta.get("tags", []),
            "last_seen": datetime.now().isoformat(),
            "status": "connected",
        }

        self.connections[agent_id] = websocket

        # Send registration acknowledgment
        await websocket.send(
            json.dumps({"type": "register_ack", "id": agent_id, "status": "registered"})
        )

        logger.info(f"✅ Agent registered: {agent_id}")

        # Update agents.yaml
        await self.update_agents_yaml()

    async def handle_heartbeat(self, websocket, message):
        """Handle heartbeat from agent"""
        agent_id = message.get("id")

        if agent_id in self.agents:
            self.agents[agent_id]["last_seen"] = datetime.now().isoformat()
            self.agents[agent_id]["status"] = "active"

            # Send heartbeat acknowledgment
            await websocket.send(
                json.dumps(
                    {
                        "type": "heartbeat_ack",
                        "id": agent_id,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
            )

            logger.info(f"💓 Heartbeat from: {agent_id}")

    async def handle_message(self, websocket, message):
        """Handle incoming message from agent"""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "register":
                await self.register_agent(websocket, data)
            elif msg_type == "heartbeat":
                await self.handle_heartbeat(websocket, data)
            else:
                logger.warning(f"Unknown message type: {msg_type}")

        except json.JSONDecodeError:
            logger.error("Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message: {e}")

    async def update_agents_yaml(self):
        """Update agents.yaml file"""
        try:
            agents_data = {"agents": list(self.agents.values())}

            with open(self.config_path, "w") as f:
                yaml.dump(agents_data, f, default_flow_style=False)

            logger.info(f"📝 Updated {self.config_path}")

        except Exception as e:
            logger.error(f"Error updating agents.yaml: {e}")

    async def handle_connection(self, websocket, path):
        """Handle new WebSocket connection"""
        logger.info(f"🔌 New connection: {websocket.remote_address}")

        try:
            async for message in websocket:
                await self.handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Connection closed: {websocket.remote_address}")
        except Exception as e:
            logger.error(f"Connection error: {e}")
        finally:
            # Remove connection from registry
            for agent_id, conn in list(self.connections.items()):
                if conn == websocket:
                    del self.connections[agent_id]
                    if agent_id in self.agents:
                        self.agents[agent_id]["status"] = "disconnected"
                    break

    async def start_server(self, host="localhost", port=7781):
        """Start WebSocket server"""
        logger.info(f"🚀 Starting Board Bridge on ws://{host}:{port}")

        self.running = True

        async with websockets.serve(self.handle_connection, host, port):
            logger.info("✅ Board Bridge is running")
            logger.info("📡 Waiting for agent connections...")

            # Keep server running
            await asyncio.Future()


def main():
    """Main entry point"""
    bridge = BoardBridge()

    try:
        asyncio.run(bridge.start_server())
    except KeyboardInterrupt:
        logger.info("🛑 Board Bridge stopped")
    except Exception as e:
        logger.error(f"❌ Bridge error: {e}")


if __name__ == "__main__":
    main()
