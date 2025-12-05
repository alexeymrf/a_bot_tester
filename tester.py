#!/usr/bin/env python3
"""
Telegram Bot Tester using Telethon.

This script automates testing of Telegram bot commands by sending
messages from a user account and verifying responses.

Usage:
    python tester.py --all           # Test all commands
    python tester.py --command /start # Test specific command
    python tester.py --interactive   # Interactive mode
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Message

load_dotenv()

# Configuration
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
BOT_USERNAME = os.getenv("BOT_USERNAME", "@your_bot")
SESSION_NAME = os.getenv("SESSION_NAME", "a_bot_tester")


# Test cases for a_bot commands
TEST_CASES = {
    "/start": {
        "description": "Start command - should show welcome message",
        "expected_contains": ["Funding Rate", "Welcome", "menu", "help"],
        "timeout": 10,
    },
    "/help": {
        "description": "Help command - should show available commands",
        "expected_contains": ["help", "command", "/"],
        "timeout": 10,
    },
    "/spreads": {
        "description": "Spreads command - should show top spreads",
        "expected_contains": ["spread", "%"],
        "timeout": 30,
    },
    "/rates": {
        "description": "Rates command - should show funding rates",
        "expected_contains": ["rate", "funding", "%"],
        "timeout": 30,
    },
    "/exchanges": {
        "description": "Exchanges command - should show exchange list",
        "expected_contains": ["exchange", "bybit", "mexc"],
        "timeout": 15,
    },
    "/alerts": {
        "description": "Alerts command - should show user alerts",
        "expected_contains": ["alert"],
        "timeout": 15,
    },
    "/settings": {
        "description": "Settings command - should show user settings",
        "expected_contains": ["settings", "notification"],
        "timeout": 15,
    },
    "/status": {
        "description": "Status command - should show system status",
        "expected_contains": ["status", "running", "online"],
        "timeout": 15,
    },
}


class BotTester:
    """Telegram bot tester using Telethon."""

    def __init__(self, api_id: str, api_hash: str, session_name: str):
        """Initialize the tester."""
        self.client = TelegramClient(session_name, int(api_id), api_hash)
        self.results: list[dict[str, Any]] = []

    async def start(self) -> None:
        """Start the Telethon client."""
        await self.client.start()
        print(f"✅ Connected as: {(await self.client.get_me()).username}")

    async def stop(self) -> None:
        """Stop the Telethon client."""
        await self.client.disconnect()

    async def send_command(
        self,
        bot_username: str,
        command: str,
        timeout: int = 30,
    ) -> list[Message]:
        """Send a command to the bot and wait for response."""
        # Resolve bot entity
        bot = await self.client.get_entity(bot_username)

        # Send the command
        await self.client.send_message(bot, command)
        print(f"📤 Sent: {command}")

        # Wait for response(s)
        await asyncio.sleep(2)  # Initial wait

        # Get recent messages from bot
        messages = []
        async for message in self.client.iter_messages(
            bot,
            limit=5,
            from_user=bot,
        ):
            # Only include messages after our command
            messages.append(message)

        return messages[::-1]  # Reverse to get chronological order

    async def test_command(
        self,
        bot_username: str,
        command: str,
        test_case: dict[str, Any],
    ) -> dict[str, Any]:
        """Test a single command."""
        result = {
            "command": command,
            "description": test_case.get("description", ""),
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "responses": [],
            "errors": [],
        }

        try:
            timeout = test_case.get("timeout", 30)
            messages = await self.send_command(bot_username, command, timeout)

            if not messages:
                result["errors"].append("No response received")
                return result

            # Extract response texts
            responses = []
            for msg in messages:
                if msg.text:
                    responses.append(msg.text)
                elif msg.message:
                    responses.append(msg.message)

            result["responses"] = responses

            # Check expected content
            expected = test_case.get("expected_contains", [])
            all_text = " ".join(responses).lower()

            matched = []
            missing = []
            for keyword in expected:
                if keyword.lower() in all_text:
                    matched.append(keyword)
                else:
                    missing.append(keyword)

            if missing:
                result["errors"].append(f"Missing keywords: {missing}")
            else:
                result["success"] = True

            result["matched_keywords"] = matched
            result["missing_keywords"] = missing

        except Exception as e:
            result["errors"].append(str(e))

        return result

    async def run_all_tests(self, bot_username: str) -> list[dict[str, Any]]:
        """Run all test cases."""
        results = []

        for command, test_case in TEST_CASES.items():
            print(f"\n🧪 Testing: {command}")
            print(f"   {test_case.get('description', '')}")

            result = await self.test_command(bot_username, command, test_case)
            results.append(result)

            if result["success"]:
                print(f"   ✅ PASSED")
            else:
                print(f"   ❌ FAILED: {result['errors']}")

            # Delay between tests to avoid rate limiting
            await asyncio.sleep(3)

        return results

    async def interactive_mode(self, bot_username: str) -> None:
        """Interactive testing mode."""
        print(f"\n🔄 Interactive mode - Send commands to {bot_username}")
        print("   Type 'quit' to exit\n")

        while True:
            try:
                command = input("Command> ").strip()
                if command.lower() in ["quit", "exit", "q"]:
                    break

                if not command:
                    continue

                messages = await self.send_command(bot_username, command)

                print("\n📥 Response(s):")
                for msg in messages:
                    text = msg.text or msg.message or "[No text]"
                    print(f"   {text[:200]}...")
                print()

            except KeyboardInterrupt:
                break

    def print_summary(self, results: list[dict[str, Any]]) -> None:
        """Print test summary."""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in results if r["success"])
        failed = len(results) - passed

        for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['command']}: {result['description']}")
            if not result["success"] and result["errors"]:
                for error in result["errors"]:
                    print(f"   └── {error}")

        print("\n" + "-" * 60)
        print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
        print("=" * 60)


async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Telegram Bot Tester")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--command", type=str, help="Test specific command")
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument(
        "--bot", type=str, default=BOT_USERNAME, help="Bot username to test"
    )
    args = parser.parse_args()

    # Validate configuration
    if not API_ID or not API_HASH:
        print("❌ Error: TELEGRAM_API_ID and TELEGRAM_API_HASH must be set")
        print("   Get them from https://my.telegram.org/apps")
        sys.exit(1)

    tester = BotTester(API_ID, API_HASH, SESSION_NAME)

    try:
        await tester.start()

        if args.interactive:
            await tester.interactive_mode(args.bot)
        elif args.command:
            # Test single command
            test_case = TEST_CASES.get(args.command, {"description": "Custom command"})
            result = await tester.test_command(args.bot, args.command, test_case)
            tester.print_summary([result])
        elif args.all:
            # Run all tests
            results = await tester.run_all_tests(args.bot)
            tester.print_summary(results)
        else:
            # Default: run all tests
            results = await tester.run_all_tests(args.bot)
            tester.print_summary(results)

    finally:
        await tester.stop()


if __name__ == "__main__":
    asyncio.run(main())
