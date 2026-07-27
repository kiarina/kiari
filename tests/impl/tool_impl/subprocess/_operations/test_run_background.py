from collections.abc import Awaitable, Callable
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_run_background(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "run_background",
            "argv": ["echo", "hello"],
        }
    )

    assert not message.failed
    assert "started running in the background" in message.contents[0].text
