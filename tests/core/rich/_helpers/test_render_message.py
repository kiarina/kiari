from kiarina.agi.content import Content
from kiarina.agi.display_content import TextDisplayContent
from kiarina.agi.message import (
    AIMessage,
    HumanMessage,
    ToolCall,
    ToolMessage,
)
from rich.console import Console

from kiari.core.rich import render_message


def test_human_message(console: Console) -> None:
    console.print(
        render_message(
            HumanMessage(
                contents=[
                    Content(text="hello"),
                    Content(text="world"),
                ]
            )
        )
    )

    output = console.export_text()

    assert "hello" in output
    assert "world" in output


def test_ai_message(console: Console) -> None:
    console.print(
        render_message(
            AIMessage(
                contents=[Content(text="thinking")],
                tool_calls=[
                    ToolCall(
                        name="search",
                        args={"action": "lookup", "query": "hello"},
                    ),
                    ToolCall(
                        name="search",
                        args={"action": "lookup", "query": "world"},
                    ),
                ],
            )
        )
    )

    output = console.export_text()

    assert "search" in output
    assert '"action": "lookup"' in output
    assert '"query": "hello"' in output
    assert '"query": "world"' in output


def test_tool_message(console: Console) -> None:
    console.print(
        render_message(
            ToolMessage(
                contents=[Content(text="done")],
                tool_name="search",
                tool_call_args={"action": "lookup", "query": "hello"},
                tool_call_id="call-1",
                failed=True,
                return_direct=True,
                artifact={"result": "found"},
                metadata={"key": "value"},
                display_contents=[
                    TextDisplayContent(text="display text 1"),
                    TextDisplayContent(text="display text 2"),
                ],
            )
        )
    )

    output = console.export_text()

    assert "search:lookup" in output
    assert "done" in output
    assert "display text 1" in output
    assert "display text 2" in output
