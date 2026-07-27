from collections.abc import Awaitable, Callable
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_run_dispatches_run(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "run",
            "argv": ["echo", "hello"],
        }
    )

    assert not message.failed
    assert message.tool_name == "subprocess"
    assert message.tool_call_args["action"] == "run"
