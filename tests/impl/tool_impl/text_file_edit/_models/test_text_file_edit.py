from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_text_file_edit_dispatches_create(
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
    assert message.tool_name == "text_file_edit"
    assert message.tool_call_args["action"] == "create"
    assert file_path.read_text() == "Hello\n"
