# CoolBits.ai @oPipe - NHA Enforcer Tests
# Test suite pentru runtime governance și policy enforcement

import pytest
import os
from unittest.mock import patch

from ..enforcer import (
    enforce_request,
    reload_registry,
    check_capability,
    check_secret,
    check_permission,
    health,
    get_agent_info,
    list_active_agents,
    get_audit_stats,
)
from ..registry import Registry, NHA, Channel, Capability, SLO


class TestEnforcer:
    """Test cases for NHA enforcer"""

    def setup_method(self):
        """Setup test environment"""
        # Create temporary registry for testing
        self.test_registry = Registry(
            version="test",
            nhas=[
                NHA(
                    id="nha:test-agent",
                    name="@Test-Agent",
                    category="dev_tools",
                    owner="test",
                    status="active",
                    channels=[
                        Channel(kind="http", endpoint="http://test", auth="hmac")
                    ],
                    capabilities=[
                        Capability(
                            name="testing",
                            description="Test capability",
                            scopes=["read:test", "write:test"],
                        )
                    ],
                    permissions=["run.invoker", "storage.objectViewer"],
                    secrets=["nha/test-agent/hmac"],
                    tags=["env:test", "service:test"],
                    slo=SLO(),
                    notes="Test agent",
                ),
                NHA(
                    id="nha:deprecated-agent",
                    name="@Deprecated-Agent",
                    category="dev_tools",
                    owner="test",
                    status="deprecated",
                    channels=[Channel(kind="cli", endpoint="test", auth="none")],
                    capabilities=[],
                    permissions=[],
                    secrets=[],
                    tags=["env:test", "service:deprecated"],
                    slo=SLO(),
                    notes="Deprecated test agent",
                ),
                NHA(
                    id="nha:paused-agent",
                    name="@Paused-Agent",
                    category="dev_tools",
                    owner="test",
                    status="paused",
                    channels=[
                        Channel(kind="http", endpoint="http://paused", auth="jwt")
                    ],
                    capabilities=[
                        Capability(
                            name="readonly",
                            description="Read-only capability",
                            scopes=["read:paused"],
                        )
                    ],
                    permissions=["storage.objectViewer"],
                    secrets=[],
                    tags=["env:test", "service:paused"],
                    slo=SLO(),
                    notes="Paused test agent",
                ),
            ],
        )

    def test_deny_unknown_agent(self):
        """Test that unknown agents are denied"""
        result = enforce_request("nha:ghost", "test:action", {}, scope="read:test")
        assert not result.allowed
        assert result.decision == "DENY"
        assert result.reason == "unknown_agent"
        assert result.nha_id == "nha:ghost"

    def test_allow_known_agent_with_valid_scope(self):
        """Test that known agents with valid scopes are allowed"""
        # Mock the registry loading
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            result = enforce_request(
                "nha:test-agent", "run.invoker", {}, scope="read:test"
            )
            assert result.allowed
            assert result.decision == "ALLOW"
            assert result.reason == "ok"

    def test_deny_invalid_scope(self):
        """Test that invalid scopes are denied"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            result = enforce_request(
                "nha:test-agent", "run.invoker", {}, scope="invalid:scope"
            )
            assert not result.allowed
            assert result.decision == "DENY"
            assert result.reason == "scope_not_allowed"

    def test_deny_invalid_permission(self):
        """Test that invalid permissions are denied"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            result = enforce_request("nha:test-agent", "invalid.permission", {})
            assert not result.allowed
            assert result.decision == "DENY"
            assert result.reason == "permission_not_allowed"

    def test_deny_deprecated_agent(self):
        """Test that deprecated agents are denied"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            result = enforce_request("nha:deprecated-agent", "any:action", {})
            assert not result.allowed
            assert result.decision == "DENY"
            assert result.reason == "agent_deprecated"

    def test_paused_agent_readonly(self):
        """Test that paused agents only allow read operations"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            # Read operations should be allowed
            result = enforce_request(
                "nha:paused-agent", "storage.objectViewer", {}, scope="read:paused"
            )
            assert result.allowed
            assert result.decision == "ALLOW"

            # Write operations should be denied
            result = enforce_request(
                "nha:paused-agent", "storage.objectCreator", {}, scope="write:paused"
            )
            assert not result.allowed
            assert result.decision == "DENY"
            assert result.reason == "agent_paused_readonly"

    def test_secret_requirement(self):
        """Test secret requirement enforcement"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            # Agent has the required secret
            result = enforce_request(
                "nha:test-agent",
                "run.invoker",
                {},
                require_secret="nha/test-agent/hmac",
            )
            assert result.allowed

            # Agent doesn't have the required secret
            result = enforce_request(
                "nha:test-agent",
                "run.invoker",
                {},
                require_secret="nha/test-agent/missing",
            )
            assert not result.allowed
            assert result.decision == "DENY"
            assert result.reason == "secret_not_allowed"

    def test_check_capability(self):
        """Test capability checking"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            # Valid capability
            assert check_capability("nha:test-agent", "read:test")
            assert check_capability("nha:test-agent", "write:test")

            # Invalid capability
            assert not check_capability("nha:test-agent", "invalid:scope")

            # Unknown agent
            assert not check_capability("nha:unknown", "read:test")

    def test_check_secret(self):
        """Test secret checking"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            # Valid secret
            assert check_secret("nha:test-agent", "nha/test-agent/hmac")

            # Invalid secret
            assert not check_secret("nha:test-agent", "nha/test-agent/missing")

            # Unknown agent
            assert not check_secret("nha:unknown", "nha/test-agent/hmac")

    def test_check_permission(self):
        """Test permission checking"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            # Valid permission
            assert check_permission("nha:test-agent", "run.invoker")
            assert check_permission("nha:test-agent", "storage.objectViewer")

            # Invalid permission
            assert not check_permission("nha:test-agent", "invalid.permission")

            # Unknown agent
            assert not check_permission("nha:unknown", "run.invoker")

    def test_health_status(self):
        """Test health status reporting"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            health_info = health()
            assert "mode" in health_info
            assert "fail_closed" in health_info
            assert "registry_version" in health_info
            assert "agents_cached" in health_info
            assert "policy_version" in health_info
            assert "audit_file" in health_info

    def test_get_agent_info(self):
        """Test agent info retrieval"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            # Valid agent
            info = get_agent_info("nha:test-agent")
            assert info is not None
            assert info["id"] == "nha:test-agent"
            assert info["name"] == "@Test-Agent"
            assert info["status"] == "active"
            assert "run.invoker" in info["permissions"]
            assert "nha/test-agent/hmac" in info["secrets"]

            # Unknown agent
            info = get_agent_info("nha:unknown")
            assert info is None

    def test_list_active_agents(self):
        """Test active agents listing"""
        with patch("cblm.opipe.nha.enforcer.load_yaml") as mock_load:
            mock_load.return_value = self.test_registry
            reload_registry()

            active_agents = list_active_agents()
            assert "nha:test-agent" in active_agents
            assert "nha:paused-agent" in active_agents
            assert "nha:deprecated-agent" not in active_agents

    def test_audit_stats(self):
        """Test audit statistics"""
        # This test would require actual audit file creation
        # For now, just test that the function doesn't crash
        stats = get_audit_stats()
        assert isinstance(stats, dict)
        assert "total_records" in stats


class TestEnforcementModes:
    """Test different enforcement modes"""

    def test_warn_mode(self):
        """Test warn mode enforcement"""
        with patch.dict(os.environ, {"NHA_ENFORCEMENT_MODE": "warn"}):
            # Reload enforcer with warn mode
            from ..enforcer import reload_registry

            reload_registry()

            # Unknown agent should warn but allow
            result = enforce_request("nha:unknown", "test:action", {})
            assert result.allowed
            assert result.decision == "WARN"
            assert result.reason == "unknown_agent"

    def test_fail_closed_mode(self):
        """Test fail-closed mode"""
        with patch.dict(os.environ, {"NHA_ENFORCEMENT_MODE": "fail-closed"}):
            # This would require mocking the registry loading failure
            # For now, just test that the mode is recognized
            from ..enforcer import FAIL_CLOSED

            assert FAIL_CLOSED


if __name__ == "__main__":
    pytest.main([__file__])
