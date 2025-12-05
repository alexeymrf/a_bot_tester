"""
Logging configuration using structlog.
"""

import logging
import sys

import structlog
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(level: str = "INFO") -> None:
    """
    Configure structured logging.

    Args:
        level: Logging level.
    """
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper(), logging.INFO),
        handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)],
    )

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a configured logger.

    Args:
        name: Logger name.

    Returns:
        Configured logger instance.
    """
    return structlog.get_logger(name)
