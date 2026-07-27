from kiarina.agi.message import ToolCall
from rich.console import Console

from kiari.core.rich._helpers.render_tool_call import render_tool_call


def render_to_text(renderable: object) -> str:
    console = Console(record=True, width=120)
    console.print(renderable)
    return console.export_text()


def test_render_tool_call(console: Console) -> None:
    console.print(
        render_tool_call(
            ToolCall(
                name="my_tool",
                args={
                    "action": "my_action",
                    "message": "hello",
                },
            )
        )
    )
    output = console.export_text()

    assert "[TOOL CALL] my_tool" in output
