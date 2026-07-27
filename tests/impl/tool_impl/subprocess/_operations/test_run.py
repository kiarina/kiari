from collections.abc import Awaitable, Callable
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_to_finish(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "run",
            "argv": ["echo", "hello"],
        }
    )

    assert not message.failed
    assert len(message.contents[0].files) == 1
    assert "Execution completed." in message.contents[0].text


async def test_to_background(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "run",
            "argv": ["sleep", "2"],
            "wait_time": 0,
        }
    )

    assert not message.failed
    assert "running in the background" in message.contents[0].text


async def test_shell_via_argv(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "run",
            "argv": ["bash", "-lc", "echo hi | tr a-z A-Z"],
        }
    )

    assert not message.failed
    assert "Execution completed." in message.contents[0].text


async def test_input_data(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "run",
            "argv": ["cat"],
            "input_data": "piped input\n",
        }
    )

    assert not message.failed
    assert "Execution completed." in message.contents[0].text
