# CoolBits.ai Feature Flags Configuration
# =======================================

import os
import json
from typing import Dict, Any
from pathlib import Path


class FeatureFlags:
    """Feature flags manager - all features OFF by default"""

    def __init__(self, config_file: str = "feature-flags.json"):
        self.config_file = Path(config_file)
        self.flags = self._load_default_flags()
        self._load_config()

    def _load_default_flags(self) -> Dict[str, Any]:
        """Load default feature flags (all OFF)"""
        return {
            # Core features
            "enable_gpu_acceleration": False,
            "enable_google_cloud": False,
            "enable_vertex_ai": False,
            "enable_openai_integration": False,
            "enable_xai_integration": False,
            # Security features
            "enable_hmac_validation": False,
            "enable_secret_rotation": False,
            "enable_audit_logging": False,
            "enable_rate_limiting": False,
            # Monitoring features
            "enable_cost_monitoring": False,
            "enable_performance_monitoring": False,
            "enable_error_tracking": False,
            "enable_uptime_monitoring": False,
            # Development features
            "enable_debug_mode": False,
            "enable_hot_reload": False,
            "enable_api_documentation": False,
            "enable_swagger_ui": False,
            # Experimental features
            "enable_rag_system": False,
            "enable_multi_agent_chat": False,
            "enable_automation_engine": False,
            "enable_cbt_economy": False,
            # Integration features
            "enable_meta_platform": False,
            "enable_email_routing": False,
            "enable_slack_integration": False,
            "enable_discord_integration": False,
            # Advanced features
            "enable_canary_deployment": False,
            "enable_blue_green_deployment": False,
            "enable_chaos_engineering": False,
            "enable_disaster_recovery": False,
            # UI features
            "enable_dark_mode": False,
            "enable_mobile_ui": False,
            "enable_accessibility": False,
            "enable_internationalization": False,
        }

    def _load_config(self):
        """Load configuration from file or environment"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    self.flags.update(config)
            except Exception as e:
                print(f"⚠️  Error loading feature flags config: {e}")

        # Override with environment variables
        for flag_name in self.flags:
            env_var = f"COOLBITS_{flag_name.upper()}"
            if env_var in os.environ:
                value = os.environ[env_var].lower()
                self.flags[flag_name] = value in ("true", "1", "yes", "on")

    def is_enabled(self, flag_name: str) -> bool:
        """Check if a feature flag is enabled"""
        return self.flags.get(flag_name, False)

    def enable(self, flag_name: str) -> bool:
        """Enable a feature flag"""
        if flag_name in self.flags:
            self.flags[flag_name] = True
            self._save_config()
            return True
        return False

    def disable(self, flag_name: str) -> bool:
        """Disable a feature flag"""
        if flag_name in self.flags:
            self.flags[flag_name] = False
            self._save_config()
            return True
        return False

    def toggle(self, flag_name: str) -> bool:
        """Toggle a feature flag"""
        if flag_name in self.flags:
            self.flags[flag_name] = not self.flags[flag_name]
            self._save_config()
            return self.flags[flag_name]
        return False

    def get_all_flags(self) -> Dict[str, Any]:
        """Get all feature flags"""
        return self.flags.copy()

    def get_enabled_flags(self) -> Dict[str, Any]:
        """Get only enabled feature flags"""
        return {k: v for k, v in self.flags.items() if v}

    def get_disabled_flags(self) -> Dict[str, Any]:
        """Get only disabled feature flags"""
        return {k: v for k, v in self.flags.items() if not v}

    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.flags, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving feature flags config: {e}")

    def reset_to_defaults(self):
        """Reset all flags to default (OFF)"""
        self.flags = self._load_default_flags()
        self._save_config()

    def export_config(self) -> str:
        """Export configuration as JSON string"""
        return json.dumps(self.flags, indent=2)

    def import_config(self, config_json: str):
        """Import configuration from JSON string"""
        try:
            config = json.loads(config_json)
            self.flags.update(config)
            self._save_config()
        except Exception as e:
            print(f"⚠️  Error importing feature flags config: {e}")


# Global feature flags instance
feature_flags = FeatureFlags()


# Convenience functions
def is_feature_enabled(flag_name: str) -> bool:
    """Check if a feature is enabled"""
    return feature_flags.is_enabled(flag_name)


def enable_feature(flag_name: str) -> bool:
    """Enable a feature"""
    return feature_flags.enable(flag_name)


def disable_feature(flag_name: str) -> bool:
    """Disable a feature"""
    return feature_flags.disable(flag_name)


def toggle_feature(flag_name: str) -> bool:
    """Toggle a feature"""
    return feature_flags.toggle(flag_name)


# Feature flag decorator
def require_feature(flag_name: str):
    """Decorator to require a feature flag"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_feature_enabled(flag_name):
                raise FeatureNotEnabledError(f"Feature '{flag_name}' is not enabled")
            return func(*args, **kwargs)

        return wrapper

    return decorator


class FeatureNotEnabledError(Exception):
    """Exception raised when a required feature is not enabled"""

    pass


# Example usage:
if __name__ == "__main__":
    print("🔧 CoolBits.ai Feature Flags")
    print("============================")
    print(f"Total flags: {len(feature_flags.get_all_flags())}")
    print(f"Enabled flags: {len(feature_flags.get_enabled_flags())}")
    print(f"Disabled flags: {len(feature_flags.get_disabled_flags())}")

    print("\n📋 All Feature Flags:")
    for flag, enabled in feature_flags.get_all_flags().items():
        status = "✅" if enabled else "❌"
        print(f"  {status} {flag}")

    print("\n🎯 Enabled Features:")
    enabled = feature_flags.get_enabled_flags()
    if enabled:
        for flag in enabled:
            print(f"  ✅ {flag}")
    else:
        print("  (No features enabled - all OFF by default)")
