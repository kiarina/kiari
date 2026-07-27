from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_create(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"

    message = await run_edit(
        {
            "action": "create",
            "file_path": str(file_path),
            "content": "Hello",
        }
    )

    assert not message.failed
    assert file_path.read_text() == "Hello\n"  # trailing newline added

    content = message.contents[0]
    assert "Created" in content.text
    assert len(content.files) == 1

    # The diff is attached as a display content
    assert len(message.display_contents) == 1
    assert message.display_contents[0].type == "text"


async def test_create_empty(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "empty.txt"

    message = await run_edit(
        {
            "action": "create",
            "file_path": str(file_path),
        }
    )

    assert not message.failed
    assert file_path.read_text() == ""  # no trailing newline for empty content

    # An empty file produces no diff, hence no display content
    assert message.display_contents == []


async def test_already_exists_error(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Existing content")

    message = await run_edit(
        {
            "action": "create",
            "file_path": str(file_path),
            "content": "Hello",
        }
    )

    assert message.failed
    assert "already exists" in message.contents[0].text
    # The existing file is left untouched
    assert file_path.read_text() == "Existing content"
