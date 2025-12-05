"""
Main entry point for the bot tester.
"""

import argparse
import asyncio
import sys

from rich.console import Console

from .client import BotTesterClient
from .config import get_settings
from .tester import BotTester, TestSuite, run_quick_test
from .utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


async def main_async(args: argparse.Namespace) -> int:
    """
    Async main function.

    Args:
        args: Command line arguments.

    Returns:
        Exit code.
    """
    console = Console()
    settings = get_settings()

    # Override bot username if provided
    if args.bot_username:
        settings.target_bot_username = args.bot_username

    console.print(f"\n[bold cyan]🤖 a_bot Tester[/bold cyan]")
    console.print(f"Target bot: @{settings.target_bot_username}")
    console.print()

    client = BotTesterClient(settings)

    try:
        await client.start()

        if args.quick:
            success = await run_quick_test(client)
            return 0 if success else 1

        # Run full tests
        tester = BotTester(client)

        suite = TestSuite(args.test) if args.test else TestSuite.ALL
        report = await tester.run(suite=suite, verbose=not args.quiet)

        # Exit code based on results
        if report.failed > 0 or report.errors > 0:
            return 1
        return 0

    except Exception as e:
        console.print(f"\n[bold red]❌ Error: {str(e)}[/bold red]")
        logger.exception("Main error")
        return 1

    finally:
        await client.stop()


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Automated testing tool for a_bot Telegram bot"
    )
    parser.add_argument(
        "--bot-username",
        "-b",
        help="Bot username to test (without @)",
    )
    parser.add_argument(
        "--test",
        "-t",
        choices=["all", "commands", "callbacks", "flows"],
        default="all",
        help="Test suite to run",
    )
    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Run quick sanity test only",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress detailed output",
    )
    parser.add_argument(
        "--log-level",
        "-l",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Log level",
    )

    args = parser.parse_args()

    setup_logging(args.log_level)

    exit_code = asyncio.run(main_async(args))
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
