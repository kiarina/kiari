import logging
from datetime import datetime
from pathlib import Path
from typing import ClassVar

from rich.highlighter import ReprHighlighter
from rich.text import Text

from kiari.core.rich import console_registry


class RichLogHandler(logging.Handler):
    """
    Custom log handler using Rich.

    - Hyperlinks file paths
    - Auto-highlights paths, URLs, numbers, etc. in messages
    - Single-line output (terminal link functionality works properly)
    """

    LEVEL_STYLES: ClassVar[dict[int, str]] = {
        logging.DEBUG: "dim",
        logging.INFO: "blue",
        logging.WARNING: "yellow",
        logging.ERROR: "red",
        logging.CRITICAL: "bold red",
    }

    def __init__(self) -> None:
        super().__init__()
        self.highlighter = ReprHighlighter()

    def emit(self, record: logging.LogRecord) -> None:
        try:
            timestamp = datetime.fromtimestamp(record.created).strftime("%y/%m/%d %H:%M:%S")

            level_style = self.LEVEL_STYLES.get(record.levelno, "")

            file_path = Path(record.pathname).resolve()
            file_link = f"file://{file_path}"
            if record.lineno:
                file_link += f"#{record.lineno}"

            file_display = f"{record.filename}:{record.lineno}"

            message = Text(record.getMessage())
            message = self.highlighter(message)

            text = Text()
            text.append(f"[{timestamp}] ", style="cyan")
            text.append(f"{record.levelname:<8}", style=level_style)
            text.append(" ")
            text.append(message)
            text.append(" (", style="dim")
            text.append(file_display, style=f"dim link {file_link}")
            text.append(")", style="dim")

            console_registry.get().print(text, soft_wrap=True)

        except Exception:
            self.handleError(record)
