from kiarina.agi.file_info import TextFileInfo
from rich.console import Console

from kiari.core.rich._helpers.render_file_info import render_file_info


def test_render_file_info(console: Console, text_file_info: TextFileInfo) -> None:
    text_file_info.name = "sample text"
    console.print(render_file_info(text_file_info))

    output = console.export_text()

    assert "[TEXT FILE INFO]" in output
