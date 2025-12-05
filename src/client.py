"""
Telethon client wrapper for bot testing.
"""

import asyncio
from datetime import datetime
from typing import Any, Callable, Coroutine

from telethon import TelegramClient
from telethon.tl.types import (
    Message,
    ReplyInlineMarkup,
    KeyboardButtonCallback,
    User,
)
from telethon.tl.functions.messages import GetBotCallbackAnswerRequest

from .config import Settings
from .utils.logging import get_logger

logger = get_logger(__name__)


class BotTesterClient:
    """
    Telethon client wrapper for testing Telegram bots.

    Provides high-level methods for sending commands, clicking buttons,
    and validating responses.
    """

    def __init__(self, settings: Settings) -> None:
        """
        Initialize the tester client.

        Args:
            settings: Application settings.
        """
        self.settings = settings
        self.client = TelegramClient(
            settings.session_name,
            settings.telegram_api_id,
            settings.telegram_api_hash,
        )
        self._bot_entity: User | None = None
        self._last_message: Message | None = None

    async def start(self) -> None:
        """Start the client and authenticate if needed."""
        await self.client.start(phone=self.settings.telegram_phone)
        logger.info("Client started successfully")

        # Resolve bot entity
        self._bot_entity = await self.client.get_entity(
            self.settings.target_bot_username
        )
        logger.info(
            "Bot resolved",
            bot_username=self.settings.target_bot_username,
            bot_id=self._bot_entity.id,
        )

    async def stop(self) -> None:
        """Stop the client."""
        await self.client.disconnect()
        logger.info("Client disconnected")

    async def send_command(
        self,
        command: str,
        wait_response: bool = True,
        timeout: float | None = None,
    ) -> Message | None:
        """
        Send a command to the bot.

        Args:
            command: Command to send (e.g., "/start").
            wait_response: Wait for bot response.
            timeout: Response timeout in seconds.

        Returns:
            Bot's response message or None.
        """
        if self._bot_entity is None:
            raise RuntimeError("Client not started. Call start() first.")

        timeout = timeout or self.settings.test_timeout

        logger.debug("Sending command", command=command)

        # Send the command
        await self.client.send_message(self._bot_entity, command)

        if not wait_response:
            return None

        # Wait for response
        await asyncio.sleep(self.settings.delay_after_command)

        response = await self._get_last_bot_message(timeout)
        self._last_message = response

        if response:
            logger.debug(
                "Received response",
                text_preview=response.text[:100] if response.text else "<no text>",
                has_buttons=bool(response.reply_markup),
            )

        return response

    async def send_message(
        self,
        text: str,
        wait_response: bool = True,
        timeout: float | None = None,
    ) -> Message | None:
        """
        Send a text message to the bot.

        Args:
            text: Message text.
            wait_response: Wait for bot response.
            timeout: Response timeout in seconds.

        Returns:
            Bot's response message or None.
        """
        if self._bot_entity is None:
            raise RuntimeError("Client not started. Call start() first.")

        timeout = timeout or self.settings.test_timeout

        logger.debug("Sending message", text=text[:50])

        await self.client.send_message(self._bot_entity, text)

        if not wait_response:
            return None

        await asyncio.sleep(self.settings.delay_after_command)

        response = await self._get_last_bot_message(timeout)
        self._last_message = response

        return response

    async def click_button(
        self,
        button_text: str | None = None,
        button_data: bytes | None = None,
        button_index: int | None = None,
        message: Message | None = None,
        timeout: float | None = None,
    ) -> Message | None:
        """
        Click an inline button.

        Args:
            button_text: Button text to find and click.
            button_data: Button callback data to match.
            button_index: Button index (row*cols + col).
            message: Message containing the button.
            timeout: Response timeout.

        Returns:
            Updated message after button click.
        """
        if self._bot_entity is None:
            raise RuntimeError("Client not started. Call start() first.")

        message = message or self._last_message
        if message is None:
            raise ValueError("No message provided and no last message available")

        timeout = timeout or self.settings.test_timeout

        # Find the button
        button = self._find_button(message, button_text, button_data, button_index)
        if button is None:
            raise ValueError(
                f"Button not found: text={button_text}, data={button_data}, index={button_index}"
            )

        logger.debug(
            "Clicking button",
            button_text=button_text,
            button_data=button.data if hasattr(button, 'data') else None,
        )

        # Click the button
        try:
            await self.client(
                GetBotCallbackAnswerRequest(
                    peer=self._bot_entity,
                    msg_id=message.id,
                    data=button.data,
                )
            )
        except Exception as e:
            # Some buttons don't return a callback answer
            logger.debug("Button click callback", error=str(e))

        await asyncio.sleep(self.settings.delay_after_command)

        # Get updated message or new message
        response = await self._get_last_bot_message(timeout)
        self._last_message = response

        return response

    async def click_button_by_position(
        self,
        row: int,
        col: int,
        message: Message | None = None,
        timeout: float | None = None,
    ) -> Message | None:
        """
        Click button by row and column position.

        Args:
            row: Row index (0-based).
            col: Column index (0-based).
            message: Message containing the button.
            timeout: Response timeout.

        Returns:
            Updated message after button click.
        """
        message = message or self._last_message
        if message is None or not isinstance(message.reply_markup, ReplyInlineMarkup):
            raise ValueError("No inline keyboard found")

        rows = message.reply_markup.rows
        if row >= len(rows):
            raise ValueError(f"Row {row} not found (max: {len(rows) - 1})")

        buttons = rows[row].buttons
        if col >= len(buttons):
            raise ValueError(f"Column {col} not found in row {row} (max: {len(buttons) - 1})")

        button = buttons[col]
        if not isinstance(button, KeyboardButtonCallback):
            raise ValueError("Button is not a callback button")

        return await self.click_button(button_data=button.data, message=message, timeout=timeout)

    def _find_button(
        self,
        message: Message,
        text: str | None = None,
        data: bytes | None = None,
        index: int | None = None,
    ) -> KeyboardButtonCallback | None:
        """Find a button in the message keyboard."""
        if not isinstance(message.reply_markup, ReplyInlineMarkup):
            return None

        buttons: list[KeyboardButtonCallback] = []
        for row in message.reply_markup.rows:
            for button in row.buttons:
                if isinstance(button, KeyboardButtonCallback):
                    buttons.append(button)

        if index is not None and 0 <= index < len(buttons):
            return buttons[index]

        for button in buttons:
            if text and button.text == text:
                return button
            if data and button.data == data:
                return button

        # Partial text match
        if text:
            for button in buttons:
                if text.lower() in button.text.lower():
                    return button

        return None

    async def _get_last_bot_message(self, timeout: float) -> Message | None:
        """Get the last message from the bot."""
        if self._bot_entity is None:
            return None

        start_time = datetime.now()
        while (datetime.now() - start_time).total_seconds() < timeout:
            async for message in self.client.iter_messages(
                self._bot_entity, limit=1
            ):
                if message.out:  # Skip our own messages
                    continue
                return message

            await asyncio.sleep(0.5)

        return None

    def get_buttons(self, message: Message | None = None) -> list[dict[str, Any]]:
        """
        Get all buttons from a message.

        Args:
            message: Message to get buttons from.

        Returns:
            List of button info dicts.
        """
        message = message or self._last_message
        if message is None or not isinstance(message.reply_markup, ReplyInlineMarkup):
            return []

        buttons = []
        for row_idx, row in enumerate(message.reply_markup.rows):
            for col_idx, button in enumerate(row.buttons):
                if isinstance(button, KeyboardButtonCallback):
                    buttons.append({
                        "text": button.text,
                        "data": button.data.decode() if button.data else None,
                        "row": row_idx,
                        "col": col_idx,
                    })

        return buttons

    def has_button(
        self,
        text: str | None = None,
        data_contains: str | None = None,
        message: Message | None = None,
    ) -> bool:
        """
        Check if message has a specific button.

        Args:
            text: Button text to find.
            data_contains: Substring to find in button data.
            message: Message to check.

        Returns:
            True if button exists.
        """
        buttons = self.get_buttons(message)

        for button in buttons:
            if text and text.lower() in button["text"].lower():
                return True
            if data_contains and button["data"] and data_contains in button["data"]:
                return True

        return False

    @property
    def last_message(self) -> Message | None:
        """Get the last received message."""
        return self._last_message

    @property
    def last_text(self) -> str:
        """Get text of last message."""
        if self._last_message:
            return self._last_message.text or ""
        return ""
