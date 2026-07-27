from collections.abc import Awaitable, Callable, Iterator
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool

from kiari.impl.tool_impl.web import Web
from kiari.impl.web_impl.mock import settings_manager as mock_web_settings_manager
from kiari.lib.web import settings_manager as web_settings_manager, web_registry


@pytest.fixture(autouse=True)
def setup_mock_web() -> Iterator[None]:
    web_settings_manager.set_cli_args("default", "mock")
    mock_web_settings_manager.set_cli_args(
        "search_results",
        [
            {
                "title": "Example",
                "url": "https://example.com",
                "content": "Example content",
            },
            {
                "title": "日本語",
                "url": "https://example.com/ja",
                "content": "日本語の検索結果",
            },
        ],
    )
    mock_web_settings_manager.set_cli_args(
        "fetch_markdown",
        "# Example\n\nFetched content.",
    )

    yield

    web_registry.clear()
    web_settings_manager.cli_args = {}
    mock_web_settings_manager.cli_args = {}


@pytest.fixture
def tool() -> BaseTool:
    tool = Web()
    tool.name = "web"
    return tool


@pytest.fixture
def run_web(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any]], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any]) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="web", args=args),
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]

        assert len(messages) == 1
        return messages[0]

    return _run
