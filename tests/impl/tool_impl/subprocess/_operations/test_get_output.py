from collections.abc import Awaitable, Callable
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_not_found(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "get_output",
            "run_id": "non_existent_run_id",
        }
    )

    assert message.failed
    assert "does not exist" in message.contents[0].text


async def test_success(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run", "argv": ["echo", "hello"]})
    assert not message.failed
    run_id = get_run_id(message)

    message = await run_run(
        {
            "action": "get_output",
            "run_id": run_id,
            "start_line": 1,
            "end_line": 1,
        }
    )

    assert not message.failed
    assert "Process completed successfully." in message.contents[0].text


async def test_failure(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run", "argv": ["bash", "-lc", "exit 1"]})
    assert not message.failed
    run_id = get_run_id(message)

    message = await run_run({"action": "get_output", "run_id": run_id})

    assert not message.failed
    assert "Process failed" in message.contents[0].text


async def test_cancelled(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run_background", "argv": ["sleep", "5"]})
    assert not message.failed
    run_id = get_run_id(message)

    message = await run_run({"action": "cancel", "run_id": run_id})
    assert not message.failed

    message = await run_run({"action": "get_output", "run_id": run_id})

    assert not message.failed
    assert "Process was cancelled." in message.contents[0].text


async def test_running(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run_background", "argv": ["sleep", "1"]})
    assert not message.failed
    run_id = get_run_id(message)

    message = await run_run({"action": "get_output", "run_id": run_id})

    assert not message.failed
    assert "Process is running." in message.contents[0].text
