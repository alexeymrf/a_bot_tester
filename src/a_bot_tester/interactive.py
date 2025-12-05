"""Interactive mode for manual bot testing."""

import asyncio
import logging
import sys

from .client import BotTesterClient
from .config import Config

logger = logging.getLogger(__name__)


async def interactive_mode() -> None:
    """Run the tester in interactive mode."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
    
    try:
        config = Config.from_env()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set up your .env file with required variables.")
        sys.exit(1)
    
    print("=" * 60)
    print("A_Bot Tester - Interactive Mode")
    print("=" * 60)
    print(f"Target bot: @{config.target_bot_username}")
    print()
    print("Commands:")
    print("  /command     - Send a command to the bot")
    print("  !buttons     - Show buttons from last response")
    print("  !click N     - Click button N from last response")
    print("  !quit        - Exit interactive mode")
    print("=" * 60)
    print()
    
    async with BotTesterClient(config) as client:
        last_responses = []
        
        while True:
            try:
                user_input = input("You> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nExiting...")
                break
            
            if not user_input:
                continue
            
            if user_input.lower() == "!quit":
                print("Goodbye!")
                break
            
            if user_input.lower() == "!buttons":
                if not last_responses:
                    print("No previous response with buttons")
                    continue
                
                for msg in last_responses:
                    if msg.buttons:
                        print("Buttons:")
                        idx = 0
                        for row_idx, row in enumerate(msg.buttons):
                            for col_idx, btn in enumerate(row):
                                print(f"  [{idx}] {btn.text}")
                                idx += 1
                        break
                else:
                    print("No buttons in last response")
                continue
            
            if user_input.lower().startswith("!click "):
                try:
                    btn_idx = int(user_input.split()[1])
                except (IndexError, ValueError):
                    print("Usage: !click N (where N is button index)")
                    continue
                
                if not last_responses:
                    print("No previous response with buttons")
                    continue
                
                # Find button by index
                for msg in last_responses:
                    if msg.buttons:
                        idx = 0
                        for row in msg.buttons:
                            for btn in row:
                                if idx == btn_idx:
                                    print(f"Clicking button: {btn.text}")
                                    response = await client.click_inline_button(
                                        msg,
                                        button_text=btn.text,
                                    )
                                    if response:
                                        print(f"Bot> {response.text or '[no text]'}")
                                        last_responses = [response]
                                    else:
                                        print("Bot> [no response]")
                                    break
                                idx += 1
                            else:
                                continue
                            break
                        else:
                            print(f"Button {btn_idx} not found")
                        break
                continue
            
            # Send message/command to bot
            responses = await client.send_command(user_input)
            last_responses = responses
            
            if responses:
                for msg in responses:
                    text = msg.text or "[no text]"
                    print(f"Bot> {text}")
                    
                    if msg.buttons:
                        print("     [Message has inline buttons - use !buttons to see]")
            else:
                print("Bot> [no response]")


def run() -> None:
    """Entry point for interactive mode."""
    asyncio.run(interactive_mode())


if __name__ == "__main__":
    run()
