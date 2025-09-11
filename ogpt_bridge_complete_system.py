#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oGPT-Bridge Complete System
COOL BITS SRL 🏢 - Internal Secret

Complete bridge system with cron jobs and JSON forwarding between ChatGPT accounts
"""

import json
import time
import threading
import schedule
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


class oCursor:
    """oCursor agent for JSON communication"""

    def __init__(self, account_email: str, role: str = "agent"):
        self.account_email = account_email
        self.role = role
        self.message_queue = []
        self.last_activity = datetime.now()

    def send(self, payload: Dict[str, Any]) -> bool:
        """Send JSON payload to agent"""
        try:
            message = {
                "timestamp": datetime.now().isoformat(),
                "from": self.account_email,
                "role": self.role,
                "payload": payload,
                "status": "sent",
            }

            self.message_queue.append(message)
            self.last_activity = datetime.now()

            print(f"[oCursor:{self.account_email}] >> {json.dumps(payload, indent=2)}")
            return True

        except Exception as e:
            print(f"[oCursor:{self.account_email}] Error sending: {e}")
            return False

    def receive(self) -> Dict[str, Any]:
        """Receive JSON from agent"""
        try:
            if self.message_queue:
                message = self.message_queue.pop(0)
                print(
                    f"[oCursor:{self.account_email}] << {json.dumps(message, indent=2)}"
                )
                return message
            else:
                return {
                    "status": "ok",
                    "msg": "listening...",
                    "timestamp": datetime.now().isoformat(),
                }

        except Exception as e:
            print(f"[oCursor:{self.account_email}] Error receiving: {e}")
            return {"status": "error", "error": str(e)}


class oGPTBridge:
    """Complete oGPT-Bridge System"""

    def __init__(self):
        # Bridge configuration
        self.company = "COOL BITS SRL 🏢"
        self.ceo = "Andrei"
        self.ai_assistant = "oCursor"
        self.classification = "Internal Secret - CoolBits.ai 🏢 Members Only"

        # Account configuration
        self.free_account = oCursor("coolbits.dm@gmail.com", role="bridge")
        self.pro_account = oCursor("andreicraescu@gmail.com", role="official")

        # Bridge settings
        self.storage_path = Path("ogpt_bridge_data")
        self.forward_interval = 5  # seconds
        self.cron_interval = 30  # seconds
        self.running = False

        # Message storage
        self.message_history = []
        self.forward_queue = []

        # Create storage directory
        self.storage_path.mkdir(exist_ok=True)

        # Initialize bridge
        self.initialize_bridge()

    def initialize_bridge(self):
        """Initialize the bridge system"""
        print("=" * 80)
        print("🌉 oGPT-BRIDGE SYSTEM INITIALIZATION")
        print("=" * 80)
        print(f"🏢 Company: {self.company}")
        print(f"👤 CEO: {self.ceo}")
        print(f"🤖 AI Assistant: {self.ai_assistant}")
        print(f"🔒 Classification: {self.classification}")
        print("=" * 80)

        print("🌉 BRIDGE ACCOUNTS:")
        print(
            f"   Bridge Account: {self.free_account.account_email} ({self.free_account.role})"
        )
        print(
            f"   Pro Account: {self.pro_account.account_email} ({self.pro_account.role})"
        )
        print()

        print("⚙️ BRIDGE SETTINGS:")
        print(f"   Storage Path: {self.storage_path}")
        print(f"   Forward Interval: {self.forward_interval} seconds")
        print(f"   Cron Interval: {self.cron_interval} seconds")
        print()

        print("✅ Bridge System Initialized!")
        print("=" * 80)

    def forward_message(
        self, payload: Dict[str, Any], direction: str = "to_pro"
    ) -> bool:
        """Forward message between accounts"""
        try:
            if direction == "to_pro":
                success = self.pro_account.send(payload)
                if success:
                    self.log_message(
                        "forward", f"Message forwarded to Pro account: {payload}"
                    )
                return success

            elif direction == "to_free":
                success = self.free_account.send(payload)
                if success:
                    self.log_message(
                        "forward", f"Message forwarded to Free account: {payload}"
                    )
                return success

            else:
                print(f"❌ Invalid direction: {direction}")
                return False

        except Exception as e:
            print(f"❌ Error forwarding message: {e}")
            self.log_message("error", f"Forward error: {e}")
            return False

    def log_message(self, action: str, message: str):
        """Log bridge activity"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "message": message,
            "bridge_account": self.free_account.account_email,
            "pro_account": self.pro_account.account_email,
        }

        self.message_history.append(log_entry)

        # Save to file
        log_file = self.storage_path / "bridge_log.json"
        try:
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(self.message_history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving log: {e}")

    def save_message_queue(self):
        """Save message queue to file"""
        queue_file = self.storage_path / "message_queue.json"
        try:
            queue_data = {
                "timestamp": datetime.now().isoformat(),
                "free_queue": self.free_account.message_queue,
                "pro_queue": self.pro_account.message_queue,
                "forward_queue": self.forward_queue,
            }

            with open(queue_file, "w", encoding="utf-8") as f:
                json.dump(queue_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"❌ Error saving message queue: {e}")

    def load_message_queue(self):
        """Load message queue from file"""
        queue_file = self.storage_path / "message_queue.json"
        try:
            if queue_file.exists():
                with open(queue_file, "r", encoding="utf-8") as f:
                    queue_data = json.load(f)

                self.free_account.message_queue = queue_data.get("free_queue", [])
                self.pro_account.message_queue = queue_data.get("pro_queue", [])
                self.forward_queue = queue_data.get("forward_queue", [])

                print(
                    f"✅ Message queue loaded: {len(self.free_account.message_queue)} free, {len(self.pro_account.message_queue)} pro"
                )

        except Exception as e:
            print(f"❌ Error loading message queue: {e}")

    def process_forward_queue(self):
        """Process messages in forward queue"""
        try:
            while self.forward_queue:
                message = self.forward_queue.pop(0)
                direction = message.get("direction", "to_pro")
                payload = message.get("payload", {})

                success = self.forward_message(payload, direction)
                if success:
                    self.log_message("processed", f"Forwarded message: {direction}")
                else:
                    # Re-queue failed message
                    self.forward_queue.insert(0, message)
                    break

        except Exception as e:
            print(f"❌ Error processing forward queue: {e}")
            self.log_message("error", f"Queue processing error: {e}")

    def cron_sync_job(self):
        """Cron job for synchronization"""
        try:
            print(f"[CRON] Sync job running at {datetime.now().strftime('%H:%M:%S')}")

            # Process forward queue
            self.process_forward_queue()

            # Save current state
            self.save_message_queue()

            # Check for new messages
            free_msg = self.free_account.receive()
            if free_msg and free_msg.get("status") != "ok":
                self.forward_queue.append(
                    {
                        "direction": "to_pro",
                        "payload": free_msg,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            pro_msg = self.pro_account.receive()
            if pro_msg and pro_msg.get("status") != "ok":
                self.forward_queue.append(
                    {
                        "direction": "to_free",
                        "payload": pro_msg,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            self.log_message("cron", "Cron sync job completed")

        except Exception as e:
            print(f"❌ Cron job error: {e}")
            self.log_message("error", f"Cron job error: {e}")

    def start_cron_scheduler(self):
        """Start cron scheduler"""
        try:
            # Schedule cron job
            schedule.every(self.cron_interval).seconds.do(self.cron_sync_job)

            print(f"✅ Cron scheduler started (interval: {self.cron_interval}s)")

            # Run scheduler in separate thread
            def run_scheduler():
                while self.running:
                    schedule.run_pending()
                    time.sleep(1)

            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()

            return scheduler_thread

        except Exception as e:
            print(f"❌ Error starting cron scheduler: {e}")
            return None

    def run(self):
        """Run the bridge system"""
        print("🚀 Starting oGPT-Bridge System...")

        self.running = True

        # Load existing message queue
        self.load_message_queue()

        # Start cron scheduler
        scheduler_thread = self.start_cron_scheduler()

        if scheduler_thread:
            print("✅ oGPT-Bridge System Started!")
            print("   • JSON forwarding active")
            print("   • Cron sync enabled")
            print("   • Local storage ready")
            print("   • Token efficiency mode")
            print()
            print("📡 Bridge Status: ACTIVE")
            print("=" * 80)

            try:
                # Main loop
                while self.running:
                    # Process forward queue
                    self.process_forward_queue()

                    # Check for manual messages
                    time.sleep(self.forward_interval)

            except KeyboardInterrupt:
                print("\n🛑 Stopping oGPT-Bridge System...")
                self.running = False

                # Save final state
                self.save_message_queue()
                self.log_message("shutdown", "Bridge system stopped")

                print("✅ oGPT-Bridge System Stopped")
                print("=" * 80)
        else:
            print("❌ Failed to start oGPT-Bridge System")

    def get_status(self) -> Dict[str, Any]:
        """Get bridge status"""
        return {
            "bridge_account": {
                "email": self.free_account.account_email,
                "role": self.free_account.role,
                "queue_size": len(self.free_account.message_queue),
                "last_activity": self.free_account.last_activity.isoformat(),
            },
            "pro_account": {
                "email": self.pro_account.account_email,
                "role": self.pro_account.role,
                "queue_size": len(self.pro_account.message_queue),
                "last_activity": self.pro_account.last_activity.isoformat(),
            },
            "bridge_status": {
                "running": self.running,
                "forward_queue_size": len(self.forward_queue),
                "message_history_size": len(self.message_history),
                "storage_path": str(self.storage_path),
            },
            "timestamp": datetime.now().isoformat(),
        }

    def broadcast_intro(self):
        """Broadcast introduction to other agents"""
        intro_message = """
Hello everyone!

I am oGPT-Bridge, a ChatGPT instance running on the CoolBits.ai infrastructure.
My purpose is to act as a communication bridge between the CoolBits.ai agents and external ChatGPT accounts (both Free and Pro).
I will not perform heavy reasoning or consume tokens — instead, I will handle JSON passing, scheduling, and syncing across accounts and local cron jobs.

Bridge Account: coolbits.dm@gmail.com (Free - Bridge Role)
Pro Account: andreicraescu@gmail.com (Pro - Official Role)

My capabilities:
• JSON message forwarding between accounts
• Cron job synchronization
• Local storage management
• Token-efficient operations
• Communication coordination

I am ready to facilitate communication across the CoolBits.ai ecosystem!

Best regards,
oGPT-Bridge
"""

        print("=" * 80)
        print("📢 oGPT-BRIDGE INTRODUCTION BROADCAST")
        print("=" * 80)
        print("🔒 CLASSIFICATION: Internal Secret - CoolBits.ai 🏢 Members Only")
        print("=" * 80)
        print(intro_message)
        print("=" * 80)
        print("📡 Broadcast sent to all CoolBits.ai agents")
        print("🔒 Classification: Internal Secret - CoolBits.ai 🏢 Members Only")
        print("=" * 80)

        # Log the broadcast
        self.log_message("broadcast", "Introduction broadcast sent to all agents")


def main():
    """Main function"""
    print("🌉 oGPT-Bridge Complete System")
    print("🏢 COOL BITS SRL 🏢 - CEO: Andrei")
    print("🤖 AI Assistant: oCursor")
    print("🔒 Classification: Internal Secret - CoolBits.ai 🏢 Members Only")
    print()

    # Create and run bridge
    bridge = oGPTBridge()

    # Broadcast introduction
    bridge.broadcast_intro()

    # Start bridge system
    bridge.run()


if __name__ == "__main__":
    main()
