from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.file_info import ImageFileInfo, TextFileInfo
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool

from kiari.impl.tool_impl.text_file_purge import TextFilePurge


@pytest.fixture
def tool() -> BaseTool:
    tool = TextFilePurge()
    tool.name = "text_file_purge"
    return tool


@pytest.fixture
def run_purge(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any], History], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any], history: History) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="text_file_purge", args=args),
                history=history,
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]
        assert len(messages) == 1
        return messages[0]

    return _run


async def test_purges_multiple_text_files_and_deduplicates_ids(
    run_purge: Callable[[dict[str, Any], History], Awaitable[ToolMessage]],
    text_file_info: TextFileInfo,
) -> None:
    second = text_file_info.model_copy(update={"id": "second-text-file"})
    history = History(file_infos=[text_file_info, second])

    message = await run_purge(
        {"ids": [text_file_info.id, second.id, text_file_info.id]},
        history,
    )

    assert not message.failed
    assert history.file_infos == []
    assert message.contents[0].text.count(text_file_info.id) == 1
    assert second.id in message.contents[0].text


async def test_reports_missing_and_preserves_non_text_files(
    run_purge: Callable[[dict[str, Any], History], Awaitable[ToolMessage]],
    text_file_info: TextFileInfo,
    image_file_info: ImageFileInfo,
) -> None:
    history = History(file_infos=[text_file_info, image_file_info])

    message = await run_purge(
        {"ids": [text_file_info.id, "missing", image_file_info.id]},
        history,
    )

    assert not message.failed
    assert [file_info.id for file_info in history.file_infos] == [image_file_info.id]
    assert f"Purged IDs: {text_file_info.id}" in message.contents[0].text
    assert "Not found IDs: missing" in message.contents[0].text
    assert f"Non-text IDs not purged: {image_file_info.id}" in message.contents[0].text


async def test_rejects_empty_ids(
    run_purge: Callable[[dict[str, Any], History], Awaitable[ToolMessage]],
) -> None:
    message = await run_purge({"ids": []}, History())

    assert message.failed
    assert "too_short" in message.contents[0].text
