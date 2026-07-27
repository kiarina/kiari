import logging

from .._models.rich_log_handler import RichLogHandler
from .._types.log_level import LogLevel


def setup_logger(
    *,
    logger_names: list[str],
    log_level: LogLevel,
) -> None:
    for logger_name in logger_names:
        _setup_logger(logger_name, log_level)


def _setup_logger(logger_name: str, log_level: LogLevel) -> None:
    logger = logging.getLogger(logger_name)

    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(logging.getLevelNamesMapping()[log_level])
    logger.propagate = False
    logger.addHandler(RichLogHandler())
