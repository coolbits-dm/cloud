# CoolBits.ai E2E Tests with Playwright
# =====================================

import pytest
from playwright.sync_api import sync_playwright, Page, Browser


class TestCoolBitsE2E:
    """End-to-end tests for CoolBits.ai application."""

    @pytest.fixture(scope="class")
    def browser(self):
        """Initialize browser for E2E tests."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            yield browser
            browser.close()

    @pytest.fixture
    def page(self, browser: Browser):
        """Create a new page for each test."""
        page = browser.new_page()
        yield page
        page.close()

    def test_main_page_loads(self, page: Page):
        """Test that main page loads correctly."""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Check if main elements are present
        assert page.title() is not None
        assert "CoolBits.ai" in page.content()

    def test_admin_console_access(self, page: Page):
        """Test admin console access."""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Look for admin console elements
        admin_elements = page.locator("text=Admin")
        if admin_elements.count() > 0:
            admin_elements.first.click()
            page.wait_for_load_state("networkidle")
            assert "Admin" in page.content()

    def test_rag_system_functionality(self, page: Page):
        """Test RAG system functionality."""
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Look for RAG-related elements
        rag_elements = page.locator("text=RAG")
        if rag_elements.count() > 0:
            rag_elements.first.click()
            page.wait_for_load_state("networkidle")

            # Test query input
            query_input = page.locator(
                "input[placeholder*='query'], input[placeholder*='search']"
            )
            if query_input.count() > 0:
                query_input.first.fill("test query")

                # Look for submit button
                submit_button = page.locator(
                    "button:has-text('Submit'), button:has-text('Search')"
                )
                if submit_button.count() > 0:
                    submit_button.first.click()
                    page.wait_for_load_state("networkidle")

    def test_responsive_design(self, page: Page):
        """Test responsive design on different screen sizes."""
        # Test desktop
        page.set_viewport_size({"width": 1920, "height": 1080})
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")

        # Test tablet
        page.set_viewport_size({"width": 768, "height": 1024})
        page.reload()
        page.wait_for_load_state("networkidle")

        # Test mobile
        page.set_viewport_size({"width": 375, "height": 667})
        page.reload()
        page.wait_for_load_state("networkidle")

    def test_error_handling(self, page: Page):
        """Test error handling."""
        # Test invalid URL
        page.goto("http://localhost:8501/nonexistent")
        page.wait_for_load_state("networkidle")

        # Should not crash the application
        page.goto("http://localhost:8501")
        page.wait_for_load_state("networkidle")
        assert "CoolBits.ai" in page.content()


if __name__ == "__main__":
    pytest.main([__file__])
