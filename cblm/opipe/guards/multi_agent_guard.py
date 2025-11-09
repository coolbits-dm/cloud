#!/usr/bin/env python3
"""
Multi-Agent Guard System for ADK Custom Agents
Prevents infinite loops, tool budget exceeded, and intermediate output issues
"""

import time
import hashlib
import asyncio
from typing import Dict, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class AgentState(Enum):
    IDLE = "idle"
    ROUTING = "routing"
    RUNNING_TOOLS = "running_tools"
    JOIN = "join"
    FINAL = "final"


@dataclass
class ToolCall:
    tool_name: str
    params: Dict[str, Any]
    parent_id: str
    timestamp: float
    call_hash: str


class MultiAgentGuard:
    """Guard system for multi-agent operations"""

    def __init__(
        self,
        max_calls: int = 8,
        ttl_s: int = 60,
        max_depth: int = 3,
        max_iterations: int = 10,
    ):
        self.calls: Dict[str, Tuple[int, float]] = {}
        self.ttl = ttl_s
        self.max_calls = max_calls
        self.max_depth = max_depth
        self.max_iterations = max_iterations

        # Circuit breaker
        self.circuit_breaker: Dict[str, Dict[str, Any]] = {}

        # Deduplication
        self.recent_calls: Dict[str, float] = {}
        self.dedup_window = 5  # seconds

        # State management
        self.state = AgentState.IDLE
        self.current_depth = 0
        self.current_iterations = 0

    def _generate_call_hash(
        self, prompt: str, params: Dict[str, Any], parent_id: str
    ) -> str:
        """Generate unique hash for call deduplication"""
        content = f"{prompt}:{str(sorted(params.items()))}:{parent_id}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def allow_tool_call(
        self,
        tool_name: str,
        prompt: str = "",
        params: Dict[str, Any] = None,
        parent_id: str = "",
    ) -> bool:
        """Check if tool call is allowed (budget + deduplication)"""
        if params is None:
            params = {}

        # Check circuit breaker
        if self._is_circuit_open(tool_name):
            return False

        # Check budget
        if not self._check_budget(tool_name):
            return False

        # Check deduplication
        call_hash = self._generate_call_hash(prompt, params, parent_id)
        if self._is_duplicate_call(call_hash):
            return False

        # Check max iterations
        if self.current_iterations >= self.max_iterations:
            return False

        # Record call
        self.calls[tool_name] = (
            self.calls.get(tool_name, (0, time.time()))[0] + 1,
            time.time(),
        )
        self.recent_calls[call_hash] = time.time()
        self.current_iterations += 1

        return True

    def _check_budget(self, tool_name: str) -> bool:
        """Check if tool is within budget"""
        now = time.time()
        count, last_reset = self.calls.get(tool_name, (0, now))

        # Reset if TTL expired
        if now - last_reset > self.ttl:
            count = 0
            last_reset = now

        # Check if within budget
        if count >= self.max_calls:
            return False

        self.calls[tool_name] = (count, last_reset)
        return True

    def _is_duplicate_call(self, call_hash: str) -> bool:
        """Check if call is duplicate within dedup window"""
        now = time.time()

        # Clean old entries
        self.recent_calls = {
            h: t for h, t in self.recent_calls.items() if now - t < self.dedup_window
        }

        return call_hash in self.recent_calls

    def _is_circuit_open(self, tool_name: str) -> bool:
        """Check if circuit breaker is open for tool"""
        if tool_name not in self.circuit_breaker:
            return False

        cb = self.circuit_breaker[tool_name]
        now = time.time()

        # Reset if timeout expired
        if now - cb.get("last_failure", 0) > 30:  # 30s timeout
            cb["failures"] = 0
            cb["timeouts"] = 0

        # Open circuit if too many failures
        return cb.get("failures", 0) >= 3 or cb.get("timeouts", 0) >= 2

    def record_tool_failure(self, tool_name: str, is_timeout: bool = False):
        """Record tool failure for circuit breaker"""
        if tool_name not in self.circuit_breaker:
            self.circuit_breaker[tool_name] = {
                "failures": 0,
                "timeouts": 0,
                "last_failure": 0,
            }

        cb = self.circuit_breaker[tool_name]
        cb["last_failure"] = time.time()

        if is_timeout:
            cb["timeouts"] += 1
        else:
            cb["failures"] += 1

    def set_state(self, state: AgentState):
        """Set agent state"""
        self.state = state

        if state == AgentState.FINAL:
            # Reset counters for next conversation
            self.current_depth = 0
            self.current_iterations = 0

    def can_send_output(self) -> bool:
        """Check if output can be sent (only in FINAL state)"""
        return self.state == AgentState.FINAL

    def increment_depth(self) -> bool:
        """Increment depth and check if within limits"""
        self.current_depth += 1
        return self.current_depth <= self.max_depth

    async def run_subagents_with_barrier(
        self, tasks: list, timeout: float = 30
    ) -> list:
        """Run subagents with barrier and timeout"""
        self.set_state(AgentState.JOIN)

        try:
            results = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True), timeout=timeout
            )
            return results
        except asyncio.TimeoutError:
            # Record timeout for circuit breaker
            for task in tasks:
                if hasattr(task, "tool_name"):
                    self.record_tool_failure(task.tool_name, is_timeout=True)
            raise
        finally:
            self.set_state(AgentState.FINAL)


# Global guard instance
guard = MultiAgentGuard()


def get_guard() -> MultiAgentGuard:
    """Get global guard instance"""
    return guard


# Usage examples:
"""
# In your agent code:
guard = get_guard()

# Before tool call:
if not guard.allow_tool_call("search", prompt, params, parent_id):
    return "tool_budget_exceeded"

# Before subagent call:
if not guard.increment_depth():
    return "max_depth_exceeded"

# Run subagents with barrier:
results = await guard.run_subagents_with_barrier([
    subagent1.run(),
    subagent2.run(),
    subagent3.run()
], timeout=30)

# Check if can send output:
if guard.can_send_output():
    return final_result
else:
    return "intermediate_result"
"""
