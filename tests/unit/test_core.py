# CoolBits.ai Unit Tests
# ======================

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from coolbits_web_app import app
from coolbits_rag_system import RAGSystem
from coolbits_secrets_manager import SecretsManager


class TestCoolBitsWebApp:
    """Test cases for the main web application."""

    def test_app_initialization(self):
        """Test that the app initializes correctly."""
        assert app is not None
        assert hasattr(app, "run")

    def test_app_configuration(self):
        """Test app configuration."""
        # Add configuration tests here
        pass


class TestRAGSystem:
    """Test cases for the RAG system."""

    def test_rag_initialization(self):
        """Test RAG system initialization."""
        rag = RAGSystem()
        assert rag is not None

    def test_rag_query(self):
        """Test RAG query functionality."""
        rag = RAGSystem()
        # Mock test - in real implementation, you'd test with actual data
        result = rag.query("test query")
        assert result is not None


class TestSecretsManager:
    """Test cases for secrets management."""

    def test_secrets_manager_initialization(self):
        """Test secrets manager initialization."""
        sm = SecretsManager()
        assert sm is not None

    def test_secrets_loading(self):
        """Test secrets loading functionality."""
        sm = SecretsManager()
        # Mock test - in real implementation, you'd test with actual secrets
        secrets = sm.load_secrets()
        assert isinstance(secrets, dict)


if __name__ == "__main__":
    pytest.main([__file__])
