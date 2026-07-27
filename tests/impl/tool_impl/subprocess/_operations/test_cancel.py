from collections.abc import Awaitable, Callable
from typing import Any
from unittest.mock import AsyncMock, patch

from kiarina.agi.message import ToolMessage


async def test_not_found(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run(
        {
            "action": "cancel",
            "run_id": "non_existent_run_id",
        }
    )

    assert message.failed
    assert "does not exist" in message.contents[0].text


async def test_already_completed(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run", "argv": ["echo", "hello"]})
    assert not message.failed
    run_id = get_run_id(message)

    message = await run_run({"action": "cancel", "run_id": run_id})

    assert message.failed
    assert "has already completed" in message.contents[0].text


async def test_failed(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run_background", "argv": ["sleep", "2"]})
    assert not message.failed
    run_id = get_run_id(message)

    with patch(
        "kiari.lib.subprocess._models.subprocess_manager.SubprocessManager.cancel_run",
        new=AsyncMock(side_effect=RuntimeError("Mock cancel error")),
    ):
        message = await run_run({"action": "cancel", "run_id": run_id})

    assert message.failed
    assert "Mock cancel error" in message.contents[0].text


async def test_success(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run_background", "argv": ["sleep", "1"]})
    assert not message.failed
    run_id = get_run_id(message)

    message = await run_run({"action": "cancel", "run_id": run_id})

    assert not message.failed
    assert "Process cancellation completed." in message.contents[0].text


async def test_immediate_forced_termination(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    get_run_id: Callable[[ToolMessage], str],
) -> None:
    message = await run_run({"action": "run_background", "argv": ["sleep", "1"]})
    assert not message.failed
    run_id = get_run_id(message)

    message = await run_run(
        {
            "action": "cancel",
            "run_id": run_id,
            "graceful_shutdown_timeout": 0,
        }
    )

    assert not message.failed
    assert "Immediate forced termination" in message.contents[0].text
