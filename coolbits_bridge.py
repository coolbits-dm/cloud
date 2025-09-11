# CoolBits.ai Bridge Communication Protocol
# Communication bridge between Cursor/oCursor and oGeminiCLI

import json
import time
from datetime import datetime
import os


class CoolBitsBridge:
    def __init__(self):
        self.bridge_file = "coolbits_bridge.json"
        self.message_queue = []
        self.connected = False

    def initialize_bridge(self):
        """Initialize the communication bridge"""
        bridge_data = {
            "timestamp": datetime.now().isoformat(),
            "status": "initialized",
            "cursor_connected": True,
            "gemini_cli_connected": False,
            "messages": [],
            "commands": [],
            "responses": [],
        }

        with open(self.bridge_file, "w") as f:
            json.dump(bridge_data, f, indent=2)

        print("🌉 CoolBits Bridge initialized")

    def send_to_gemini_cli(self, message, command_type="message"):
        """Send message to oGeminiCLI"""
        bridge_data = self.load_bridge_data()

        message_data = {
            "timestamp": datetime.now().isoformat(),
            "from": "cursor_ocursor",
            "to": "ogemini_cli",
            "type": command_type,
            "content": message,
            "status": "sent",
        }

        bridge_data["messages"].append(message_data)
        bridge_data["commands"].append(message_data)

        self.save_bridge_data(bridge_data)
        print(f"📤 Sent to oGeminiCLI: {message}")

        return message_data

    def receive_from_gemini_cli(self):
        """Receive response from oGeminiCLI"""
        bridge_data = self.load_bridge_data()

        # Look for new responses
        new_responses = []
        for response in bridge_data.get("responses", []):
            if response.get("status") == "new":
                new_responses.append(response)
                response["status"] = "read"

        if new_responses:
            self.save_bridge_data(bridge_data)
            print(f"📥 Received from oGeminiCLI: {len(new_responses)} messages")
            return new_responses

        return []

    def send_command(self, command, parameters=None):
        """Send command to oGeminiCLI"""
        command_data = {
            "timestamp": datetime.now().isoformat(),
            "from": "cursor_ocursor",
            "to": "ogemini_cli",
            "type": "command",
            "command": command,
            "parameters": parameters or {},
            "status": "pending",
        }

        bridge_data = self.load_bridge_data()
        bridge_data["commands"].append(command_data)
        self.save_bridge_data(bridge_data)

        print(f"⚡ Command sent: {command}")
        return command_data

    def wait_for_response(self, command_id, timeout=30):
        """Wait for response to a specific command"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            bridge_data = self.load_bridge_data()

            for response in bridge_data.get("responses", []):
                if (
                    response.get("command_id") == command_id
                    and response.get("status") == "new"
                ):
                    response["status"] = "read"
                    self.save_bridge_data(bridge_data)
                    return response

            time.sleep(1)

        return None

    def load_bridge_data(self):
        """Load bridge data from file"""
        try:
            if os.path.exists(self.bridge_file):
                with open(self.bridge_file, "r") as f:
                    return json.load(f)
            else:
                return {"messages": [], "commands": [], "responses": []}
        except Exception as e:
            print(f"Error loading bridge data: {e}")
            return {"messages": [], "commands": [], "responses": []}

    def save_bridge_data(self, data):
        """Save bridge data to file"""
        try:
            with open(self.bridge_file, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving bridge data: {e}")

    def get_status(self):
        """Get bridge status"""
        bridge_data = self.load_bridge_data()
        return {
            "cursor_connected": bridge_data.get("cursor_connected", False),
            "gemini_cli_connected": bridge_data.get("gemini_cli_connected", False),
            "total_messages": len(bridge_data.get("messages", [])),
            "pending_commands": len(
                [
                    c
                    for c in bridge_data.get("commands", [])
                    if c.get("status") == "pending"
                ]
            ),
            "new_responses": len(
                [
                    r
                    for r in bridge_data.get("responses", [])
                    if r.get("status") == "new"
                ]
            ),
        }


# Example usage
def main():
    bridge = CoolBitsBridge()
    bridge.initialize_bridge()

    # Send message to oGeminiCLI
    bridge.send_to_gemini_cli("Hello oGeminiCLI! Ready for cloud operations.")

    # Send command
    bridge.send_command(
        "check_cloud_run", {"region": "europe-west3", "project": "coolbits-og-bridge"}
    )

    # Check status
    status = bridge.get_status()
    print(f"Bridge Status: {status}")


if __name__ == "__main__":
    main()
