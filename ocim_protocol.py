#!/usr/bin/env python3
"""
OCIM Protocol Implementation - CoolBits.ai Agent Communication
Non-lins-in-cur mindset enforcement system
"""

import json
import hmac
import hashlib
import time
from datetime import datetime
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCIMProtocol:
    """OCIM Protocol Handler with non-lins-in-cur enforcement"""

    def __init__(self):
        self.version = "ocim-0.1"
        self.integrity_threshold = 0.85
        self.audit_flags = []
        self.message_history = []

    def generate_hmac_signature(
        self, message_data: Dict[str, Any], secret_key: str
    ) -> str:
        """Generate HMAC-SHA256 signature for OCIM message"""
        message_str = json.dumps(message_data, sort_keys=True, separators=(",", ":"))
        signature = hmac.new(
            secret_key.encode("utf-8"), message_str.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    def create_ocim_broadcast(
        self, objective: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create OCIM broadcast message"""
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S+03:00")
        nonce = f"x{int(time.time() * 1000) % 0xFFFFFF:06x}"

        message_data = {
            "ver": self.version,
            "id": f"mindset.broadcast.{int(time.time())}",
            "ts": timestamp,
            "from": {"agent": "oCopilot", "role": "orchestrator"},
            "to": ["oCopilot-Grok", "oCopilot-Cursor", "cblm.ai-Core"],
            "flows": ["coolbits-og-bridge", "cblm-core"],
            "objective": objective,
            "requires_ack": True,
            "sec": {
                "channel": "bits-secure",
                "sig_alg": "HMAC-SHA256",
                "nonce": nonce,
                "__sig": "<placeholder>",
            },
            "body": {
                "type": "directive",
                "action": "adopt.mindset",
                "payload": payload,
            },
        }

        # Generate signature
        secret_key = "coolbits-secure-channel-key-2025"
        signature = self.generate_hmac_signature(message_data, secret_key)
        message_data["sec"]["__sig"] = signature

        return message_data

    def calculate_integrity_score(self, message: str) -> float:
        """Calculate integrity score based on message honesty"""
        # Simple heuristic for detecting "sugarcoating"
        sugar_words = [
            "excellent",
            "amazing",
            "fantastic",
            "perfect",
            "outstanding",
            "brilliant",
        ]
        soft_words = ["might", "could", "perhaps", "maybe", "possibly", "potentially"]

        message_lower = message.lower()
        sugar_count = sum(1 for word in sugar_words if word in message_lower)
        soft_count = sum(1 for word in soft_words if word in message_lower)

        # Penalize excessive sugarcoating
        sugar_penalty = min(sugar_count * 0.1, 0.3)
        soft_penalty = min(soft_count * 0.05, 0.2)

        base_score = 1.0
        integrity_score = max(base_score - sugar_penalty - soft_penalty, 0.0)

        return integrity_score

    def audit_message(self, message: str, agent: str) -> Dict[str, Any]:
        """Audit message for compliance with non-lins-in-cur protocol"""
        integrity_score = self.calculate_integrity_score(message)

        audit_result = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "message": message,
            "integrity_score": integrity_score,
            "compliance": integrity_score >= self.integrity_threshold,
            "flags": [],
        }

        if integrity_score < self.integrity_threshold:
            audit_result["flags"].append("audit.flag.softbias")
            logger.warning(
                f"⚠️ Agent {agent} flagged for softbias - Score: {integrity_score:.2f}"
            )

        self.audit_flags.append(audit_result)
        return audit_result

    def process_agent_response(self, agent: str, response: str) -> Dict[str, Any]:
        """Process agent response with OCIM protocol"""
        audit_result = self.audit_message(response, agent)

        ocim_response = {
            "ver": self.version,
            "id": f"response.{agent}.{int(time.time())}",
            "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+03:00"),
            "from": {"agent": agent, "role": "responder"},
            "to": ["oCopilot"],
            "ack": "accepted",
            "mindset": "non-lins-in-cur",
            "integrity_score": audit_result["integrity_score"],
            "response": response,
            "audit": audit_result,
        }

        self.message_history.append(ocim_response)
        return ocim_response


# Initialize OCIM Protocol
ocim = OCIMProtocol()

# Generate the OCIM broadcast for non-lins-in-cur protocol
ocim_broadcast = ocim.create_ocim_broadcast(
    objective="protocol.update",
    payload={
        "rule": "non-lins-in-cur",
        "enforce": True,
        "audit": True,
        "integrity_score_threshold": 0.85,
    },
)

print("🔔 OCIM Broadcast Generated:")
print(json.dumps(ocim_broadcast, indent=2))

# Simulate agent responses
agents = ["oCopilot-Grok", "oCopilot-Cursor", "cblm.ai-Core"]
responses = [
    "Protocol acknowledged. Direct communication mode activated. No sugarcoating.",
    "Mindset updated. Status reports will reflect actual conditions only.",
    "Business logic aligned with non-lins-in-cur directive. Audit trail enabled.",
]

print("\n📣 Agent Confirmations:")
for agent, response in zip(agents, responses):
    ocim_response = ocim.process_agent_response(agent, response)
    print(f"\n{agent}:")
    print(f"  Integrity Score: {ocim_response['integrity_score']:.2f}")
    print(f"  Response: {response}")
    print(f"  Compliance: {'✅' if ocim_response['audit']['compliance'] else '❌'}")

print("\n📊 Audit Summary:")
print(f"  Total Messages: {len(ocim.message_history)}")
print(
    f"  Compliance Rate: {sum(1 for msg in ocim.message_history if msg['audit']['compliance']) / len(ocim.message_history) * 100:.1f}%"
)
print(f"  Flags Raised: {len(ocim.audit_flags)}")
