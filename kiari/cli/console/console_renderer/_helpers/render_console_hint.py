from kiarina.i18n import get_i18n, get_system_language
from rich.console import RenderableType
from rich.text import Text

from kiari.cli.console._i18n import ConsoleI18n
from kiari.core.profile import RunOptions


def render_console_hint(run_options: RunOptions) -> RenderableType:
    t = get_i18n(ConsoleI18n, run_options.language or get_system_language())
    return Text.from_markup(f"[bold white on blue] hint [/bold white on blue] {t.help_hint}")
