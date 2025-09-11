# CoolBits.ai Integration Tests
# =============================

import pytest
import requests
import time
import subprocess
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestAPIIntegration:
    """Integration tests for API endpoints."""

    @pytest.fixture(autouse=True)
    def setup_server(self):
        """Start the server for integration tests."""
        # Start server in background
        self.server_process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "coolbits_web_app.py",
                "--server.port=8502",
            ]
        )
        time.sleep(10)  # Wait for server to start
        yield
        # Cleanup
        self.server_process.terminate()
        self.server_process.wait()

    def test_health_endpoint(self):
        """Test health endpoint."""
        response = requests.get("http://localhost:8502/_stcore/health")
        assert response.status_code == 200

    def test_main_page_loads(self):
        """Test that main page loads correctly."""
        response = requests.get("http://localhost:8502")
        assert response.status_code == 200
        assert "CoolBits.ai" in response.text


class TestRAGIntegration:
    """Integration tests for RAG system."""

    def test_rag_with_qdrant(self):
        """Test RAG system with Qdrant vector database."""
        # This would test actual integration with Qdrant
        # For now, we'll create a mock test
        pass

    def test_rag_with_openai(self):
        """Test RAG system with OpenAI API."""
        # This would test actual integration with OpenAI
        # For now, we'll create a mock test
        pass


if __name__ == "__main__":
    pytest.main([__file__])
