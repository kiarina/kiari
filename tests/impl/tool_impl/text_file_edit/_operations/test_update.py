from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_update(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Old content\n")

    message = await run_edit(
        {
            "action": "update",
            "file_path": str(file_path),
            "content": "New content",
        }
    )

    assert not message.failed
    assert file_path.read_text() == "New content\n"

    content = message.contents[0]
    assert "Updated" in content.text
    assert len(content.files) == 1

    assert len(message.display_contents) == 1


async def test_update_no_change(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "test.txt"
    file_path.write_text("Same content\n")

    message = await run_edit(
        {
            "action": "update",
            "file_path": str(file_path),
            "content": "Same content",
        }
    )

    assert not message.failed
    # Identical content produces no diff, hence no display content
    assert message.display_contents == []


async def test_not_exists_error(
    run_edit: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    tmp_path: Path,
) -> None:
    file_path = tmp_path / "missing.txt"

    message = await run_edit(
        {
            "action": "update",
            "file_path": str(file_path),
            "content": "Hello",
        }
    )

    assert message.failed
    assert "does not exist" in message.contents[0].text
    assert not file_path.exists()
