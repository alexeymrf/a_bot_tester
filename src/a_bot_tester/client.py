"""Telethon client wrapper for bot testing."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

from telethon import TelegramClient
from telethon.tl.types import Message

from .config import Config

logger = logging.getLogger(__name__)


class BotTesterClient:
    """Telethon client wrapper for testing Telegram bots."""

    def __init__(self, config: Config) -> None:
        """Initialize the tester client.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.client = TelegramClient(
            config.session_name,
            config.api_id,
            config.api_hash,
        )
        self._target_entity: Any = None

    async def start(self) -> None:
        """Start the Telethon client and authenticate."""
        await self.client.start(phone=self.config.phone)
        logger.info("Telegram client started successfully")
        
        # Resolve target bot
        self._target_entity = await self.client.get_entity(
            f"@{self.config.target_bot_username}"
        )
        logger.info(f"Target bot resolved: @{self.config.target_bot_username}")

    async def stop(self) -> None:
        """Stop the Telethon client."""
        await self.client.disconnect()
        logger.info("Telegram client disconnected")

    async def send_command(
        self,
        command: str,
        timeout: int | None = None,
    ) -> list[Message]:
        """Send a command to the target bot and collect responses.
        
        Args:
            command: Command to send (e.g., '/start', '/help')
            timeout: Timeout in seconds to wait for responses
            
        Returns:
            List of response messages from the bot
        """
        if not self._target_entity:
            raise RuntimeError("Client not started. Call start() first.")

        timeout = timeout or self.config.response_timeout
        
        # Record time before sending
        before_send = datetime.now()
        
        # Send the command
        await self.client.send_message(self._target_entity, command)
        logger.info(f"Sent command: {command}")
        
        # Collect responses
        responses: list[Message] = []
        end_time = datetime.now() + timedelta(seconds=timeout)
        
        # Wait a bit for initial response
        await asyncio.sleep(0.5)
        
        while datetime.now() < end_time:
            # Get recent messages from the bot
            messages = await self.client.get_messages(
                self._target_entity,
                limit=10,
            )
            
            # Filter messages that are from the bot and after our command
            new_messages = [
                msg for msg in messages
                if msg.date.replace(tzinfo=None) > before_send
                and msg.out is False  # Message is not from us
            ]
            
            if new_messages:
                # Check if we got new messages since last check
                new_count = len(new_messages) - len(responses)
                if new_count > 0:
                    responses = new_messages
                    # Wait a bit more for additional messages
                    await asyncio.sleep(0.5)
                else:
                    # No new messages, we might be done
                    break
            else:
                await asyncio.sleep(0.3)
        
        logger.info(f"Received {len(responses)} response(s) for command: {command}")
        return responses

    async def send_message(self, text: str) -> None:
        """Send a plain text message to the target bot.
        
        Args:
            text: Text message to send
        """
        if not self._target_entity:
            raise RuntimeError("Client not started. Call start() first.")
            
        await self.client.send_message(self._target_entity, text)
        logger.info(f"Sent message: {text[:50]}...")

    async def click_inline_button(
        self,
        message: Message,
        button_text: str | None = None,
        button_data: bytes | None = None,
        row: int | None = None,
        col: int | None = None,
    ) -> Message | None:
        """Click an inline button in a message.
        
        Args:
            message: Message containing the inline keyboard
            button_text: Text of the button to click
            button_data: Data of the button to click
            row: Row index of the button (0-based)
            col: Column index of the button (0-based)
            
        Returns:
            Response message or None if no response
        """
        if not message.buttons:
            logger.warning("Message has no inline buttons")
            return None
            
        # Find the button
        target_button = None
        
        if row is not None and col is not None:
            try:
                target_button = message.buttons[row][col]
            except IndexError:
                logger.error(f"Button at row={row}, col={col} not found")
                return None
        elif button_text:
            for btn_row in message.buttons:
                for btn in btn_row:
                    if btn.text == button_text:
                        target_button = btn
                        break
                if target_button:
                    break
        elif button_data:
            for btn_row in message.buttons:
                for btn in btn_row:
                    if hasattr(btn, "data") and btn.data == button_data:
                        target_button = btn
                        break
                if target_button:
                    break
        
        if not target_button:
            logger.error("Target button not found")
            return None
        
        # Click the button
        before_click = datetime.now()
        await target_button.click()
        logger.info(f"Clicked button: {target_button.text}")
        
        # Wait for response
        await asyncio.sleep(1)
        
        # Get response
        messages = await self.client.get_messages(
            self._target_entity,
            limit=5,
        )
        
        for msg in messages:
            if msg.date.replace(tzinfo=None) > before_click and not msg.out:
                return msg
                
        return None

    async def __aenter__(self) -> "BotTesterClient":
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.stop()
