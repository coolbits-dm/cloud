#!/usr/bin/env python3
"""
Multi-Agent Guard System for CoolBits.ai
Prevents ADK Custom Agent issues: infinite loops, tool budget exceeded, intermediate output
"""

from .multi_agent_guard import MultiAgentGuard, get_guard, AgentState
from .decorators import (
    guard_tool_call,
    guard_subagent, 
    ensure_final_output,
    with_barrier
)
from .config import (
    GuardConfig,
    DEFAULT_CONFIG,
    PRODUCTION_CONFIG,
    DEVELOPMENT_CONFIG,
    get_config,
    get_current_config
)

__version__ = "1.0.0"
__author__ = "CoolBits.ai Team"

__all__ = [
    "MultiAgentGuard",
    "get_guard", 
    "AgentState",
    "guard_tool_call",
    "guard_subagent",
    "ensure_final_output", 
    "with_barrier",
    "GuardConfig",
    "DEFAULT_CONFIG",
    "PRODUCTION_CONFIG", 
    "DEVELOPMENT_CONFIG",
    "get_config",
    "get_current_config"
]
