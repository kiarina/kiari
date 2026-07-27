from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_str_replace(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Hello world\nGoodbye world\n")

    message = await run_edit(
        {
            "action": "str_replace",
            "file_path": str(file_path),
            "search": "Hello",
            "replace": "Hi",
        }
    )

    assert not message.failed
    assert file_path.read_text() == "Hi world\nGoodbye world\n"
    assert "Replaced string" in message.contents[0].text


async def test_replace_all(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("a\na\na\n")

    message = await run_edit(
        {
            "action": "str_replace",
            "file_path": str(file_path),
            "search": "a",
            "replace": "b",
            "replace_all": True,
        }
    )

    assert not message.failed
    assert file_path.read_text() == "b\nb\nb\n"


async def test_replace_all_not_found(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("content\n")

    message = await run_edit(
        {
            "action": "str_replace",
            "file_path": str(file_path),
            "search": "missing",
            "replace": "x",
            "replace_all": True,
        }
    )

    assert message.failed
    assert "not found" in message.contents[0].text


async def test_file_not_readable(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    message = await run_edit(
        {
            "action": "str_replace",
            "file_path": str(tmp_path / "missing.txt"),
            "search": "a",
            "replace": "b",
        }
    )

    assert message.failed
    assert "cannot be read" in message.contents[0].text


async def test_empty_search(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("content\n")

    message = await run_edit(
        {
            "action": "str_replace",
            "file_path": str(file_path),
            "search": "",
            "replace": "x",
        }
    )

    assert message.failed
    assert "Search pattern is empty" in message.contents[0].text


async def test_multiple_matches(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("a a a\n")

    message = await run_edit(
        {
            "action": "str_replace",
            "file_path": str(file_path),
            "search": "a",
            "replace": "b",
        }
    )

    assert message.failed
    assert "3 locations" in message.contents[0].text


async def test_pattern_not_found(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("content\n")

    message = await run_edit(
        {
            "action": "str_replace",
            "file_path": str(file_path),
            "search": "missing",
            "replace": "x",
        }
    )

    assert message.failed
    assert "not found" in message.contents[0].text
