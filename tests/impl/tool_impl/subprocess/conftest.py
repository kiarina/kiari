import re
from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool

from kiari.impl.tool_impl.subprocess import Subprocess
from kiari.lib.subprocess import get_subprocess_manager


@pytest.fixture(autouse=True)
def terminate():
    yield
    get_subprocess_manager().terminate_all_sessions()


@pytest.fixture
def tool() -> BaseTool:
    tool = Subprocess()
    tool.name = "subprocess"
    return tool


@pytest.fixture
def run_run(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any]], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any]) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="subprocess", args=args),
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]

        assert len(messages) == 1
        return messages[0]

    return _run


@pytest.fixture
def get_run_id() -> Callable[[ToolMessage], str]:
    def _get(message: ToolMessage) -> str:
        text = message.contents[0].text
        match = re.search(r"Run ID: (\S+)", text)
        assert match is not None
        return match.group(1)

    return _get
