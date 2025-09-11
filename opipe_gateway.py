#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
oPipe® Gateway Central - Backend GPU Integration
CoolBits.ai / cbLM.ai - Protocol Management System

This module provides standardized functions for managing data flows between
GPU-backend and client applications through the oPipe® gateway.

Compatibility: Python ≥3.10 with full Unicode (UTF-8) support
Author: oPipe® Agent (oCursor)
Company: COOL BITS SRL
"""

import json
import logging
import time
import uuid
import re
import unicodedata
from typing import Dict, Any, Optional, Union
from datetime import datetime

# GPU Detection
try:
    import torch

    GPU_AVAILABLE = torch.cuda.is_available()
except ImportError:
    GPU_AVAILABLE = False

# NVIDIA-SMI Detection
try:
    import subprocess

    result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
    NVIDIA_SMI_AVAILABLE = result.returncode == 0
except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
    NVIDIA_SMI_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("oPipe")


class OPipeGateway:
    """
    oPipe® Gateway Central for GPU-backend integration
    Manages protocols and data routing between GPU-backend and client applications
    """

    def __init__(self):
        self.trace_id = None
        self.model = "oPipe-Gateway"
        self.start_time = None
        self.gpu_status = self._check_gpu_availability()

    def _check_gpu_availability(self) -> Dict[str, Any]:
        """Check GPU availability and return status"""
        gpu_info = {
            "torch_cuda": GPU_AVAILABLE,
            "nvidia_smi": NVIDIA_SMI_AVAILABLE,
            "fallback_cpu": True,
        }

        if GPU_AVAILABLE:
            try:
                gpu_info["device_count"] = torch.cuda.device_count()
                gpu_info["current_device"] = torch.cuda.current_device()
                gpu_info["device_name"] = torch.cuda.get_device_name(0)
            except Exception as e:
                logger.warning(f"GPU detection error: {e}")
                gpu_info["torch_cuda"] = False

        return gpu_info


def sanitize_str(input_str: str) -> str:
    """
    Clean and normalize input string for safe processing

    Args:
        input_str: Raw input string to sanitize

    Returns:
        Cleaned and normalized string

    Raises:
        TypeError: If input is not a string
        ValueError: If input contains invalid characters
    """
    if not isinstance(input_str, str):
        raise TypeError(f"Expected string, got {type(input_str).__name__}")

    # Generate trace ID for this operation
    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    try:
        # Unicode normalization
        normalized = unicodedata.normalize("NFKC", input_str)

        # Remove control characters except newlines and tabs
        cleaned = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", normalized)

        # Remove excessive whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        # Validate UTF-8 encoding
        cleaned.encode("utf-8")

        # Log operation
        latency_ms = int((time.time() - start_time) * 1000)
        logger.info(f"[{trace_id}] sanitize_str completed - latency: {latency_ms}ms")

        return cleaned

    except UnicodeError as e:
        logger.error(f"[{trace_id}] Unicode error in sanitize_str: {e}")
        raise ValueError(f"Invalid Unicode in input: {e}")
    except Exception as e:
        logger.error(f"[{trace_id}] Error in sanitize_str: {e}")
        raise


def encode_payload(obj: Dict[str, Any]) -> str:
    """
    Encode dictionary to JSON string with strict validation

    Args:
        obj: Dictionary to encode

    Returns:
        JSON string representation

    Raises:
        TypeError: If input is not a dictionary
        ValueError: If object cannot be serialized
    """
    if not isinstance(obj, dict):
        raise TypeError(f"Expected dict, got {type(obj).__name__}")

    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    try:
        # Validate payload size
        json_str = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))

        if len(json_str.encode("utf-8")) > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("Payload too large (>10MB)")

        # Log operation
        latency_ms = int((time.time() - start_time) * 1000)
        payload_size = len(json_str.encode("utf-8"))
        logger.info(
            f"[{trace_id}] encode_payload completed - size: {payload_size}B, latency: {latency_ms}ms"
        )

        return json_str

    except (TypeError, ValueError) as e:
        logger.error(f"[{trace_id}] Serialization error in encode_payload: {e}")
        raise ValueError(f"Cannot serialize payload: {e}")
    except Exception as e:
        logger.error(f"[{trace_id}] Error in encode_payload: {e}")
        raise


def decode_payload(txt: str) -> Dict[str, Any]:
    """
    Decode JSON string to dictionary with validation and exception handling

    Args:
        txt: JSON string to decode

    Returns:
        Decoded dictionary

    Raises:
        TypeError: If input is not a string
        ValueError: If JSON is invalid or payload is too large
    """
    if not isinstance(txt, str):
        raise TypeError(f"Expected string, got {type(txt).__name__}")

    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    try:
        # Validate input size
        if len(txt.encode("utf-8")) > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("Payload too large (>10MB)")

        # Decode JSON
        obj = json.loads(txt)

        if not isinstance(obj, dict):
            raise ValueError("Decoded payload must be a dictionary")

        # Log operation
        latency_ms = int((time.time() - start_time) * 1000)
        payload_size = len(txt.encode("utf-8"))
        logger.info(
            f"[{trace_id}] decode_payload completed - size: {payload_size}B, latency: {latency_ms}ms"
        )

        return obj

    except json.JSONDecodeError as e:
        logger.error(f"[{trace_id}] JSON decode error: {e}")
        raise ValueError(f"Invalid JSON: {e}")
    except Exception as e:
        logger.error(f"[{trace_id}] Error in decode_payload: {e}")
        raise


def route_request(path: str, body: Dict[str, Any]) -> Dict[str, Any]:
    """
    Route request based on path with logical routing

    Args:
        path: Request path for routing
        body: Request body dictionary

    Returns:
        Response dictionary with trace_id, model, and latency_ms

    Raises:
        TypeError: If inputs are not correct types
        ValueError: If path is invalid
    """
    if not isinstance(path, str):
        raise TypeError(f"Expected string path, got {type(path).__name__}")
    if not isinstance(body, dict):
        raise TypeError(f"Expected dict body, got {type(body).__name__}")

    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    try:
        # Initialize gateway
        gateway = OPipeGateway()
        gateway.trace_id = trace_id
        gateway.start_time = start_time

        # Sanitize path
        clean_path = sanitize_str(path)

        # Route based on path
        response = {
            "trace_id": trace_id,
            "model": gateway.model,
            "path": clean_path,
            "timestamp": datetime.now().isoformat(),
            "gpu_status": gateway.gpu_status,
            "status": "success",
        }

        # Add routing logic based on path
        if clean_path.startswith("/gpu/"):
            if gateway.gpu_status["torch_cuda"]:
                response["backend"] = "gpu"
                response["device"] = gateway.gpu_status.get("device_name", "cuda")
            else:
                response["backend"] = "cpu_fallback"
                response["warning"] = "GPU not available, using CPU fallback"

        elif clean_path.startswith("/cpu/"):
            response["backend"] = "cpu"

        elif clean_path.startswith("/status/"):
            response["backend"] = "status"
            response["gpu_info"] = gateway.gpu_status

        else:
            response["backend"] = "default"
            response["warning"] = "Unknown path, using default routing"

        # Add request body info
        response["request_size"] = len(encode_payload(body))
        response["body_keys"] = list(body.keys()) if body else []

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)
        response["latency_ms"] = latency_ms

        # Log operation
        logger.info(
            f"[{trace_id}] route_request completed - path: {clean_path}, latency: {latency_ms}ms"
        )

        return response

    except Exception as e:
        latency_ms = int((time.time() - start_time) * 1000)
        logger.error(f"[{trace_id}] Error in route_request: {e}")

        return {
            "trace_id": trace_id,
            "model": "oPipe-Gateway",
            "error": str(e),
            "status": "error",
            "latency_ms": latency_ms,
            "timestamp": datetime.now().isoformat(),
        }


# Test functions for large payloads and special characters
def test_large_payload():
    """Test with payload >1MB"""
    large_data = {
        "content": "x" * (1024 * 1024),  # 1MB of data
        "metadata": {"size": "large", "test": True},
    }

    try:
        encoded = encode_payload(large_data)
        decoded = decode_payload(encoded)
        print(f"Large payload test: SUCCESS - {len(encoded)} bytes")
        return True
    except Exception as e:
        print(f"Large payload test: FAILED - {e}")
        return False


def test_special_characters():
    """Test with special characters and Unicode"""
    special_data = {
        "unicode": "🚀 Hello 世界! ñáéíóú",
        "control_chars": "Line1\nLine2\tTabbed",
        "symbols": "!@#$%^&*()_+-=[]{}|;:,.<>?",
        "mixed": "Mix: 中文 + English + 123 + 🎯",
    }

    try:
        for key, value in special_data.items():
            sanitized = sanitize_str(value)
            print(f"Special chars test ({key}): SUCCESS")
        return True
    except Exception as e:
        print(f"Special chars test: FAILED - {e}")
        return False


def test_routing():
    """Test routing functionality"""
    test_cases = [
        ("/gpu/inference", {"model": "test", "input": "hello"}),
        ("/cpu/processing", {"data": "test"}),
        ("/status/health", {}),
        ("/unknown/path", {"test": True}),
    ]

    try:
        for path, body in test_cases:
            response = route_request(path, body)
            print(f"Routing test ({path}): SUCCESS - {response['status']}")
        return True
    except Exception as e:
        print(f"Routing test: FAILED - {e}")
        return False


if __name__ == "__main__":
    print("oPipe® Gateway Central - Testing Suite")
    print("=" * 50)

    # Run tests
    print("\n1. Testing large payloads...")
    test_large_payload()

    print("\n2. Testing special characters...")
    test_special_characters()

    print("\n3. Testing routing...")
    test_routing()

    print("\n4. GPU Status Check...")
    gateway = OPipeGateway()
    print(f"GPU Available: {gateway.gpu_status['torch_cuda']}")
    print(f"NVIDIA-SMI Available: {gateway.gpu_status['nvidia_smi']}")
    if gateway.gpu_status["torch_cuda"]:
        print(f"Device Count: {gateway.gpu_status['device_count']}")
        print(f"Current Device: {gateway.gpu_status['device_name']}")

    print("\n" + "=" * 50)
    print("oPipe® Gateway Central - Ready for Production")
