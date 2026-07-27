from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_line_replace(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": 2,
            "end_line": 2,
            "replace": "Replaced",
        }
    )

    assert not message.failed
    assert file_path.read_text() == "Line 1\nReplaced\nLine 3"
    assert "Replaced lines" in message.contents[0].text


async def test_insert_head(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": 0,
            "end_line": 0,
            "replace": "Header",
        }
    )

    assert not message.failed
    assert file_path.read_text() == "Header\nLine 1\nLine 2"


async def test_insert_tail(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": -1,
            "end_line": -1,
            "replace": "Footer",
        }
    )

    assert not message.failed
    assert file_path.read_text() == "Line 1\nLine 2\nFooter"


async def test_file_not_readable(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(tmp_path / "missing.txt"),
            "start_line": 1,
            "end_line": 1,
            "replace": "x",
        }
    )

    assert message.failed
    assert "cannot be read" in message.contents[0].text


async def test_invalid_start_line(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": -5,
            "end_line": 1,
            "replace": "x",
        }
    )

    assert message.failed
    assert "Start line number must be 1 or greater" in message.contents[0].text


async def test_start_line_exceeds_max(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": 10,
            "end_line": 10,
            "replace": "x",
        }
    )

    assert message.failed
    assert "exceeds the maximum line count" in message.contents[0].text


async def test_invalid_end_line(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": 1,
            "end_line": -5,
            "replace": "x",
        }
    )

    assert message.failed
    assert "End line number must be 1 or greater" in message.contents[0].text


async def test_end_line_exceeds_max(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": 1,
            "end_line": 10,
            "replace": "x",
        }
    )

    assert message.failed
    assert "exceeds the maximum line count" in message.contents[0].text


async def test_start_greater_than_end(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Line 1\nLine 2\nLine 3")

    message = await run_edit(
        {
            "action": "line_replace",
            "file_path": str(file_path),
            "start_line": 3,
            "end_line": 2,
            "replace": "x",
        }
    )

    assert message.failed
    assert "must be less than or equal to" in message.contents[0].text
