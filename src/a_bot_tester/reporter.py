"""Test report generation."""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """Result of a single test."""
    
    test_name: str
    scenario_name: str
    passed: bool
    duration_ms: float
    command: str
    validation_results: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    response_preview: str | None = None
    skipped: bool = False
    skip_reason: str = ""


@dataclass
class ScenarioResult:
    """Result of a test scenario."""
    
    name: str
    passed: bool
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    duration_ms: float
    test_results: list[TestResult] = field(default_factory=list)


@dataclass
class TestReport:
    """Complete test report."""
    
    timestamp: str
    total_scenarios: int
    passed_scenarios: int
    failed_scenarios: int
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    total_duration_ms: float
    scenario_results: list[ScenarioResult] = field(default_factory=list)


class TestReporter:
    """Generates and saves test reports."""
    
    def __init__(self) -> None:
        """Initialize the reporter."""
        self._start_time: datetime | None = None
        self._scenario_results: list[ScenarioResult] = []
        self._current_scenario: str | None = None
        self._current_tests: list[TestResult] = []
        self._scenario_start: datetime | None = None
    
    def start_run(self) -> None:
        """Mark the start of a test run."""
        self._start_time = datetime.now()
        self._scenario_results = []
        logger.info("Test run started")
    
    def start_scenario(self, name: str) -> None:
        """Mark the start of a scenario.
        
        Args:
            name: Scenario name
        """
        self._current_scenario = name
        self._current_tests = []
        self._scenario_start = datetime.now()
        logger.info(f"Starting scenario: {name}")
    
    def add_test_result(self, result: TestResult) -> None:
        """Add a test result.
        
        Args:
            result: Test result to add
        """
        self._current_tests.append(result)
        status = "PASS" if result.passed else ("SKIP" if result.skipped else "FAIL")
        logger.info(f"  [{status}] {result.test_name} ({result.duration_ms:.0f}ms)")
        
        if not result.passed and not result.skipped and result.error:
            logger.error(f"    Error: {result.error}")
    
    def end_scenario(self) -> ScenarioResult:
        """Mark the end of a scenario and return results.
        
        Returns:
            Scenario result
        """
        if not self._current_scenario or not self._scenario_start:
            raise RuntimeError("No scenario in progress")
        
        duration = (datetime.now() - self._scenario_start).total_seconds() * 1000
        
        passed = sum(1 for t in self._current_tests if t.passed)
        failed = sum(1 for t in self._current_tests if not t.passed and not t.skipped)
        skipped = sum(1 for t in self._current_tests if t.skipped)
        
        result = ScenarioResult(
            name=self._current_scenario,
            passed=failed == 0,
            total_tests=len(self._current_tests),
            passed_tests=passed,
            failed_tests=failed,
            skipped_tests=skipped,
            duration_ms=duration,
            test_results=self._current_tests.copy(),
        )
        
        self._scenario_results.append(result)
        
        status = "PASSED" if result.passed else "FAILED"
        logger.info(
            f"Scenario '{result.name}' {status}: "
            f"{passed}/{result.total_tests} passed, {skipped} skipped"
        )
        
        return result
    
    def generate_report(self) -> TestReport:
        """Generate the final test report.
        
        Returns:
            Complete test report
        """
        if not self._start_time:
            raise RuntimeError("Test run not started")
        
        total_duration = (datetime.now() - self._start_time).total_seconds() * 1000
        
        total_tests = sum(s.total_tests for s in self._scenario_results)
        passed_tests = sum(s.passed_tests for s in self._scenario_results)
        failed_tests = sum(s.failed_tests for s in self._scenario_results)
        skipped_tests = sum(s.skipped_tests for s in self._scenario_results)
        
        passed_scenarios = sum(1 for s in self._scenario_results if s.passed)
        
        report = TestReport(
            timestamp=self._start_time.isoformat(),
            total_scenarios=len(self._scenario_results),
            passed_scenarios=passed_scenarios,
            failed_scenarios=len(self._scenario_results) - passed_scenarios,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            skipped_tests=skipped_tests,
            total_duration_ms=total_duration,
            scenario_results=self._scenario_results,
        )
        
        logger.info("=" * 60)
        logger.info("TEST RUN SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Scenarios: {passed_scenarios}/{report.total_scenarios} passed")
        logger.info(f"Tests: {passed_tests}/{total_tests} passed, {skipped_tests} skipped")
        logger.info(f"Duration: {total_duration:.0f}ms")
        logger.info("=" * 60)
        
        return report
    
    def save_report(
        self,
        report: TestReport,
        output_path: Path,
        format: str = "json",
    ) -> None:
        """Save the report to a file.
        
        Args:
            report: Report to save
            output_path: Output file path
            format: Output format ('json' or 'text')
        """
        if format == "json":
            with open(output_path, "w") as f:
                json.dump(asdict(report), f, indent=2)
        elif format == "text":
            with open(output_path, "w") as f:
                f.write(self._format_text_report(report))
        else:
            raise ValueError(f"Unknown format: {format}")
        
        logger.info(f"Report saved to {output_path}")
    
    def _format_text_report(self, report: TestReport) -> str:
        """Format report as text.
        
        Args:
            report: Report to format
            
        Returns:
            Formatted text report
        """
        lines = [
            "=" * 60,
            "TEST REPORT",
            f"Generated: {report.timestamp}",
            "=" * 60,
            "",
            f"Total Scenarios: {report.total_scenarios}",
            f"  Passed: {report.passed_scenarios}",
            f"  Failed: {report.failed_scenarios}",
            "",
            f"Total Tests: {report.total_tests}",
            f"  Passed: {report.passed_tests}",
            f"  Failed: {report.failed_tests}",
            f"  Skipped: {report.skipped_tests}",
            "",
            f"Total Duration: {report.total_duration_ms:.0f}ms",
            "",
            "-" * 60,
            "DETAILED RESULTS",
            "-" * 60,
        ]
        
        for scenario in report.scenario_results:
            status = "PASSED" if scenario.passed else "FAILED"
            lines.append(f"\nScenario: {scenario.name} [{status}]")
            lines.append(f"  Tests: {scenario.passed_tests}/{scenario.total_tests} passed")
            
            for test in scenario.test_results:
                if test.skipped:
                    status = "SKIP"
                elif test.passed:
                    status = "PASS"
                else:
                    status = "FAIL"
                lines.append(f"  [{status}] {test.test_name} ({test.duration_ms:.0f}ms)")
                
                if test.error:
                    lines.append(f"         Error: {test.error}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)
