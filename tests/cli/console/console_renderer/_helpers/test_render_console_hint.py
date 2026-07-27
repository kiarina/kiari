from rich.console import Console

from kiari.cli.console.console_renderer import render_console_hint
from kiari.core.profile import RunOptions


def test_render_console_hint(
    console: Console,
    run_options: RunOptions,
) -> None:
    console.print(render_console_hint(run_options))
    output = console.export_text()
    assert "hint" in output
