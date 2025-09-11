#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@oPipe® Bridge - Zero-Trust Gateway to str.py
CoolBits.ai / cbLM.ai - Internal Bridge System

Bridge @oPipe® ↔ str.py (confidențial)
- str.py rămâne privat. Nicio citire, niciun dump, niciun LLM train.
- Interfață minimă, stabilă, pentru rutare și inferență GPU prin @oPipe®.
- Principiu: zero-trust. Totul semnat, totul logat. Fail-closed.

Author: oPipe® Agent (oCursor)
Company: COOL BITS SRL
"""

import json
import logging
import time
import uuid
import hmac
import hashlib
import base64
import ipaddress
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from flask import Flask, request, jsonify, Response
import threading
import queue

# GPU Detection
try:
    import torch

    GPU_AVAILABLE = torch.cuda.is_available()
except ImportError:
    GPU_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(message)s")  # JSON per line for audit
logger = logging.getLogger("oPipeBridge")


@dataclass
class BridgeConfig:
    """Bridge configuration with security settings"""

    client_id: str
    hmac_key: str
    api_key: str
    allowlist_ips: List[str]
    mtls_ca: Optional[str] = None
    max_body_size: int = 10 * 1024 * 1024  # 10 MiB
    timeout_seconds: int = 120
    rate_limit_rps: int = 60
    rate_limit_burst: int = 120
    key_ttl_days: int = 30


class HMACAuth:
    """HMAC authentication handler"""

    def __init__(self, config: BridgeConfig):
        self.config = config
        self.active_keys = {
            "v1": {
                "client_id": config.client_id,
                "hmac_key": base64.b64decode(config.hmac_key),
                "api_key": config.api_key,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(days=config.key_ttl_days),
            }
        }

    def verify_request(
        self, headers: Dict[str, str], method: str, path: str, body: bytes
    ) -> Tuple[bool, str]:
        """Verify HMAC signature and authentication"""
        try:
            # Extract headers
            client_id = headers.get("X-Client-Id")
            timestamp = headers.get("X-Timestamp")
            nonce = headers.get("X-Nonce")
            auth_header = headers.get("Authorization", "")
            signature = headers.get("X-Signature")
            key_id = headers.get("X-Key-Id", "v1")

            # Validate required headers
            if not all([client_id, timestamp, nonce, signature]):
                return False, "Missing required headers"

            if not auth_header.startswith("Bearer "):
                return False, "Invalid authorization header"

            api_key = auth_header[7:]  # Remove 'Bearer '

            # Check key ID and get key info
            if key_id not in self.active_keys:
                return False, "Invalid key ID"

            key_info = self.active_keys[key_id]

            # Verify client ID and API key
            if client_id != key_info["client_id"] or api_key != key_info["api_key"]:
                return False, "Authentication failed"

            # Check key expiration
            if datetime.now() > key_info["expires_at"]:
                return False, "Key expired"

            # Verify timestamp (prevent replay attacks)
            try:
                req_time = int(timestamp) / 1000  # Convert ms to seconds
                current_time = time.time()
                if abs(current_time - req_time) > 300:  # 5 minutes tolerance
                    return False, "Request too old"
            except ValueError:
                return False, "Invalid timestamp"

            # Calculate expected signature
            body_hash = hashlib.sha256(body).hexdigest()
            message = f"{method}|{path}|{timestamp}|{nonce}|{body_hash}"
            expected_sig = hmac.new(
                key_info["hmac_key"], message.encode("utf-8"), hashlib.sha256
            ).hexdigest()

            # Verify signature
            if not hmac.compare_digest(signature, expected_sig):
                return False, "Invalid signature"

            return True, "OK"

        except Exception as e:
            logger.error(f"HMAC verification error: {e}")
            return False, "Verification error"


class IPAllowlist:
    """IP allowlist checker"""

    def __init__(self, allowlist_cidrs: List[str]):
        self.allowed_networks = []
        for cidr in allowlist_cidrs:
            try:
                self.allowed_networks.append(ipaddress.ip_network(cidr, strict=False))
            except ValueError as e:
                logger.error(f"Invalid CIDR {cidr}: {e}")

    def is_allowed(self, ip: str) -> bool:
        """Check if IP is in allowlist"""
        try:
            client_ip = ipaddress.ip_address(ip)
            return any(client_ip in network for network in self.allowed_networks)
        except ValueError:
            return False


class RateLimiter:
    """Rate limiter with burst support"""

    def __init__(self, rps: int, burst: int):
        self.rps = rps
        self.burst = burst
        self.requests = {}  # client_id -> [timestamps]
        self.lock = threading.Lock()

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()

        with self.lock:
            if client_id not in self.requests:
                self.requests[client_id] = []

            # Clean old requests
            cutoff = current_time - 1.0  # Last second
            self.requests[client_id] = [
                t for t in self.requests[client_id] if t > cutoff
            ]

            # Check burst limit
            if len(self.requests[client_id]) >= self.burst:
                return False

            # Check RPS limit
            if len(self.requests[client_id]) >= self.rps:
                return False

            # Add current request
            self.requests[client_id].append(current_time)
            return True


class OPipeBridge:
    """Main bridge class handling requests to str.py"""

    def __init__(self, config: BridgeConfig):
        self.config = config
        self.auth = HMACAuth(config)
        self.allowlist = IPAllowlist(config.allowlist_ips)
        self.rate_limiter = RateLimiter(config.rate_limit_rps, config.rate_limit_burst)
        self.app = Flask(__name__)
        self._setup_routes()

        # GPU status
        self.gpu_status = self._check_gpu_status()

    def _check_gpu_status(self) -> Dict[str, Any]:
        """Check GPU availability and status"""
        gpu_info = {"cuda_available": GPU_AVAILABLE, "devices": []}

        if GPU_AVAILABLE:
            try:
                device_count = torch.cuda.device_count()
                for i in range(device_count):
                    device_info = {
                        "name": torch.cuda.get_device_name(i),
                        "memory_total": torch.cuda.get_device_properties(i).total_memory
                        // (1024**3),
                        "memory_free": torch.cuda.memory_reserved(i) // (1024**3),
                    }
                    gpu_info["devices"].append(device_info)
            except Exception as e:
                logger.error(f"GPU status check error: {e}")

        return gpu_info

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.before_request
        def before_request():
            """Security middleware"""
            # Get client IP
            client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            if "," in client_ip:
                client_ip = client_ip.split(",")[0].strip()

            # Check IP allowlist
            if not self.allowlist.is_allowed(client_ip):
                return (
                    jsonify(
                        {
                            "ok": False,
                            "code": "BRIDGE_NOT_ALLOWED",
                            "msg": "IP not in allowlist",
                            "trace": {"rid": str(uuid.uuid4())},
                        }
                    ),
                    403,
                )

            # Check rate limits
            client_id = request.headers.get("X-Client-Id", "unknown")
            if not self.rate_limiter.is_allowed(client_id):
                return (
                    jsonify(
                        {
                            "ok": False,
                            "code": "BRIDGE_BUSY",
                            "msg": "Rate limit exceeded",
                            "trace": {"rid": str(uuid.uuid4())},
                        }
                    ),
                    429,
                )

            # Verify HMAC authentication
            body = request.get_data()
            verified, msg = self.auth.verify_request(
                dict(request.headers), request.method, request.path, body
            )

            if not verified:
                return (
                    jsonify(
                        {
                            "ok": False,
                            "code": "BRIDGE_AUTH_FAILED",
                            "msg": msg,
                            "trace": {"rid": str(uuid.uuid4())},
                        }
                    ),
                    401,
                )

            # Check body size
            if len(body) > self.config.max_body_size:
                return (
                    jsonify(
                        {
                            "ok": False,
                            "code": "BRIDGE_INVALID_PAYLOAD",
                            "msg": "Payload too large",
                            "trace": {"rid": str(uuid.uuid4())},
                        }
                    ),
                    400,
                )

        @self.app.route("/_bridge/v1/route", methods=["POST"])
        def route_request():
            """Main routing endpoint"""
            request_id = str(uuid.uuid4())
            start_time = time.time()

            try:
                data = request.get_json()
                if not data:
                    return (
                        jsonify(
                            {
                                "ok": False,
                                "code": "BRIDGE_INVALID_PAYLOAD",
                                "msg": "Invalid JSON",
                                "trace": {"rid": request_id},
                            }
                        ),
                        400,
                    )

                path = data.get("path")
                payload = data.get("payload", {})
                prefs = data.get("prefs", {})

                # Validate path
                valid_paths = [
                    "/v1/chat/completions",
                    "/v1/embeddings",
                    "/v1/completions",
                ]
                if path not in valid_paths:
                    return (
                        jsonify(
                            {
                                "ok": False,
                                "code": "BRIDGE_MODEL_UNSUPPORTED",
                                "msg": f"Unsupported path: {path}",
                                "trace": {"rid": request_id},
                            }
                        ),
                        422,
                    )

                # Process request through str.py interface
                result = self._process_request(path, payload, prefs)

                # Calculate latency
                latency_ms = int((time.time() - start_time) * 1000)

                # Audit log
                self._audit_log(request_id, "route", path, latency_ms, result)

                return jsonify(
                    {
                        "ok": True,
                        "data": result,
                        "trace": {
                            "lat_ms": latency_ms,
                            "model": payload.get("model", "unknown"),
                        },
                    }
                )

            except Exception as e:
                latency_ms = int((time.time() - start_time) * 1000)
                logger.error(f"Route error [{request_id}]: {e}")

                return (
                    jsonify(
                        {
                            "ok": False,
                            "code": "BRIDGE_BACKEND_ERROR",
                            "msg": "Internal error",
                            "trace": {"rid": request_id},
                        }
                    ),
                    500,
                )

        @self.app.route("/_bridge/v1/healthz", methods=["GET"])
        def health_check():
            """Health check endpoint"""
            request_id = str(uuid.uuid4())

            return jsonify(
                {
                    "ok": True,
                    "cuda": self.gpu_status["cuda_available"],
                    "gpus": self.gpu_status["devices"],
                }
            )

        @self.app.route("/_bridge/v1/models", methods=["GET"])
        def list_models():
            """List available models"""
            request_id = str(uuid.uuid4())

            models = [
                {
                    "id": "qwen2.5-7b-instruct",
                    "dtype": "auto",
                    "device": "cuda" if self.gpu_status["cuda_available"] else "cpu",
                },
                {
                    "id": "qwen2.5-14b-instruct",
                    "dtype": "auto",
                    "device": "cuda" if self.gpu_status["cuda_available"] else "cpu",
                },
            ]

            return jsonify({"data": models})

        @self.app.route("/_bridge/v1/encode", methods=["POST"])
        def encode_payload():
            """Encode object to JSON string"""
            request_id = str(uuid.uuid4())

            try:
                data = request.get_json()
                if not data or "txt" not in data:
                    return (
                        jsonify(
                            {
                                "ok": False,
                                "code": "BRIDGE_INVALID_PAYLOAD",
                                "msg": "Missing txt field",
                                "trace": {"rid": request_id},
                            }
                        ),
                        400,
                    )

                # Strict JSON encoding
                json_str = json.dumps(
                    data["txt"], ensure_ascii=False, separators=(",", ":")
                )

                return jsonify({"ok": True, "json": json_str})

            except Exception as e:
                return (
                    jsonify(
                        {
                            "ok": False,
                            "code": "BRIDGE_BACKEND_ERROR",
                            "msg": "Encoding error",
                            "trace": {"rid": request_id},
                        }
                    ),
                    500,
                )

        @self.app.route("/_bridge/v1/decode", methods=["POST"])
        def decode_payload():
            """Decode JSON string to object"""
            request_id = str(uuid.uuid4())

            try:
                data = request.get_json()
                if not data or "json" not in data:
                    return (
                        jsonify(
                            {
                                "ok": False,
                                "code": "BRIDGE_INVALID_PAYLOAD",
                                "msg": "Missing json field",
                                "trace": {"rid": request_id},
                            }
                        ),
                        400,
                    )

                # Strict JSON decoding
                obj = json.loads(data["json"])

                return jsonify({"ok": True, "obj": obj})

            except Exception as e:
                return (
                    jsonify(
                        {
                            "ok": False,
                            "code": "BRIDGE_INVALID_PAYLOAD",
                            "msg": "Invalid JSON",
                            "trace": {"rid": request_id},
                        }
                    ),
                    400,
                )

    def _process_request(
        self, path: str, payload: Dict[str, Any], prefs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process request through str.py interface"""
        # This is where we would interface with str.py
        # For now, return a mock response based on the path

        if path == "/v1/chat/completions":
            return self._handle_chat_completions(payload, prefs)
        elif path == "/v1/embeddings":
            return self._handle_embeddings(payload, prefs)
        elif path == "/v1/completions":
            return self._handle_completions(payload, prefs)
        else:
            raise ValueError(f"Unsupported path: {path}")

    def _handle_chat_completions(
        self, payload: Dict[str, Any], prefs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle chat completions request"""
        model = payload.get("model", "qwen2.5-7b-instruct")
        messages = payload.get("messages", [])
        temperature = payload.get("temperature", 0.0)
        max_tokens = payload.get("max_tokens", 1024)
        stream = payload.get("stream", False)

        # Use GPU if available and requested
        use_gpu = prefs.get("gpu", True) and self.gpu_status["cuda_available"]

        # Mock response - in real implementation, this would call str.py
        response = {
            "id": f"chatcmpl-{uuid.uuid4().hex[:29]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Mock response from {model} (GPU: {use_gpu})",
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
        }

        return response

    def _handle_embeddings(
        self, payload: Dict[str, Any], prefs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle embeddings request"""
        model = payload.get("model", "qwen2.5-7b-instruct")
        input_text = payload.get("input", "")

        # Mock response
        response = {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "index": 0,
                    "embedding": [0.1] * 1024,  # Mock 1024-dim embedding
                }
            ],
            "model": model,
            "usage": {
                "prompt_tokens": len(input_text.split()),
                "total_tokens": len(input_text.split()),
            },
        }

        return response

    def _handle_completions(
        self, payload: Dict[str, Any], prefs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle completions request"""
        model = payload.get("model", "qwen2.5-7b-instruct")
        prompt = payload.get("prompt", "")
        max_tokens = payload.get("max_tokens", 1024)

        # Mock response
        response = {
            "id": f"cmpl-{uuid.uuid4().hex[:29]}",
            "object": "text_completion",
            "created": int(time.time()),
            "model": model,
            "choices": [
                {
                    "text": f"Mock completion for: {prompt[:50]}...",
                    "index": 0,
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": 20,
                "total_tokens": len(prompt.split()) + 20,
            },
        }

        return response

    def _audit_log(
        self,
        request_id: str,
        operation: str,
        path: str,
        latency_ms: int,
        result: Dict[str, Any],
    ):
        """Log audit information"""
        client_id = request.headers.get("X-Client-Id", "unknown")
        client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)

        # Calculate token usage
        tokens_in = 0
        tokens_out = 0
        if "usage" in result:
            tokens_in = result["usage"].get("prompt_tokens", 0)
            tokens_out = result["usage"].get("completion_tokens", 0)

        # Body hash (without logging full body)
        body_hash = hashlib.sha256(request.get_data()).hexdigest()

        audit_entry = {
            "time": datetime.now().isoformat(),
            "rid": request_id,
            "client_id": client_id,
            "ip": client_ip,
            "path": path,
            "model": result.get("model", "unknown"),
            "lat_ms": latency_ms,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "gpu": self.gpu_status["cuda_available"],
            "rc": "200",
            "body_sha256": body_hash,
        }

        logger.info(json.dumps(audit_entry))

    def run(self, host: str = "127.0.0.1", port: int = 8080, debug: bool = False):
        """Run the bridge server"""
        logger.info(f"Starting @oPipe® Bridge on {host}:{port}")
        logger.info(f"GPU Available: {self.gpu_status['cuda_available']}")
        if self.gpu_status["cuda_available"]:
            logger.info(f"GPU Devices: {len(self.gpu_status['devices'])}")

        self.app.run(host=host, port=port, debug=debug, threaded=True)


# Example configuration
def create_bridge_config() -> BridgeConfig:
    """Create bridge configuration with example values"""
    return BridgeConfig(
        client_id="OGPT_BRIDGE_ID",
        hmac_key="OGPT_BRIDGE_HMAC_BASE64",  # Base64 encoded HMAC key
        api_key="OGPT_BRIDGE_APIKEY",
        allowlist_ips=["127.0.0.1/32", "10.0.0.0/8"],  # Example CIDR list
        mtls_ca=None,  # Optional mTLS CA
        max_body_size=10 * 1024 * 1024,  # 10 MiB
        timeout_seconds=120,
        rate_limit_rps=60,
        rate_limit_burst=120,
        key_ttl_days=30,
    )


if __name__ == "__main__":
    # Create and run bridge
    config = create_bridge_config()
    bridge = OPipeBridge(config)

    print("@oPipe® Bridge - Zero-Trust Gateway")
    print("=" * 50)
    print(f"GPU Available: {bridge.gpu_status['cuda_available']}")
    print(f"Allowed IPs: {config.allowlist_ips}")
    print(f"Rate Limit: {config.rate_limit_rps} RPS, {config.rate_limit_burst} burst")
    print("=" * 50)

    bridge.run(host="127.0.0.1", port=8080, debug=False)
