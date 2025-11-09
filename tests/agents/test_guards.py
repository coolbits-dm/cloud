#!/usr/bin/env python3
"""
Tests for Multi-Agent Guard System
Anti-ADK loop prevention tests
"""

import pytest
import asyncio
import time
from unittest.mock import patch
from cblm.opipe.guards import (
    MultiAgentGuard,
    get_guard,
    AgentState,
    guard_tool_call,
    ensure_final_output,
)


class TestToolBudget:
    """Test tool budget limits"""

    def test_tool_budget(self):
        """Test max 8 calls/tool in 60s"""
        guard = MultiAgentGuard(max_calls=8, ttl_s=60)

        # Should allow 8 calls with different prompts to avoid deduplication
        for i in range(8):
            assert guard.allow_tool_call("test_tool", f"test_{i}", {}, "parent")

        # 9th call should be blocked
        assert not guard.allow_tool_call("test_tool", "test_9", {}, "parent")

        # Different tool should still work
        assert guard.allow_tool_call("other_tool", "test", {}, "parent")

    def test_tool_ttl_reset(self):
        """Test TTL reset after 60s"""
        guard = MultiAgentGuard(max_calls=2, ttl_s=1)  # 1 second TTL for testing

        # Use up budget with different prompts
        assert guard.allow_tool_call("test_tool", "test1", {}, "parent")
        assert guard.allow_tool_call("test_tool", "test2", {}, "parent")
        assert not guard.allow_tool_call("test_tool", "test3", {}, "parent")

        # Wait for TTL reset
        time.sleep(1.1)

        # Should work again
        assert guard.allow_tool_call("test_tool", "test4", {}, "parent")


class TestDeduplication:
    """Test call deduplication"""

    def test_dedup_5s_window(self):
        """Test 5s deduplication window"""
        guard = MultiAgentGuard()
        guard.dedup_window = 5  # Set dedup window

        # First call should work
        assert guard.allow_tool_call(
            "test_tool", "same_prompt", {"param": "value"}, "parent"
        )

        # Identical call should be blocked
        assert not guard.allow_tool_call(
            "test_tool", "same_prompt", {"param": "value"}, "parent"
        )

        # Different prompt should work
        assert guard.allow_tool_call(
            "test_tool", "different_prompt", {"param": "value"}, "parent"
        )

    def test_dedup_window_expiry(self):
        """Test deduplication window expiry"""
        guard = MultiAgentGuard()
        guard.dedup_window = 1  # 1 second for testing

        # First call
        assert guard.allow_tool_call("test_tool", "same_prompt", {}, "parent")

        # Should be blocked immediately
        assert not guard.allow_tool_call("test_tool", "same_prompt", {}, "parent")

        # Wait for window to expire
        time.sleep(1.1)

        # Should work again
        assert guard.allow_tool_call("test_tool", "same_prompt", {}, "parent")


class TestParallelBarrier:
    """Test parallel execution with barrier"""

    @pytest.mark.asyncio
    async def test_parallel_barrier_timeout(self):
        """Test 30s timeout on parallel gather"""
        guard = MultiAgentGuard()

        async def slow_task():
            await asyncio.sleep(35)  # Longer than timeout
            return "slow_result"

        async def fast_task():
            await asyncio.sleep(1)
            return "fast_result"

        # Should timeout and raise TimeoutError
        with pytest.raises(asyncio.TimeoutError):
            await guard.run_subagents_with_barrier(
                [slow_task(), fast_task()], timeout=30
            )

    @pytest.mark.asyncio
    async def test_parallel_barrier_success(self):
        """Test successful parallel execution"""
        guard = MultiAgentGuard()

        async def task1():
            await asyncio.sleep(0.1)
            return "result1"

        async def task2():
            await asyncio.sleep(0.1)
            return "result2"

        results = await guard.run_subagents_with_barrier([task1(), task2()], timeout=30)
        assert results == ["result1", "result2"]


class TestCircuitBreaker:
    """Test circuit breaker functionality"""

    def test_circuit_breaker_failures(self):
        """Test circuit opens after 3 failures"""
        guard = MultiAgentGuard()

        # Record 3 failures
        guard.record_tool_failure("test_tool", is_timeout=False)
        guard.record_tool_failure("test_tool", is_timeout=False)
        guard.record_tool_failure("test_tool", is_timeout=False)

        # Should be blocked
        assert not guard.allow_tool_call("test_tool", "test", {}, "parent")

        # Other tools should still work
        assert guard.allow_tool_call("other_tool", "test", {}, "parent")

    def test_circuit_breaker_timeouts(self):
        """Test circuit opens after 2 timeouts"""
        guard = MultiAgentGuard()

        # Record 2 timeouts
        guard.record_tool_failure("test_tool", is_timeout=True)
        guard.record_tool_failure("test_tool", is_timeout=True)

        # Should be blocked
        assert not guard.allow_tool_call("test_tool", "test", {}, "parent")


class TestStateMachine:
    """Test state machine functionality"""

    def test_state_transitions(self):
        """Test state machine transitions"""
        guard = MultiAgentGuard()

        # Start in IDLE
        assert guard.state == AgentState.IDLE

        # Can't send output in IDLE
        assert not guard.can_send_output()

        # Transition to FINAL
        guard.set_state(AgentState.FINAL)
        assert guard.state == AgentState.FINAL

        # Can send output in FINAL
        assert guard.can_send_output()

    def test_depth_limits(self):
        """Test max depth limits"""
        guard = MultiAgentGuard(max_depth=3)

        # Should allow 3 depth increments
        assert guard.increment_depth()  # depth 1
        assert guard.increment_depth()  # depth 2
        assert guard.increment_depth()  # depth 3

        # 4th increment should fail
        assert not guard.increment_depth()  # depth 4 (exceeds max)


class TestDecorators:
    """Test guard decorators"""

    @pytest.mark.asyncio
    async def test_guard_tool_call_decorator(self):
        """Test @guard_tool_call decorator"""

        # Create a fresh guard for this test
        from cblm.opipe.guards.multi_agent_guard import MultiAgentGuard

        test_guard = MultiAgentGuard(max_calls=2)

        @guard_tool_call("test_tool", max_calls=2)
        async def test_tool(prompt="test", params=None, parent_id="parent"):
            return "tool_result"

        # Mock the global guard
        with patch("cblm.opipe.guards.decorators.get_guard", return_value=test_guard):
            # First two calls should work with different prompts
            result1 = await test_tool(prompt="test1")
            result2 = await test_tool(prompt="test2")
            assert result1 == "tool_result"
            assert result2 == "tool_result"

            # Third call should be blocked
            result3 = await test_tool(prompt="test3")
            assert result3["error"] == "tool_budget_exceeded"

    @pytest.mark.asyncio
    async def test_ensure_final_output_decorator(self):
        """Test @ensure_final_output decorator"""

        @ensure_final_output()
        async def generate_response(context="test"):
            return "final_response"

        guard = get_guard()

        # Should block if not in FINAL state
        guard.set_state(AgentState.RUNNING_TOOLS)
        result = await generate_response()
        assert result["status"] == "intermediate"

        # Should work in FINAL state
        guard.set_state(AgentState.FINAL)
        result = await generate_response()
        assert result == "final_response"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
