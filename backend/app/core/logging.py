import logging
import sys

import structlog
from structlog.types import EventDict, Processor

from app.core.config import settings


def _drop_debug_color(record: logging.LogRecord) -> EventDict:
    return {"event": record.getMessage(), "level": record.levelname.lower()}


def configure_logging() -> None:
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        timestamper,
    ]
    if settings.app_env == "dev":
        processors.append(structlog.dev.ConsoleRenderer(colors=True))
    else:
        processors.append(structlog.processors.dict_tracebacks)
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(message)s",
        stream=sys.stdout,
    )


log = structlog.get_logger()
