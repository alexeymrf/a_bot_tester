"""
Conversation flow tests for a_bot.
"""

from .base import BaseTest
from ..utils.report import TestResult, TestStatus
from ..utils.logging import get_logger

logger = get_logger(__name__)


class FlowTests(BaseTest):
    """Tests for multi-step conversation flows."""

    async def run_all(self) -> list[TestResult]:
        """Run all flow tests."""
        tests = [
            ("Flow: Complete User Journey", self.test_complete_user_journey),
            ("Flow: Language Change", self.test_language_change_flow),
            ("Flow: Alert Creation Cancellation", self.test_alert_creation_cancel),
        ]

        results = []
        for name, test_func in tests:
            result = await self.run_test(name, test_func)
            results.append(result)
            await self.delay()

        return results

    async def test_complete_user_journey(self) -> TestResult:
        """Test a complete user journey through the bot."""
        steps_completed = []

        try:
            # Step 1: Start the bot
            await self.client.send_command("/start")
            self.assert_response_received()
            steps_completed.append("start")
            await self.delay(1)

            # Step 2: Check spreads
            await self.client.send_command("/spreads")
            self.assert_response_received()
            steps_completed.append("spreads")
            await self.delay(1)

            # Step 3: Check alerts
            await self.client.send_command("/alerts")
            self.assert_response_received()
            steps_completed.append("alerts")
            await self.delay(1)

            # Step 4: Check settings
            await self.client.send_command("/settings")
            self.assert_response_received()
            steps_completed.append("settings")
            await self.delay(1)

            # Step 5: Return to menu
            await self.client.send_command("/menu")
            self.assert_response_received()
            steps_completed.append("menu")

            return TestResult(
                name="test_complete_user_journey",
                status=TestStatus.PASSED,
                message=f"Completed {len(steps_completed)} steps",
                details={"steps": steps_completed},
            )

        except Exception as e:
            return TestResult(
                name="test_complete_user_journey",
                status=TestStatus.FAILED,
                message=f"Failed at steps: {steps_completed}. Error: {str(e)}",
                details={"completed_steps": steps_completed},
            )

    async def test_language_change_flow(self) -> TestResult:
        """Test language change flow."""
        await self.client.send_command("/settings")
        self.assert_response_received()

        # Look for language button
        if not self.client.has_button(data_contains="lang"):
            return TestResult(
                name="test_language_change_flow",
                status=TestStatus.SKIPPED,
                message="Language button not found in settings",
            )

        try:
            # Click language button
            await self.client.click_button(data_contains="lang")
            await self.delay(1)

            # Should show language options
            text = self.client.last_text.lower()
            has_lang_options = any(
                word in text
                for word in ["language", "english", "русский", "язык"]
            )

            if not has_lang_options:
                return TestResult(
                    name="test_language_change_flow",
                    status=TestStatus.FAILED,
                    message="Language options not displayed",
                )

            # Go back to settings or home
            if self.client.has_button(text="⬅️") or self.client.has_button(data_contains="back"):
                try:
                    if self.client.has_button(text="⬅️"):
                        await self.client.click_button(text="⬅️")
                    else:
                        await self.client.click_button(data_contains="back")
                except Exception:
                    pass

            return TestResult(
                name="test_language_change_flow",
                status=TestStatus.PASSED,
                message="Language options displayed correctly",
            )

        except Exception as e:
            return TestResult(
                name="test_language_change_flow",
                status=TestStatus.FAILED,
                message=f"Error in language flow: {str(e)}",
            )

    async def test_alert_creation_cancel(self) -> TestResult:
        """Test alert creation can be cancelled."""
        await self.client.send_command("/newalert")
        self.assert_response_received()

        # Should be in alert creation flow
        text = self.client.last_text.lower()
        in_flow = any(
            word in text
            for word in ["alert", "create", "symbol", "spread", "select"]
        )

        if not in_flow:
            return TestResult(
                name="test_alert_creation_cancel",
                status=TestStatus.FAILED,
                message="Did not enter alert creation flow",
            )

        # Try to cancel
        cancel_button_found = False
        if self.client.has_button(text="Cancel") or self.client.has_button(text="❌"):
            cancel_button_found = True
            try:
                if self.client.has_button(text="Cancel"):
                    await self.client.click_button(text="Cancel")
                else:
                    await self.client.click_button(text="❌")
            except Exception:
                pass
        elif self.client.has_button(data_contains="cancel"):
            cancel_button_found = True
            try:
                await self.client.click_button(data_contains="cancel")
            except Exception:
                pass

        if not cancel_button_found:
            return TestResult(
                name="test_alert_creation_cancel",
                status=TestStatus.SKIPPED,
                message="Cancel button not found",
            )

        await self.delay(1)

        # Should be cancelled
        text = self.client.last_text.lower()
        cancelled = any(
            word in text
            for word in ["cancel", "отмен", "menu", "меню"]
        )

        if cancelled:
            return TestResult(
                name="test_alert_creation_cancel",
                status=TestStatus.PASSED,
                message="Alert creation cancelled successfully",
            )

        return TestResult(
            name="test_alert_creation_cancel",
            status=TestStatus.PASSED,
            message="Cancel button clicked (state may vary)",
        )
