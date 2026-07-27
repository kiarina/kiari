import pytest
from kiarina.agi.event import AIMessageEvent
from kiarina.agi.message import ToolCall
from rich.console import Console

from kiari.cli.console.console_handler import (
    BaseConsoleHandler,
    ConsoleRequest,
)
from kiari.core.profile import RunOptions


class ExampleConsoleHandler(BaseConsoleHandler):
    pass


@pytest.fixture
def handler():
    handler = ExampleConsoleHandler("example", RunOptions())
    handler.name = "example"
    return handler


async def test_base_console_handler(
    console: Console, setup_run_context, handler: ExampleConsoleHandler
) -> None:
    print(f"name: {handler.name}")
    print(f"history_repository: {handler.history_repository}")

    with pytest.raises(Exception, match="Test exception"):
        async with handler.handle_session() as session:
            raise Exception("Test exception")

    async with handler.handle_session() as session:
        console.print(handler.render_ui(session))
        session.history.add_event(AIMessageEvent.create(tool_calls=[ToolCall(name="hello")]))

        async with handler.handle_request(session, ConsoleRequest(text="hello")):
            await handler.on_agent_event(session, AIMessageEvent.create("hello"))

    assert True
