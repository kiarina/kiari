from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, ToolContext

from kiari.impl.tool_impl.video_file_view import VideoFileView


@pytest.fixture
def tool():
    tool = VideoFileView()
    tool.name = "video_file_view"
    return tool


def _create_ctx(run_context: RunContext, args: dict[str, Any]) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="video_file_view", args=args),
        run_context=run_context,
    )


async def test_valid_video_file(
    tool: BaseTool, run_context: RunContext, video_file_path: str
) -> None:
    ctx = _create_ctx(run_context, {"uri_or_file_path": video_file_path})

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert content.text == "Viewed the video file successfully."
    assert len(content.files) == 1
    assert content.files[0].type == "video"


async def test_not_found(tool: BaseTool, run_context: RunContext) -> None:
    ctx = _create_ctx(
        run_context,
        {"uri_or_file_path": "/path/to/non_existent_file.mp4"},
    )

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert "was not found" in content.text
    assert content.files == []


async def test_not_video(tool: BaseTool, run_context: RunContext, text_file_path: str) -> None:
    ctx = _create_ctx(run_context, {"uri_or_file_path": text_file_path})

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert "is not a video file" in content.text
    assert content.files == []
