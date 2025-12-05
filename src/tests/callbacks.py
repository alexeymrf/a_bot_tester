"""
Callback/button tests for a_bot.
"""

from .base import BaseTest
from ..utils.report import TestResult, TestStatus
from ..utils.logging import get_logger

logger = get_logger(__name__)


class CallbackTests(BaseTest):
    """Tests for bot inline buttons and callbacks."""

    async def run_all(self) -> list[TestResult]:
        """Run all callback tests."""
        tests = [
            ("Callback: Main Menu Navigation", self.test_main_menu_navigation),
            ("Callback: Spreads from Menu", self.test_spreads_from_menu),
            ("Callback: Alerts from Menu", self.test_alerts_from_menu),
            ("Callback: Settings from Menu", self.test_settings_from_menu),
            ("Callback: Home Button", self.test_home_button),
            ("Callback: Refresh Spreads", self.test_refresh_spreads),
        ]

        results = []
        for name, test_func in tests:
            result = await self.run_test(name, test_func)
            results.append(result)
            await self.delay()

        return results

    async def test_main_menu_navigation(self) -> TestResult:
        """Test main menu buttons are present after /start."""
        await self.client.send_command("/start")
        self.assert_response_received()

        buttons = self.client.get_buttons()
        if len(buttons) < 2:
            return TestResult(
                name="test_main_menu_navigation",
                status=TestStatus.FAILED,
                message=f"Expected at least 2 menu buttons, got {len(buttons)}",
            )

        # Check for expected buttons
        button_texts = [b["text"].lower() for b in buttons]
        expected_buttons = ["spread", "alert", "setting"]

        found = sum(1 for exp in expected_buttons if any(exp in text for text in button_texts))

        if found < 2:
            return TestResult(
                name="test_main_menu_navigation",
                status=TestStatus.FAILED,
                message=f"Expected main menu buttons, got: {button_texts}",
            )

        return TestResult(
            name="test_main_menu_navigation",
            status=TestStatus.PASSED,
            message=f"Found {len(buttons)} menu buttons",
            details={"buttons": button_texts},
        )

    async def test_spreads_from_menu(self) -> TestResult:
        """Test clicking spreads button from menu."""
        await self.client.send_command("/menu")
        self.assert_response_received()

        # Find and click spreads button
        if not self.client.has_button(data_contains="spreads"):
            return TestResult(
                name="test_spreads_from_menu",
                status=TestStatus.SKIPPED,
                message="Spreads button not found in menu",
            )

        await self.client.click_button(data_contains="spreads")
        await self.delay(1)

        text = self.client.last_text.lower()
        has_spreads = any(
            word in text
            for word in ["spread", "funding", "📊", "no", "loading", "fetching"]
        )

        if not has_spreads:
            return TestResult(
                name="test_spreads_from_menu",
                status=TestStatus.FAILED,
                message=f"Expected spreads view, got: {text[:200]}",
            )

        return TestResult(
            name="test_spreads_from_menu",
            status=TestStatus.PASSED,
            message="Spreads view opened from menu",
        )

    async def test_alerts_from_menu(self) -> TestResult:
        """Test clicking alerts button from menu."""
        await self.client.send_command("/menu")
        self.assert_response_received()

        # Find and click alerts button
        if not self.client.has_button(data_contains="alerts"):
            return TestResult(
                name="test_alerts_from_menu",
                status=TestStatus.SKIPPED,
                message="Alerts button not found in menu",
            )

        await self.client.click_button(data_contains="alerts")
        await self.delay(1)

        text = self.client.last_text.lower()
        has_alerts = any(
            word in text
            for word in ["alert", "🔔", "no alerts", "your alerts"]
        )

        if not has_alerts:
            return TestResult(
                name="test_alerts_from_menu",
                status=TestStatus.FAILED,
                message=f"Expected alerts view, got: {text[:200]}",
            )

        return TestResult(
            name="test_alerts_from_menu",
            status=TestStatus.PASSED,
            message="Alerts view opened from menu",
        )

    async def test_settings_from_menu(self) -> TestResult:
        """Test clicking settings button from menu."""
        await self.client.send_command("/menu")
        self.assert_response_received()

        # Find and click settings button
        if not self.client.has_button(data_contains="settings"):
            return TestResult(
                name="test_settings_from_menu",
                status=TestStatus.SKIPPED,
                message="Settings button not found in menu",
            )

        await self.client.click_button(data_contains="settings")
        await self.delay(1)

        text = self.client.last_text.lower()
        has_settings = any(
            word in text
            for word in ["setting", "language", "timezone", "⚙️"]
        )

        if not has_settings:
            return TestResult(
                name="test_settings_from_menu",
                status=TestStatus.FAILED,
                message=f"Expected settings view, got: {text[:200]}",
            )

        return TestResult(
            name="test_settings_from_menu",
            status=TestStatus.PASSED,
            message="Settings view opened from menu",
        )

    async def test_home_button(self) -> TestResult:
        """Test home button returns to main menu."""
        # First go to a sub-view
        await self.client.send_command("/settings")
        self.assert_response_received()

        # Find and click home button
        if not self.client.has_button(text="🏠") and not self.client.has_button(data_contains="home"):
            return TestResult(
                name="test_home_button",
                status=TestStatus.SKIPPED,
                message="Home button not found",
            )

        try:
            if self.client.has_button(text="🏠"):
                await self.client.click_button(text="🏠")
            else:
                await self.client.click_button(data_contains="home")
        except Exception as e:
            return TestResult(
                name="test_home_button",
                status=TestStatus.FAILED,
                message=f"Failed to click home button: {e}",
            )

        await self.delay(1)

        # Should return to main menu
        buttons = self.client.get_buttons()
        if len(buttons) >= 2:
            return TestResult(
                name="test_home_button",
                status=TestStatus.PASSED,
                message="Returned to main menu",
            )

        return TestResult(
            name="test_home_button",
            status=TestStatus.FAILED,
            message="Did not return to main menu",
        )

    async def test_refresh_spreads(self) -> TestResult:
        """Test refresh button on spreads view."""
        await self.client.send_command("/spreads")
        await self.delay(2)  # Wait for spreads to load
        self.assert_response_received()

        # Find and click refresh button
        if not self.client.has_button(text="🔄") and not self.client.has_button(data_contains="refresh"):
            return TestResult(
                name="test_refresh_spreads",
                status=TestStatus.SKIPPED,
                message="Refresh button not found",
            )

        try:
            if self.client.has_button(text="��"):
                await self.client.click_button(text="🔄")
            else:
                await self.client.click_button(data_contains="refresh")
        except Exception as e:
            return TestResult(
                name="test_refresh_spreads",
                status=TestStatus.FAILED,
                message=f"Failed to click refresh: {e}",
            )

        await self.delay(2)

        # Should still show spreads
        text = self.client.last_text.lower()
        has_spreads = any(
            word in text
            for word in ["spread", "funding", "📊", "no"]
        )

        if not has_spreads:
            return TestResult(
                name="test_refresh_spreads",
                status=TestStatus.FAILED,
                message="Refresh did not maintain spreads view",
            )

        return TestResult(
            name="test_refresh_spreads",
            status=TestStatus.PASSED,
            message="Spreads refreshed successfully",
        )
