"""
Test reporting utilities.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


class TestStatus(str, Enum):
    """Test result status."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class TestResult:
    """Individual test result."""

    name: str
    status: TestStatus
    duration_ms: float = 0.0
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def passed(self) -> bool:
        """Check if test passed."""
        return self.status == TestStatus.PASSED


@dataclass
class TestReport:
    """Aggregated test report."""

    results: list[TestResult] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)
    finished_at: datetime | None = None

    def add_result(self, result: TestResult) -> None:
        """Add a test result."""
        self.results.append(result)

    def finish(self) -> None:
        """Mark report as finished."""
        self.finished_at = datetime.now()

    @property
    def total(self) -> int:
        """Total number of tests."""
        return len(self.results)

    @property
    def passed(self) -> int:
        """Number of passed tests."""
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)

    @property
    def failed(self) -> int:
        """Number of failed tests."""
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)

    @property
    def skipped(self) -> int:
        """Number of skipped tests."""
        return sum(1 for r in self.results if r.status == TestStatus.SKIPPED)

    @property
    def errors(self) -> int:
        """Number of error tests."""
        return sum(1 for r in self.results if r.status == TestStatus.ERROR)

    @property
    def success_rate(self) -> float:
        """Success rate percentage."""
        if self.total == 0:
            return 0.0
        return (self.passed / self.total) * 100

    @property
    def total_duration_ms(self) -> float:
        """Total duration in milliseconds."""
        return sum(r.duration_ms for r in self.results)

    def print_summary(self, console: Console | None = None) -> None:
        """Print formatted test summary."""
        if console is None:
            console = Console()

        # Create summary table
        table = Table(
            title="🧪 Test Results Summary",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Metric", style="bold")
        table.add_column("Value", justify="right")

        table.add_row("Total Tests", str(self.total))
        table.add_row("✅ Passed", f"[green]{self.passed}[/green]")
        table.add_row("❌ Failed", f"[red]{self.failed}[/red]")
        table.add_row("⏭️ Skipped", f"[yellow]{self.skipped}[/yellow]")
        table.add_row("💥 Errors", f"[magenta]{self.errors}[/magenta]")
        table.add_row("📊 Success Rate", f"{self.success_rate:.1f}%")
        table.add_row("⏱️ Total Duration", f"{self.total_duration_ms:.0f}ms")

        console.print(table)

        # Print failed tests details
        failed_results = [r for r in self.results if r.status in (TestStatus.FAILED, TestStatus.ERROR)]
        if failed_results:
            console.print("\n[bold red]Failed Tests:[/bold red]")
            for result in failed_results:
                console.print(Panel(
                    f"[bold]{result.name}[/bold]\n"
                    f"Status: {result.status.value}\n"
                    f"Message: {result.message}",
                    border_style="red",
                ))

    def print_detailed(self, console: Console | None = None) -> None:
        """Print detailed test results."""
        if console is None:
            console = Console()

        table = Table(
            title="🧪 Detailed Test Results",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Test Name", style="bold")
        table.add_column("Status", justify="center", width=10)
        table.add_column("Duration", justify="right", width=10)
        table.add_column("Message", max_width=40)

        status_styles = {
            TestStatus.PASSED: "[green]✅ PASS[/green]",
            TestStatus.FAILED: "[red]❌ FAIL[/red]",
            TestStatus.SKIPPED: "[yellow]⏭️ SKIP[/yellow]",
            TestStatus.ERROR: "[magenta]💥 ERR[/magenta]",
        }

        for i, result in enumerate(self.results, 1):
            table.add_row(
                str(i),
                result.name,
                status_styles.get(result.status, result.status.value),
                f"{result.duration_ms:.0f}ms",
                result.message[:40] + "..." if len(result.message) > 40 else result.message,
            )

        console.print(table)
        console.print()
        self.print_summary(console)
