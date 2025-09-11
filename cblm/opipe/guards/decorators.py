#!/usr/bin/env python3
"""
Decorators for Multi-Agent Guard System
Easy integration with existing agent code
"""

import functools
import asyncio
from typing import Callable, Any, Dict
from .multi_agent_guard import get_guard, AgentState

def guard_tool_call(tool_name: str, max_calls: int = 8):
    """Decorator to guard tool calls"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            guard = get_guard()
            
            # Extract prompt and params from kwargs
            prompt = kwargs.get('prompt', '')
            params = kwargs.get('params', {})
            parent_id = kwargs.get('parent_id', '')
            
            if not guard.allow_tool_call(tool_name, prompt, params, parent_id):
                return {
                    "error": "tool_budget_exceeded",
                    "tool": tool_name,
                    "reason": "budget_limit_reached"
                }
            
            try:
                result = await func(*args, **kwargs)
                return result
            except asyncio.TimeoutError:
                guard.record_tool_failure(tool_name, is_timeout=True)
                return {
                    "error": "tool_timeout",
                    "tool": tool_name,
                    "reason": "timeout_exceeded"
                }
            except Exception as e:
                guard.record_tool_failure(tool_name, is_timeout=False)
                return {
                    "error": "tool_failure",
                    "tool": tool_name,
                    "reason": str(e)
                }
        
        return wrapper
    return decorator

def guard_subagent(max_depth: int = 3):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            guard = get_guard()
            # verificăm înainte, nu incrementăm
            if getattr(guard, "current_depth", 0) >= max_depth:
                return {"error": "max_depth_exceeded", "reason": "subagent_depth_limit_reached"}
            # acceptăm → incrementăm; garantăm decrement în finally
            guard.current_depth = getattr(guard, "current_depth", 0) + 1
            try:
                return await func(*args, **kwargs)
            finally:
                guard.current_depth = max(0, guard.current_depth - 1)
        return wrapper
    return decorator

def ensure_final_output():
    """Decorator to ensure only final output is sent"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            guard = get_guard()
            
            if not guard.can_send_output():
                return {
                    "status": "intermediate",
                    "reason": "waiting_for_tools_or_subagents"
                }
            
            result = await func(*args, **kwargs)
            return result
        
        return wrapper
    return decorator

def with_barrier(timeout: float = 30):
    """Decorator to run multiple async operations with barrier"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            guard = get_guard()
            
            # Extract tasks from kwargs or return value
            tasks = kwargs.get('tasks', [])
            if not tasks:
                # If function returns tasks, extract them
                result = await func(*args, **kwargs)
                if isinstance(result, list):
                    tasks = result
                else:
                    return result
            
            try:
                results = await guard.run_subagents_with_barrier(tasks, timeout)
                return results
            except asyncio.TimeoutError:
                return {
                    "error": "barrier_timeout",
                    "reason": "subagents_did_not_complete_in_time"
                }
        
        return wrapper
    return decorator

# Usage examples:
"""
# Guard tool calls:
@guard_tool_call("search", max_calls=5)
async def search_tool(query: str, **kwargs):
    # Your tool implementation
    pass

# Guard subagent calls:
@guard_subagent(max_depth=3)
async def subagent_call(task: str, **kwargs):
    # Your subagent implementation
    pass

# Ensure final output:
@ensure_final_output()
async def generate_response(context: str, **kwargs):
    # Your response generation
    pass

# Run with barrier:
@with_barrier(timeout=30)
async def run_parallel_tasks(tasks: list, **kwargs):
    return tasks  # Will be executed with barrier
"""
