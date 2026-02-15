import sys
import logging
import structlog
from datetime import datetime, timezone

def setup_logging():
    logging.basicConfig(
        format="-> %(message)s",
        stream=sys.stdout,
        level=logging.WARNING,
    )

    structlog.configure(
        logger_factory=structlog.stdlib.LoggerFactory(),
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S", utc=False),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
    )


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
