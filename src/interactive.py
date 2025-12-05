"""
Interactive testing mode for manual bot exploration.
"""

import asyncio

from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from .client import BotTesterClient
from .config import get_settings
from .utils.logging import setup_logging, get_logger

logger = get_logger(__name__)


class InteractiveSession:
    """Interactive testing session."""

    def __init__(self, client: BotTesterClient) -> None:
        """Initialize interactive session."""
        self.client = client
        self.console = Console()
        self.running = True

    async def run(self) -> None:
        """Run interactive session."""
        self.console.print("\n[bold cyan]🎮 Interactive Mode[/bold cyan]")
        self.console.print("Commands: /cmd <command>, /click <text>, /buttons, /text, /help, /quit\n")

        while self.running:
            try:
                user_input = Prompt.ask("[cyan]>[/cyan]")
                await self.handle_input(user_input)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")

    async def handle_input(self, user_input: str) -> None:
        """Handle user input."""
        if not user_input:
            return

        parts = user_input.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd == "/quit" or cmd == "/q":
            self.running = False
            self.console.print("[yellow]Goodbye![/yellow]")

        elif cmd == "/help" or cmd == "/h":
            self.show_help()

        elif cmd == "/cmd" or cmd == "/c":
            if not arg:
                self.console.print("[yellow]Usage: /cmd <command>[/yellow]")
                return
            await self.send_command(arg if arg.startswith("/") else f"/{arg}")

        elif cmd == "/click" or cmd == "/k":
            if not arg:
                self.console.print("[yellow]Usage: /click <button_text>[/yellow]")
                return
            await self.click_button(arg)

        elif cmd == "/buttons" or cmd == "/b":
            self.show_buttons()

        elif cmd == "/text" or cmd == "/t":
            self.show_text()

        elif cmd == "/msg" or cmd == "/m":
            if not arg:
                self.console.print("[yellow]Usage: /msg <text>[/yellow]")
                return
            await self.send_message(arg)

        elif cmd.startswith("/"):
            # Treat as bot command
            await self.send_command(user_input)

        else:
            # Treat as message
            await self.send_message(user_input)

    def show_help(self) -> None:
        """Show help."""
        table = Table(title="Commands", box=box.ROUNDED)
        table.add_column("Command", style="cyan")
        table.add_column("Description")

        table.add_row("/cmd <command>", "Send command to bot (e.g., /cmd start)")
        table.add_row("/click <text>", "Click button by text")
        table.add_row("/buttons", "Show available buttons")
        table.add_row("/text", "Show last message text")
        table.add_row("/msg <text>", "Send text message")
        table.add_row("/help", "Show this help")
        table.add_row("/quit", "Exit interactive mode")

        self.console.print(table)

    async def send_command(self, command: str) -> None:
        """Send command to bot."""
        self.console.print(f"[dim]Sending: {command}[/dim]")
        response = await self.client.send_command(command)

        if response:
            self.console.print(f"\n[green]Response:[/green]")
            self.console.print(response.text or "<no text>")
            self.show_buttons()
        else:
            self.console.print("[yellow]No response received[/yellow]")

    async def send_message(self, text: str) -> None:
        """Send message to bot."""
        self.console.print(f"[dim]Sending: {text}[/dim]")
        response = await self.client.send_message(text)

        if response:
            self.console.print(f"\n[green]Response:[/green]")
            self.console.print(response.text or "<no text>")
            self.show_buttons()
        else:
            self.console.print("[yellow]No response received[/yellow]")

    async def click_button(self, text: str) -> None:
        """Click button by text."""
        try:
            self.console.print(f"[dim]Clicking: {text}[/dim]")
            response = await self.client.click_button(button_text=text)

            if response:
                self.console.print(f"\n[green]Response:[/green]")
                self.console.print(response.text or "<no text>")
                self.show_buttons()
            else:
                self.console.print("[yellow]No response received[/yellow]")
        except ValueError as e:
            self.console.print(f"[red]{str(e)}[/red]")

    def show_buttons(self) -> None:
        """Show available buttons."""
        buttons = self.client.get_buttons()
        if not buttons:
            return

        self.console.print("\n[cyan]Buttons:[/cyan]")
        for i, btn in enumerate(buttons):
            self.console.print(f"  [{i}] {btn['text']} ({btn['data']})")

    def show_text(self) -> None:
        """Show last message text."""
        text = self.client.last_text
        if text:
            self.console.print(f"\n[green]Last message:[/green]")
            self.console.print(text)
        else:
            self.console.print("[yellow]No message[/yellow]")


async def main_async() -> None:
    """Async main function."""
    setup_logging("INFO")
    settings = get_settings()
    console = Console()

    console.print(f"\n[bold cyan]🎮 a_bot Interactive Tester[/bold cyan]")
    console.print(f"Target bot: @{settings.target_bot_username}")

    client = BotTesterClient(settings)

    try:
        await client.start()
        session = InteractiveSession(client)
        await session.run()
    finally:
        await client.stop()


def main() -> None:
    """Main entry point."""
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
