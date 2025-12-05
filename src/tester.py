"""
Test orchestrator for running all bot tests.
"""

import asyncio
from enum import Enum
from typing import TYPE_CHECKING

from rich.console import Console

from .tests import CommandTests, CallbackTests, FlowTests
from .utils.report import TestReport
from .utils.logging import get_logger

if TYPE_CHECKING:
    from .client import BotTesterClient

logger = get_logger(__name__)


class TestSuite(str, Enum):
    """Available test suites."""

    ALL = "all"
    COMMANDS = "commands"
    CALLBACKS = "callbacks"
    FLOWS = "flows"


class BotTester:
    """
    Test orchestrator for running bot tests.
    """

    def __init__(self, client: "BotTesterClient") -> None:
        """
        Initialize the tester.

        Args:
            client: Bot tester client.
        """
        self.client = client
        self.console = Console()

    async def run(
        self,
        suite: TestSuite = TestSuite.ALL,
        verbose: bool = True,
    ) -> TestReport:
        """
        Run tests.

        Args:
            suite: Test suite to run.
            verbose: Print detailed output.

        Returns:
            Test report.
        """
        report = TestReport()

        self.console.print("\n[bold cyan]🤖 Starting a_bot Test Suite[/bold cyan]\n")

        suites_to_run = []

        if suite in (TestSuite.ALL, TestSuite.COMMANDS):
            suites_to_run.append(("Commands", CommandTests(self.client)))

        if suite in (TestSuite.ALL, TestSuite.CALLBACKS):
            suites_to_run.append(("Callbacks", CallbackTests(self.client)))

        if suite in (TestSuite.ALL, TestSuite.FLOWS):
            suites_to_run.append(("Flows", FlowTests(self.client)))

        for suite_name, test_suite in suites_to_run:
            self.console.print(f"\n[bold yellow]📋 Running {suite_name} Tests[/bold yellow]")

            try:
                results = await test_suite.run_all()
                for result in results:
                    report.add_result(result)

                    # Print individual result
                    if result.passed:
                        self.console.print(f"  ✅ {result.name} ({result.duration_ms:.0f}ms)")
                    else:
                        self.console.print(
                            f"  ❌ {result.name}: {result.message} ({result.duration_ms:.0f}ms)"
                        )

            except Exception as e:
                logger.error("Suite error", suite=suite_name, error=str(e))
                self.console.print(f"  💥 Suite error: {str(e)}")

        report.finish()

        if verbose:
            self.console.print("\n")
            report.print_detailed(self.console)

        return report


async def run_quick_test(client: "BotTesterClient") -> bool:
    """
    Run a quick sanity test.

    Args:
        client: Bot tester client.

    Returns:
        True if basic functionality works.
    """
    console = Console()
    console.print("\n[bold cyan]🔧 Running Quick Test[/bold cyan]\n")

    try:
        # Test /start
        response = await client.send_command("/start")
        if response is None:
            console.print("❌ No response to /start")
            return False

        console.print("✅ Bot responds to /start")

        # Check for buttons
        buttons = client.get_buttons()
        if buttons:
            console.print(f"✅ Menu has {len(buttons)} buttons")
        else:
            console.print("⚠️ No inline buttons found")

        console.print("\n[bold green]Quick test passed![/bold green]")
        return True

    except Exception as e:
        console.print(f"❌ Error: {str(e)}")
        return False
