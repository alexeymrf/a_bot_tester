"""
Authentication helper for first-time setup.
"""

import asyncio

from telethon import TelegramClient
from rich.console import Console
from rich.prompt import Prompt

from .config import get_settings
from .utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


async def authenticate() -> None:
    """
    Authenticate with Telegram and create session.
    """
    console = Console()
    setup_logging("INFO")

    console.print("\n[bold cyan]🔐 Telegram Authentication Setup[/bold cyan]\n")

    settings = get_settings()

    console.print(f"Session name: [cyan]{settings.session_name}[/cyan]")
    console.print(f"Phone: [cyan]{settings.telegram_phone}[/cyan]")
    console.print()

    client = TelegramClient(
        settings.session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )

    await client.start(phone=settings.telegram_phone)

    me = await client.get_me()
    console.print(f"\n[bold green]✅ Authenticated as:[/bold green]")
    console.print(f"   Name: {me.first_name} {me.last_name or ''}")
    console.print(f"   Username: @{me.username or 'N/A'}")
    console.print(f"   ID: {me.id}")

    # Verify bot access
    try:
        bot = await client.get_entity(settings.target_bot_username)
        console.print(f"\n[bold green]✅ Bot found:[/bold green]")
        console.print(f"   Username: @{bot.username}")
        console.print(f"   ID: {bot.id}")
    except Exception as e:
        console.print(f"\n[yellow]⚠️ Could not find bot @{settings.target_bot_username}[/yellow]")
        console.print(f"   Error: {str(e)}")
        console.print("   Make sure the bot username is correct and you have chatted with it.")

    await client.disconnect()

    console.print(f"\n[bold green]✅ Session saved to '{settings.session_name}.session'[/bold green]")
    console.print("\nYou can now run tests with:")
    console.print(f"  [cyan]python -m src.main[/cyan]")


def main() -> None:
    """Entry point for authentication."""
    asyncio.run(authenticate())


if __name__ == "__main__":
    main()
