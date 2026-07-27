from kiari.core.logging import setup_logger


def test_setup_logger() -> None:
    setup_logger(
        logger_names=["kiari", "hello"],
        log_level="DEBUG",
    )
