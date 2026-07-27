from pathlib import Path
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, ToolContext

from kiari.impl.tool_impl.text_file_view import TextFileView


@pytest.fixture
def tool():
    tool = TextFileView()
    tool.name = "text_file_view"
    return tool


def _create_ctx(run_context: RunContext, args: dict[str, Any]) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="text_file_view", args=args),
        run_context=run_context,
    )


async def test_valid_text_file(tool: BaseTool, run_context: RunContext, tmp_path: Path) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5")

    ctx = _create_ctx(
        run_context,
        {
            "file_path": str(file_path),
            "start_line": 2,
            "end_line": 4,
        },
    )

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert content.text == "Viewed the file successfully."
    assert len(content.files) == 1


async def test_not_found(tool: BaseTool, run_context: RunContext) -> None:
    ctx = _create_ctx(
        run_context,
        {"file_path": "/path/to/non_existent_file.txt"},
    )

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert "was not found" in content.text
    assert content.files == []


async def test_directory(tool: BaseTool, run_context: RunContext, tmp_path: Path) -> None:
    dir_path = tmp_path / "text_files"
    dir_path.mkdir()
    (dir_path / "sample.txt").write_text("Hello")
    (dir_path / ".hidden").write_text("secret")
    (dir_path / "subdir").mkdir()

    ctx = _create_ctx(run_context, {"file_path": str(dir_path)})

    events = [event async for event in tool.run(ctx)]

    assert isinstance(events[0], ToolMessageEvent)
    content = events[0].message.contents[0]
    assert "is a directory" in content.text
    assert "- sample.txt" in content.text
    assert "- .hidden" in content.text  # hidden files included
    assert "- subdir/" in content.text  # directories included with trailing slash
    assert content.files == []


async def test_directory_with_many_entries(
    tool: BaseTool, run_context: RunContext, tmp_path: Path
) -> None:
    dir_path = tmp_path / "many_files"
    dir_path.mkdir()

    for i in range(150):
        (dir_path / f"file_{i:03d}.txt").write_text("x")

    ctx = _create_ctx(run_context, {"file_path": str(dir_path)})

    events = [event async for event in tool.run(ctx)]

    assert isinstance(events[0], ToolMessageEvent)
    content = events[0].message.contents[0]
    assert "- file_099.txt" in content.text  # first 100 entries are shown
    assert "- file_100.txt" not in content.text  # 101st entry onwards is omitted
    assert "... and 50 more" in content.text


async def test_empty_directory(tool: BaseTool, run_context: RunContext, tmp_path: Path) -> None:
    dir_path = tmp_path / "empty_text_files"
    dir_path.mkdir()

    ctx = _create_ctx(run_context, {"file_path": str(dir_path)})

    events = [event async for event in tool.run(ctx)]

    assert isinstance(events[0], ToolMessageEvent)
    content = events[0].message.contents[0]
    assert "is a directory" in content.text
    assert "(No entries found)" in content.text
