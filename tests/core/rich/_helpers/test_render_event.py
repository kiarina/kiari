from kiarina.agi.event import CustomEvent, HumanMessageEvent
from rich.console import Console

from kiari.core.rich import render_event


def test_message(console: Console) -> None:
    console.print(render_event(HumanMessageEvent.create("hello")))
    output = console.export_text()
    assert "hello" in output


def test_custom_event(console: Console) -> None:
    console.print(
        render_event(
            CustomEvent(
                payload={
                    "type": "test_event",
                    "data": {"key": "value"},
                    "state": "completed",
                },
            )
        )
    )

    output = console.export_text()

    assert "completed" in output
