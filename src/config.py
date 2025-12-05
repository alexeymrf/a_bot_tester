"""
Configuration management for the bot tester.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    # Telegram API credentials
    telegram_api_id: int = Field(..., description="Telegram API ID")
    telegram_api_hash: str = Field(..., description="Telegram API Hash")
    telegram_phone: str = Field(..., description="Phone number with country code")

    # Target bot
    target_bot_username: str = Field(..., description="Bot username to test")

    # Session settings
    session_name: str = Field(default="tester", description="Session file name")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # Test settings
    test_timeout: int = Field(default=30, description="Timeout for test operations")
    delay_between_tests: float = Field(
        default=2.0, description="Delay between tests in seconds"
    )
    delay_after_command: float = Field(
        default=1.5, description="Delay after sending command"
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
