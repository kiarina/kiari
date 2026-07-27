from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool

from kiari.impl.tool_impl.text_file_edit import TextFileEdit


@pytest.fixture
def tool() -> BaseTool:
    tool = TextFileEdit()
    tool.name = "text_file_edit"
    return tool


@pytest.fixture
def run_edit(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any]], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any]) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="text_file_edit", args=args),
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]

        assert len(messages) == 1
        return messages[0]

    return _run
