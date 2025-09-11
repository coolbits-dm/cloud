#!/usr/bin/env python3
"""
API Cost Dashboard Server
CoolBits.ai - Real-time cost monitoring and optimization
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn
import json
import os
from datetime import datetime
from typing import Dict, List

app = FastAPI(title="CoolBits.ai API Cost Dashboard", version="1.0.0")

# Mount static files
app.mount("/static", StaticFiles(directory="."), name="static")


@app.get("/", response_class=HTMLResponse)
async def cost_dashboard():
    """Serve the cost dashboard"""
    try:
        with open("api_cost_dashboard.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Cost Dashboard not found</h1>", status_code=404
        )


@app.get("/api/cost-stats")
async def get_cost_stats():
    """Get current cost statistics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "optimization_status": "active",
        "models": {
            "development": {
                "openai": {"model": "gpt-4o-mini", "cost_per_1m": 0.15},
                "xai": {"model": "grok-3-mini", "cost_per_1m": 0.30},
            },
            "production": {
                "openai": {"model": "gpt-4o", "cost_per_1m": 2.50},
                "xai": {"model": "grok-2-1212", "cost_per_1m": 2.00},
            },
            "premium": {
                "openai": {"model": "gpt-4", "cost_per_1m": 30.00},
                "xai": {"model": "grok-4-0709", "cost_per_1m": 3.00},
            },
        },
        "savings": {
            "gpt4_to_gpt4o_mini": "200x cheaper",
            "grok2_to_grok3_mini": "6.7x cheaper",
            "total_savings_percentage": "90%+",
        },
        "recommendations": [
            "Use development tier for 90% of tasks",
            "Limit context tokens to reduce input costs",
            "Monitor daily/weekly/monthly budgets",
            "Use premium models only when necessary",
        ],
    }


@app.get("/api/usage-estimate")
async def get_usage_estimate(tokens: int = 1000):
    """Get cost estimate for given tokens"""
    estimates = {
        "tokens": tokens,
        "costs": {
            "gpt-4": (tokens / 1_000_000) * 30.00,
            "gpt-4o-mini": (tokens / 1_000_000) * 0.15,
            "grok-2-1212": (tokens / 1_000_000) * 2.00,
            "grok-3-mini": (tokens / 1_000_000) * 0.30,
        },
    }

    # Calculate savings
    old_cost = estimates["costs"]["gpt-4"]
    new_cost = estimates["costs"]["gpt-4o-mini"]
    savings_percentage = ((old_cost - new_cost) / old_cost) * 100 if old_cost > 0 else 0

    estimates["savings"] = {
        "amount": old_cost - new_cost,
        "percentage": savings_percentage,
    }

    return estimates


@app.get("/api/model-recommendation")
async def get_model_recommendation(
    context: str = "development", task_complexity: str = "simple"
):
    """Get model recommendation based on context"""
    recommendations = {
        "development": {
            "openai": "gpt-4o-mini",
            "xai": "grok-3-mini",
            "reason": "Cheapest models for testing and development",
        },
        "production": {
            "openai": "gpt-4o",
            "xai": "grok-2-1212",
            "reason": "Balanced cost and performance for production",
        },
        "premium": {
            "openai": "gpt-4",
            "xai": "grok-4-0709",
            "reason": "Highest quality for complex tasks",
        },
    }

    # Determine tier based on context and complexity
    if context == "development" or task_complexity == "simple":
        tier = "development"
    elif context == "production" and task_complexity == "medium":
        tier = "production"
    elif context == "premium" or task_complexity == "complex":
        tier = "premium"
    else:
        tier = "development"

    return {
        "recommended_tier": tier,
        "recommendation": recommendations[tier],
        "context": context,
        "task_complexity": task_complexity,
    }


if __name__ == "__main__":
    print("🚀 Starting CoolBits.ai API Cost Dashboard Server...")
    print("🌐 Access: http://localhost:8095")
    print("💰 Cost optimization active!")

    uvicorn.run(app, host="0.0.0.0", port=8095, log_level="info")
