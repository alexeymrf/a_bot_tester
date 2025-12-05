"""
Base test class for bot testing.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..utils.report import TestResult, TestStatus
from ..utils.logging import get_logger

if TYPE_CHECKING:
    from ..client import BotTesterClient

logger = get_logger(__name__)


class BaseTest(ABC):
    """Base class for test suites."""

    def __init__(self, client: "BotTesterClient") -> None:
        """
        Initialize the test suite.

        Args:
            client: Bot tester client.
        """
        self.client = client
        self.results: list[TestResult] = []

    @abstractmethod
    async def run_all(self) -> list[TestResult]:
        """
        Run all tests in the suite.

        Returns:
            List of test results.
        """
        pass

    async def run_test(
        self,
        name: str,
        test_func,
        *args,
        **kwargs,
    ) -> TestResult:
        """
        Run a single test with timing and error handling.

        Args:
            name: Test name.
            test_func: Test function to run.
            *args: Arguments for test function.
            **kwargs: Keyword arguments for test function.

        Returns:
            Test result.
        """
        start_time = time.time()
        logger.info("Running test", test_name=name)

        try:
            result = await test_func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000

            if isinstance(result, TestResult):
                result.duration_ms = duration_ms
                return result

            # Test function returned True/False
            if result:
                return TestResult(
                    name=name,
                    status=TestStatus.PASSED,
                    duration_ms=duration_ms,
                    message="Test passed",
                )
            else:
                return TestResult(
                    name=name,
                    status=TestStatus.FAILED,
                    duration_ms=duration_ms,
                    message="Test assertion failed",
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error("Test error", test_name=name, error=str(e))
            return TestResult(
                name=name,
                status=TestStatus.ERROR,
                duration_ms=duration_ms,
                message=str(e),
            )

    def assert_text_contains(
        self,
        text: str,
        substring: str,
        message: str = "",
    ) -> bool:
        """
        Assert text contains substring.

        Args:
            text: Text to check.
            substring: Expected substring.
            message: Optional message on failure.

        Returns:
            True if assertion passes.

        Raises:
            AssertionError: If assertion fails.
        """
        if substring.lower() not in text.lower():
            raise AssertionError(
                message or f"Expected '{substring}' in text, but got: {text[:200]}"
            )
        return True

    def assert_has_button(
        self,
        text: str | None = None,
        data_contains: str | None = None,
        message: str = "",
    ) -> bool:
        """
        Assert message has a button.

        Args:
            text: Expected button text.
            data_contains: Expected substring in button data.
            message: Optional message on failure.

        Returns:
            True if assertion passes.

        Raises:
            AssertionError: If assertion fails.
        """
        if not self.client.has_button(text=text, data_contains=data_contains):
            buttons = self.client.get_buttons()
            raise AssertionError(
                message or f"Expected button with text='{text}' or data containing '{data_contains}'. "
                f"Available buttons: {buttons}"
            )
        return True

    def assert_response_received(self, message: str = "") -> bool:
        """
        Assert that a response was received.

        Args:
            message: Optional message on failure.

        Returns:
            True if assertion passes.

        Raises:
            AssertionError: If no response received.
        """
        if self.client.last_message is None:
            raise AssertionError(message or "No response received from bot")
        return True

    async def delay(self, seconds: float | None = None) -> None:
        """
        Delay between tests.

        Args:
            seconds: Delay in seconds.
        """
        seconds = seconds or self.client.settings.delay_between_tests
        await asyncio.sleep(seconds)
