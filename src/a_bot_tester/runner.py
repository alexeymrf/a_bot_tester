"""Test runner for executing test scenarios."""

import argparse
import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path

from .client import BotTesterClient
from .config import Config
from .reporter import TestReporter, TestResult
from .scenario import TestScenario, load_all_scenarios, load_scenario
from .validator import create_validators_from_config

logger = logging.getLogger(__name__)


class TestRunner:
    """Runs test scenarios against a Telegram bot."""
    
    def __init__(
        self,
        client: BotTesterClient,
        reporter: TestReporter | None = None,
    ) -> None:
        """Initialize the test runner.
        
        Args:
            client: Telethon client wrapper
            reporter: Optional test reporter
        """
        self.client = client
        self.reporter = reporter or TestReporter()
    
    async def run_scenario(self, scenario: TestScenario) -> None:
        """Run a single test scenario.
        
        Args:
            scenario: Scenario to run
        """
        self.reporter.start_scenario(scenario.name)
        
        # Run setup commands
        for cmd in scenario.setup_commands:
            logger.info(f"Running setup command: {cmd}")
            await self.client.send_command(cmd, timeout=5)
            await asyncio.sleep(1)
        
        # Run tests
        for test in scenario.tests:
            result = await self._run_test(test, scenario.name)
            self.reporter.add_test_result(result)
            await asyncio.sleep(0.5)  # Small delay between tests
        
        # Run teardown commands
        for cmd in scenario.teardown_commands:
            logger.info(f"Running teardown command: {cmd}")
            await self.client.send_command(cmd, timeout=5)
            await asyncio.sleep(1)
        
        self.reporter.end_scenario()
    
    async def _run_test(self, test: "TestCase", scenario_name: str) -> TestResult:
        """Run a single test case.
        
        Args:
            test: Test case to run
            scenario_name: Name of the parent scenario
            
        Returns:
            Test result
        """
        from .scenario import TestCase  # Import here to avoid circular import
        
        if test.skip:
            return TestResult(
                test_name=test.name,
                scenario_name=scenario_name,
                passed=False,
                duration_ms=0,
                command=test.command,
                skipped=True,
                skip_reason=test.skip_reason,
            )
        
        start_time = datetime.now()
        
        try:
            # Send command and get responses
            responses = await self.client.send_command(
                test.command,
                timeout=test.timeout,
            )
            
            # Validate responses
            validators = create_validators_from_config(test.expected)
            validation_results = []
            all_passed = True
            
            if not responses and test.expected:
                all_passed = False
                validation_results.append({
                    "passed": False,
                    "message": "No response received from bot",
                })
            else:
                for validator in validators:
                    result = validator.validate(responses)
                    validation_results.append({
                        "passed": result.passed,
                        "message": result.message,
                        "details": result.details,
                    })
                    if not result.passed:
                        all_passed = False
            
            # Create response preview
            response_preview = None
            if responses:
                preview_parts = []
                for msg in responses[:3]:  # Limit to 3 messages
                    if msg.text:
                        preview_parts.append(msg.text[:100])
                response_preview = " | ".join(preview_parts)
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return TestResult(
                test_name=test.name,
                scenario_name=scenario_name,
                passed=all_passed,
                duration_ms=duration,
                command=test.command,
                validation_results=validation_results,
                response_preview=response_preview,
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            logger.exception(f"Error running test '{test.name}'")
            
            return TestResult(
                test_name=test.name,
                scenario_name=scenario_name,
                passed=False,
                duration_ms=duration,
                command=test.command,
                error=str(e),
            )
    
    async def run_all(self, scenarios: list[TestScenario]) -> None:
        """Run all test scenarios.
        
        Args:
            scenarios: List of scenarios to run
        """
        self.reporter.start_run()
        
        for scenario in scenarios:
            await self.run_scenario(scenario)
        
        self.reporter.generate_report()


async def main() -> int:
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="A_Bot Tester - Telegram Bot Testing Tool")
    parser.add_argument(
        "--scenario",
        "-s",
        help="Specific scenario file to run",
    )
    parser.add_argument(
        "--scenarios-dir",
        "-d",
        default="scenarios",
        help="Directory containing scenario files (default: scenarios)",
    )
    parser.add_argument(
        "--output",
        "-o",
        help="Output file for test report",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text"],
        default="json",
        help="Report format (default: json)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    try:
        config = Config.from_env()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    
    # Load scenarios
    if args.scenario:
        scenario_path = Path(args.scenario)
        if not scenario_path.exists():
            logger.error(f"Scenario file not found: {scenario_path}")
            return 1
        scenarios = [load_scenario(scenario_path)]
    else:
        scenarios_dir = Path(args.scenarios_dir)
        if not scenarios_dir.exists():
            logger.error(f"Scenarios directory not found: {scenarios_dir}")
            return 1
        scenarios = load_all_scenarios(scenarios_dir)
    
    if not scenarios:
        logger.error("No scenarios found to run")
        return 1
    
    logger.info(f"Loaded {len(scenarios)} scenario(s)")
    
    # Run tests
    reporter = TestReporter()
    
    async with BotTesterClient(config) as client:
        runner = TestRunner(client, reporter)
        await runner.run_all(scenarios)
    
    # Save report
    if args.output:
        report = reporter.generate_report()
        reporter.save_report(report, Path(args.output), args.format)
    
    # Return exit code based on results
    report = reporter.generate_report()
    return 0 if report.failed_tests == 0 else 1


def run() -> None:
    """Entry point for the command line."""
    sys.exit(asyncio.run(main()))


if __name__ == "__main__":
    run()
