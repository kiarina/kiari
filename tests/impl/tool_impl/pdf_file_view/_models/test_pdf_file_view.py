from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, ToolContext

from kiari.impl.tool_impl.pdf_file_view import PdfFileView


@pytest.fixture
def tool():
    tool = PdfFileView()
    tool.name = "pdf_file_view"
    return tool


def _create_ctx(run_context: RunContext, args: dict[str, Any]) -> ToolContext:
    return ToolContext.create(
        tool_call=ToolCall(name="pdf_file_view", args=args),
        run_context=run_context,
    )


async def test_valid_pdf_file(tool: BaseTool, run_context: RunContext, pdf_file_path: str) -> None:
    ctx = _create_ctx(run_context, {"uri_or_file_path": pdf_file_path})

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert content.text == "Viewed the PDF file successfully."
    assert len(content.files) == 1
    assert content.files[0].type == "pdf"


async def test_page_range(tool: BaseTool, run_context: RunContext, pdf_file_path: str) -> None:
    ctx = _create_ctx(
        run_context,
        {"uri_or_file_path": pdf_file_path, "start_page": 1, "end_page": 1},
    )

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert content.files[0].type == "pdf"


async def test_not_found(tool: BaseTool, run_context: RunContext) -> None:
    ctx = _create_ctx(
        run_context,
        {"uri_or_file_path": "/path/to/non_existent_file.pdf"},
    )

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert "was not found" in content.text
    assert content.files == []


async def test_not_pdf(tool: BaseTool, run_context: RunContext, text_file_path: str) -> None:
    ctx = _create_ctx(run_context, {"uri_or_file_path": text_file_path})

    events = [event async for event in tool.run(ctx)]

    assert len(events) == 1
    assert isinstance(events[0], ToolMessageEvent)
    assert not events[0].message.failed

    content = events[0].message.contents[0]
    assert "is not a PDF file" in content.text
    assert content.files == []
