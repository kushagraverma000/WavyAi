"""Logging configuration."""
import logging
import sys
from typing import Any

import structlog
from structlog.types import Processor

from app.core.config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Set up structured logging."""
    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
    ]

    if settings.LOG_FORMAT == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL),
    )


def get_logger(*args: Any, **kwargs: Any) -> structlog.BoundLogger:
    """Get a structured logger."""
    return structlog.get_logger(*args, **kwargs)

