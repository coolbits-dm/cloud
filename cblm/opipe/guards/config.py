#!/usr/bin/env python3
"""
Configuration for Multi-Agent Guard System
Centralized settings for all guard parameters
"""

from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class GuardConfig:
    """Configuration for multi-agent guards"""
    
    # Tool budget settings
    max_calls_per_tool: int = 8
    tool_ttl_seconds: int = 60
    
    # Depth and iteration limits
    max_depth: int = 3
    max_iterations: int = 10
    
    # Circuit breaker settings
    max_failures: int = 3
    max_timeouts: int = 2
    circuit_timeout_seconds: int = 30
    
    # Deduplication settings
    dedup_window_seconds: int = 5
    
    # Barrier settings
    subagent_timeout_seconds: float = 30.0
    
    # Tool-specific overrides
    tool_overrides: Dict[str, Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.tool_overrides is None:
            self.tool_overrides = {
                "search": {"max_calls": 5, "ttl": 30},
                "code_generation": {"max_calls": 3, "ttl": 120},
                "file_operations": {"max_calls": 10, "ttl": 60},
                "api_calls": {"max_calls": 15, "ttl": 30},
            }

# Default configuration
DEFAULT_CONFIG = GuardConfig()

# Production configuration (stricter)
PRODUCTION_CONFIG = GuardConfig(
    max_calls_per_tool=5,
    tool_ttl_seconds=30,
    max_depth=2,
    max_iterations=5,
    max_failures=2,
    max_timeouts=1,
    circuit_timeout_seconds=15,
    dedup_window_seconds=3,
    subagent_timeout_seconds=20.0,
    tool_overrides={
        "search": {"max_calls": 3, "ttl": 15},
        "code_generation": {"max_calls": 2, "ttl": 60},
        "file_operations": {"max_calls": 5, "ttl": 30},
        "api_calls": {"max_calls": 8, "ttl": 15},
    }
)

# Development configuration (more permissive)
DEVELOPMENT_CONFIG = GuardConfig(
    max_calls_per_tool=15,
    tool_ttl_seconds=120,
    max_depth=5,
    max_iterations=20,
    max_failures=5,
    max_timeouts=3,
    circuit_timeout_seconds=60,
    dedup_window_seconds=10,
    subagent_timeout_seconds=60.0,
    tool_overrides={
        "search": {"max_calls": 10, "ttl": 60},
        "code_generation": {"max_calls": 5, "ttl": 180},
        "file_operations": {"max_calls": 20, "ttl": 120},
        "api_calls": {"max_calls": 25, "ttl": 60},
    }
)

def get_config(environment: str = "development") -> GuardConfig:
    """Get configuration for environment"""
    configs = {
        "development": DEVELOPMENT_CONFIG,
        "staging": PRODUCTION_CONFIG,
        "production": PRODUCTION_CONFIG,
    }
    return configs.get(environment, DEFAULT_CONFIG)

# Environment detection
import os
def get_current_config() -> GuardConfig:
    """Get configuration based on current environment"""
    env = os.getenv("CB_ENVIRONMENT", "development")
    return get_config(env)
