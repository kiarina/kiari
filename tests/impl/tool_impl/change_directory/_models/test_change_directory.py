import os
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool
from kiarina.i18n import get_i18n

from kiari.impl.tool_impl.change_directory import ChangeDirectory
from kiari.impl.tool_impl.change_directory._i18n import ChangeDirectoryI18n


@pytest.fixture
def tool() -> BaseTool:
    tool = ChangeDirectory()
    tool.name = "change_directory"
    return tool


@pytest.fixture
def t(run_context: RunContext) -> ChangeDirectoryI18n:
    return get_i18n(ChangeDirectoryI18n, run_context.language)


@pytest.fixture
def run_cd(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any]], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any]) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="change_directory", args=args),
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]

        assert len(messages) == 1
        return messages[0]

    return _run


async def test_valid_directory_change(
    run_cd: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    t: ChangeDirectoryI18n,
    tmp_path: Path,
) -> None:
    original_dir = os.getcwd()

    try:
        target_dir = str(tmp_path)
        message = await run_cd({"dir_path": target_dir})

        assert not message.failed
        assert t.result.format(dir_path=target_dir) in message.contents[0].text
        assert os.getcwd() == str(Path(target_dir).resolve())

    finally:
        os.chdir(original_dir)


async def test_home_directory_expansion(
    run_cd: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    t: ChangeDirectoryI18n,
) -> None:
    original_dir = os.getcwd()

    try:
        message = await run_cd({"dir_path": "~"})

        assert not message.failed
        assert t.result.format(dir_path=str(Path.home())) in message.contents[0].text
        assert os.getcwd() == str(Path.home())

    finally:
        os.chdir(original_dir)


async def test_directory_not_found(
    run_cd: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    t: ChangeDirectoryI18n,
) -> None:
    dir_path = "/non_existent_directory_12345"
    message = await run_cd({"dir_path": dir_path})

    assert message.failed
    assert t.file_not_found_error.format(dir_path=dir_path) in message.contents[0].text


async def test_not_a_directory(
    run_cd: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    t: ChangeDirectoryI18n,
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "sample.txt"
    file_path.write_text("hello")

    message = await run_cd({"dir_path": str(file_path)})

    assert message.failed
    assert t.not_a_directory_error.format(dir_path=str(file_path)) in message.contents[0].text
