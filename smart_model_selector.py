#!/usr/bin/env python3
"""
Smart Model Selection Script
CoolBits.ai - Automatically select the best model based on context and cost
"""

import yaml
from typing import Dict


class SmartModelSelector:
    """Smart model selector based on context and cost optimization"""

    def __init__(self, config_file: str = "api_cost_optimization_config.yaml"):
        """Initialize with configuration"""
        self.config = self.load_config(config_file)
        self.usage_stats = {"development": 0, "production": 0, "premium": 0}

    def load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML file"""
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Config file {config_file} not found, using defaults")
            return self.get_default_config()

    def get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "development": {
                "openai": {"model": "gpt-4o-mini", "input_cost_per_1m": 0.15},
                "xai": {"model": "grok-3-mini", "input_cost_per_1m": 0.30},
            },
            "production": {
                "openai": {"model": "gpt-4o", "input_cost_per_1m": 2.50},
                "xai": {"model": "grok-2-1212", "input_cost_per_1m": 2.00},
            },
            "premium": {
                "openai": {"model": "gpt-4", "input_cost_per_1m": 30.00},
                "xai": {"model": "grok-4-0709", "input_cost_per_1m": 3.00},
            },
        }

    def select_model(
        self,
        context: str = "development",
        provider: str = "openai",
        task_complexity: str = "simple",
        budget_limit: float = 10.0,
    ) -> Dict:
        """Select the best model based on context and constraints"""

        # Determine tier based on context and task complexity
        if context == "development" or task_complexity == "simple":
            tier = "development"
        elif context == "production" and task_complexity == "medium":
            tier = "production"
        elif context == "premium" or task_complexity == "complex":
            tier = "premium"
        else:
            tier = "development"  # Default to cheapest

        # Check budget constraints
        if self.usage_stats[tier] > budget_limit * 0.8:  # 80% threshold
            print(f"⚠️  Budget warning for {tier} tier, falling back to development")
            tier = "development"

        # Get model configuration
        model_config = self.config[tier][provider]

        # Update usage stats
        self.usage_stats[tier] += model_config["input_cost_per_1m"] * 0.001  # Estimate

        return {
            "tier": tier,
            "provider": provider,
            "model": model_config["model"],
            "cost_per_1m": model_config["input_cost_per_1m"],
            "reason": f"Selected {tier} tier for {context} context",
        }

    def get_cost_estimate(self, tokens: int, tier: str, provider: str) -> float:
        """Estimate cost for given tokens"""
        model_config = self.config[tier][provider]
        cost_per_1m = model_config["input_cost_per_1m"]
        return (tokens / 1_000_000) * cost_per_1m

    def print_cost_comparison(self, tokens: int = 1000):
        """Print cost comparison for different models"""
        print(f"💰 Cost Comparison for {tokens:,} tokens:")
        print("=" * 50)

        for tier in ["development", "production", "premium"]:
            for provider in ["openai", "xai"]:
                cost = self.get_cost_estimate(tokens, tier, provider)
                model = self.config[tier][provider]["model"]
                print(f"{tier:12} | {provider:6} | {model:15} | ${cost:.6f}")

        print("=" * 50)
        print("💡 Recommendation: Use development tier for 90%+ cost savings!")


def main():
    """Main function"""
    print("🧠 Smart Model Selection System")
    print("=" * 40)

    selector = SmartModelSelector()

    # Print cost comparison
    selector.print_cost_comparison(1000)

    # Example selections
    print("\n🎯 Example Model Selections:")
    print("=" * 40)

    examples = [
        {"context": "development", "provider": "openai", "task_complexity": "simple"},
        {"context": "production", "provider": "xai", "task_complexity": "medium"},
        {"context": "premium", "provider": "openai", "task_complexity": "complex"},
    ]

    for example in examples:
        selection = selector.select_model(**example)
        print(
            f"Context: {example['context']:12} | Model: {selection['model']:15} | Cost: ${selection['cost_per_1m']:.2f}/1M"
        )

    print("\n✅ Smart model selection configured!")
    print("🚀 Use this system to automatically select cost-optimized models!")


if __name__ == "__main__":
    main()
