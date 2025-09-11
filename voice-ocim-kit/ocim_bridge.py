#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCIM Bridge Server
SC COOL BITS SRL - Voice to OCIM Bridge
"""

import os
import json
import uuid
import time
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
from flask_cors import CORS

# Try to import redis, fallback to mock if not available
try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("⚠️ Redis not available, using mock implementation")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)


class OCIMBridge:
    """OCIM Bridge for Voice to @oPyC Communication"""

    def __init__(self):
        self.company = "SC COOL BITS SRL"
        self.ceo = "Andrei"
        self.protocol_version = "ocim-0.1"

        # Configuration from environment
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.stream_key = os.getenv("OCIM_STREAM", "opipe.ocim")
        self.target_agent = os.getenv("TARGET_AGENT", "opyc")
        self.bridge_port = int(os.getenv("BRIDGE_PORT", "7071"))

        # Initialize Redis connection
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis.from_url(self.redis_url)
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Redis connection established")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}")
                self.redis_client = None
        else:
            self.redis_client = None

        # Statistics
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "errors": 0,
            "start_time": time.time(),
        }

    def create_ocim_message(self, text: str, source: str = "voice") -> dict:
        """Create OCIM message from voice input"""
        message_id = f"evt_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()

        return {
            "ver": self.protocol_version,
            "id": message_id,
            "ts": timestamp,
            "from": {"agent": "voice-bridge", "role": "system"},
            "to": [self.target_agent],
            "flows": ["opipe.handshake", "coolbits-og-bridge"],
            "objective": "voice.command",
            "requires_ack": True,
            "ttl_s": 300,
            "corr_id": message_id,
            "parent_id": None,
            "sec": {
                "channel": "bits-secure",
                "sig_alg": "HMAC-SHA256",
                "replay_guard": {"nonce_ttl_s": 30},
                "clock_skew_tolerance_s": 10,
            },
            "payload": {
                "source": source,
                "text": text,
                "timestamp": int(time.time() * 1000),
                "session": f"voice_{int(time.time())}",
                "bridge_version": "1.0.0",
            },
        }

    def send_to_redis(self, message: dict) -> bool:
        """Send OCIM message to Redis Stream"""
        try:
            if not REDIS_AVAILABLE or not self.redis_client:
                logger.info(f"ℹ️ Mock mode: Would send to {self.stream_key}")
                logger.info(f"📤 Mock OCIM: {message['objective']} -> {message['to']}")
                return True

            # Add to Redis Stream
            self.redis_client.xadd(
                self.stream_key, {"ocim": json.dumps(message, separators=(",", ":"))}
            )

            logger.info(f"📤 OCIM sent: {message['objective']} -> {message['to']}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send to Redis: {e}")
            return False

    def get_health_status(self) -> dict:
        """Get health status"""
        redis_status = False
        if REDIS_AVAILABLE and self.redis_client:
            try:
                redis_status = self.redis_client.ping()
            except:
                redis_status = False

        uptime = time.time() - self.stats["start_time"]

        return {
            "ok": True,
            "redis": redis_status,
            "uptime_seconds": int(uptime),
            "stats": self.stats,
            "config": {
                "stream": self.stream_key,
                "target": self.target_agent,
                "port": self.bridge_port,
            },
        }


# Initialize bridge
bridge = OCIMBridge()


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify(bridge.get_health_status())


@app.route("/ocim", methods=["POST"])
def receive_ocim():
    """Receive OCIM message from voice interface"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        # Validate required fields
        if "payload" not in data or "text" not in data.get("payload", {}):
            return jsonify({"error": "Missing required fields: payload.text"}), 400

        # Update stats
        bridge.stats["messages_received"] += 1

        # Extract text
        text = data["payload"]["text"]
        source = data["payload"].get("source", "voice")

        logger.info(f"📥 Received voice input: '{text}' from {source}")

        # Create OCIM message
        ocim_message = bridge.create_ocim_message(text, source)

        # Send to Redis
        success = bridge.send_to_redis(ocim_message)

        if success:
            bridge.stats["messages_sent"] += 1
            return jsonify(
                {
                    "ok": True,
                    "message_id": ocim_message["id"],
                    "sent_to": ocim_message["to"],
                    "objective": ocim_message["objective"],
                }
            )
        else:
            bridge.stats["errors"] += 1
            return jsonify({"error": "Failed to send to Redis"}), 500

    except Exception as e:
        bridge.stats["errors"] += 1
        logger.error(f"❌ Error processing OCIM: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/stats", methods=["GET"])
def get_stats():
    """Get bridge statistics"""
    return jsonify(bridge.stats)


@app.route("/config", methods=["GET"])
def get_config():
    """Get bridge configuration"""
    return jsonify(
        {
            "redis_url": bridge.redis_url,
            "stream_key": bridge.stream_key,
            "target_agent": bridge.target_agent,
            "bridge_port": bridge.bridge_port,
            "redis_available": REDIS_AVAILABLE,
        }
    )


@app.route("/test", methods=["POST"])
def test_message():
    """Test endpoint for sending test messages"""
    try:
        data = request.get_json()
        test_text = data.get("text", "Test message from voice bridge")

        logger.info(f"🧪 Test message: '{test_text}'")

        # Create and send test OCIM message
        ocim_message = bridge.create_ocim_message(test_text, "test")
        success = bridge.send_to_redis(ocim_message)

        if success:
            return jsonify(
                {
                    "ok": True,
                    "message": "Test message sent successfully",
                    "message_id": ocim_message["id"],
                }
            )
        else:
            return jsonify({"error": "Failed to send test message"}), 500

    except Exception as e:
        logger.error(f"❌ Test message error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def index():
    """Index page"""
    return jsonify(
        {
            "service": "OCIM Bridge",
            "company": bridge.company,
            "ceo": bridge.ceo,
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "ocim": "/ocim (POST)",
                "stats": "/stats",
                "config": "/config",
                "test": "/test (POST)",
            },
            "classification": "Internal Secret - CoolBits.ai Members Only",
        }
    )


if __name__ == "__main__":
    print("=" * 80)
    print("🌉 OCIM BRIDGE SERVER")
    print("=" * 80)
    print(f"Company: {bridge.company}")
    print(f"CEO: {bridge.ceo}")
    print(f"Port: {bridge.bridge_port}")
    print(f"Stream: {bridge.stream_key}")
    print(f"Target: {bridge.target_agent}")
    print(
        f"Redis: {'Available' if REDIS_AVAILABLE and bridge.redis_client else 'Mock Mode'}"
    )
    print("=" * 80)

    # Start server
    app.run(host="0.0.0.0", port=bridge.bridge_port, debug=False, threaded=True)
