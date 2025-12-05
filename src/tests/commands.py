"""
Command tests for a_bot.
"""

from .base import BaseTest
from ..utils.report import TestResult, TestStatus
from ..utils.logging import get_logger

logger = get_logger(__name__)


class CommandTests(BaseTest):
    """Tests for bot commands."""

    async def run_all(self) -> list[TestResult]:
        """Run all command tests."""
        tests = [
            ("Command: /start", self.test_start_command),
            ("Command: /help", self.test_help_command),
            ("Command: /menu", self.test_menu_command),
            ("Command: /spreads", self.test_spreads_command),
            ("Command: /alerts", self.test_alerts_command),
            ("Command: /newalert", self.test_newalert_command),
            ("Command: /settings", self.test_settings_command),
        ]

        results = []
        for name, test_func in tests:
            result = await self.run_test(name, test_func)
            results.append(result)
            await self.delay()

        return results

    async def test_start_command(self) -> TestResult:
        """Test /start command."""
        response = await self.client.send_command("/start")

        self.assert_response_received()

        # Check for welcome message elements
        text = self.client.last_text.lower()
        has_welcome = any(word in text for word in ["welcome", "привет", "👋", "hello"])

        if not has_welcome:
            return TestResult(
                name="test_start_command",
                status=TestStatus.FAILED,
                message=f"Expected welcome message, got: {text[:200]}",
            )

        # Check for main menu buttons
        self.assert_has_button(data_contains="spreads")

        return TestResult(
            name="test_start_command",
            status=TestStatus.PASSED,
            message="Welcome message received with menu buttons",
            details={"response_length": len(text)},
        )

    async def test_help_command(self) -> TestResult:
        """Test /help command."""
        response = await self.client.send_command("/help")

        self.assert_response_received()

        text = self.client.last_text.lower()

        # Check for help content
        has_help = any(word in text for word in ["help", "command", "помощь", "/"])

        if not has_help:
            return TestResult(
                name="test_help_command",
                status=TestStatus.FAILED,
                message=f"Expected help content, got: {text[:200]}",
            )

        return TestResult(
            name="test_help_command",
            status=TestStatus.PASSED,
            message="Help message received",
        )

    async def test_menu_command(self) -> TestResult:
        """Test /menu command."""
        response = await self.client.send_command("/menu")

        self.assert_response_received()

        # Check for menu buttons
        buttons = self.client.get_buttons()
        if not buttons:
            return TestResult(
                name="test_menu_command",
                status=TestStatus.FAILED,
                message="Menu should have inline buttons",
            )

        return TestResult(
            name="test_menu_command",
            status=TestStatus.PASSED,
            message=f"Menu displayed with {len(buttons)} buttons",
            details={"button_count": len(buttons)},
        )

    async def test_spreads_command(self) -> TestResult:
        """Test /spreads command."""
        response = await self.client.send_command("/spreads")

        self.assert_response_received()

        text = self.client.last_text.lower()

        # Should contain spread-related content or "fetching" message
        has_spreads = any(
            word in text
            for word in ["spread", "funding", "спред", "fetching", "loading", "📊", "no"]
        )

        if not has_spreads:
            return TestResult(
                name="test_spreads_command",
                status=TestStatus.FAILED,
                message=f"Expected spreads content, got: {text[:200]}",
            )

        return TestResult(
            name="test_spreads_command",
            status=TestStatus.PASSED,
            message="Spreads data or loading message received",
        )

    async def test_alerts_command(self) -> TestResult:
        """Test /alerts command."""
        response = await self.client.send_command("/alerts")

        self.assert_response_received()

        text = self.client.last_text.lower()

        # Should contain alerts-related content
        has_alerts = any(
            word in text
            for word in ["alert", "оповещ", "🔔", "no alerts", "your alerts"]
        )

        if not has_alerts:
            return TestResult(
                name="test_alerts_command",
                status=TestStatus.FAILED,
                message=f"Expected alerts content, got: {text[:200]}",
            )

        return TestResult(
            name="test_alerts_command",
            status=TestStatus.PASSED,
            message="Alerts list displayed",
        )

    async def test_newalert_command(self) -> TestResult:
        """Test /newalert command starts alert creation."""
        response = await self.client.send_command("/newalert")

        self.assert_response_received()

        text = self.client.last_text.lower()

        # Should start alert creation flow
        has_creation = any(
            word in text
            for word in ["alert", "create", "symbol", "spread", "select", "choose"]
        )

        if not has_creation:
            return TestResult(
                name="test_newalert_command",
                status=TestStatus.FAILED,
                message=f"Expected alert creation flow, got: {text[:200]}",
            )

        # Cancel the flow to clean up
        if self.client.has_button(text="Cancel") or self.client.has_button(data_contains="cancel"):
            try:
                await self.client.click_button(text="Cancel")
            except Exception:
                pass

        return TestResult(
            name="test_newalert_command",
            status=TestStatus.PASSED,
            message="Alert creation flow started",
        )

    async def test_settings_command(self) -> TestResult:
        """Test /settings command."""
        response = await self.client.send_command("/settings")

        self.assert_response_received()

        text = self.client.last_text.lower()

        # Should contain settings-related content
        has_settings = any(
            word in text
            for word in ["setting", "настрой", "language", "timezone", "⚙️"]
        )

        if not has_settings:
            return TestResult(
                name="test_settings_command",
                status=TestStatus.FAILED,
                message=f"Expected settings content, got: {text[:200]}",
            )

        return TestResult(
            name="test_settings_command",
            status=TestStatus.PASSED,
            message="Settings displayed",
        )
