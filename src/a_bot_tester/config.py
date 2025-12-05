"""Configuration management for a_bot_tester."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""

    api_id: int
    api_hash: str
    phone: str
    target_bot_username: str
    session_name: str = "tester_session"
    response_timeout: int = 30
    log_level: str = "INFO"

    @classmethod
    def from_env(cls, env_path: Path | None = None) -> "Config":
        """Load configuration from environment variables.
        
        Args:
            env_path: Optional path to .env file
            
        Returns:
            Config instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        if env_path:
            load_dotenv(env_path)
        else:
            load_dotenv()

        api_id = os.getenv("TELEGRAM_API_ID")
        api_hash = os.getenv("TELEGRAM_API_HASH")
        phone = os.getenv("TELEGRAM_PHONE")
        target_bot = os.getenv("TARGET_BOT_USERNAME")

        missing = []
        if not api_id:
            missing.append("TELEGRAM_API_ID")
        if not api_hash:
            missing.append("TELEGRAM_API_HASH")
        if not phone:
            missing.append("TELEGRAM_PHONE")
        if not target_bot:
            missing.append("TARGET_BOT_USERNAME")

        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

        return cls(
            api_id=int(api_id),
            api_hash=api_hash,
            phone=phone,
            target_bot_username=target_bot.lstrip("@"),
            session_name=os.getenv("SESSION_NAME", "tester_session"),
            response_timeout=int(os.getenv("RESPONSE_TIMEOUT", "30")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
