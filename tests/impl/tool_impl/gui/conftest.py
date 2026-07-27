import asyncio
from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import MagicMock

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool
from kiarina.utils.mime import MIMEBlob

from kiari.impl.tool_impl.gui import Gui


@pytest.fixture
def tool() -> BaseTool:
    tool = Gui()
    tool.name = "gui"
    return tool


@pytest.fixture(autouse=True)
def fast_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _sleep(*args: Any, **kwargs: Any) -> None:
        return None

    monkeypatch.setattr(asyncio, "sleep", _sleep)


@pytest.fixture
def gui_mock(monkeypatch: pytest.MonkeyPatch, image_file_path: str) -> MagicMock:
    from kiari.lib.gui import gui

    with open(image_file_path, "rb") as f:
        mime_blob = MIMEBlob("image/png", f.read())

    monitor = MagicMock()
    monitor.monitor_indexes = [1]
    monitor.get_screenshot.return_value = mime_blob

    mouse = MagicMock()
    keyboard = MagicMock()

    # ``gui`` is a shared singleton imported by reference in every operation
    # module, so patching the private slots is enough to cover all of them.
    monkeypatch.setattr(gui, "_monitor", monitor)
    monkeypatch.setattr(gui, "_mouse", mouse)
    monkeypatch.setattr(gui, "_keyboard", keyboard)

    container = MagicMock()
    container.monitor = monitor
    container.mouse = mouse
    container.keyboard = keyboard
    return container


@pytest.fixture
def run_gui(
    tool: BaseTool,
    run_context: RunContext,
    gui_mock: MagicMock,
) -> Callable[[dict[str, Any]], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any]) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="gui", args=args),
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]

        assert len(messages) == 1
        return messages[0]

    return _run
