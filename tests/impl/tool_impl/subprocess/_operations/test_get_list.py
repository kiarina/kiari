from collections.abc import Awaitable, Callable
from typing import Any

from kiarina.agi.message import ToolMessage


async def test_no_processes(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run({"action": "get_list"})

    assert not message.failed
    assert "No tracked processes found." in message.contents[0].text
    assert len(message.contents[0].files) == 0


async def test_running_process_found(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_run({"action": "run_background", "argv": ["sleep", "1"]})
    assert not message.failed

    message = await run_run({"action": "get_list"})

    assert not message.failed
    assert "Found 1 tracked process(es)." in message.contents[0].text
    assert "RUNNING" in message.contents[0].text
    assert len(message.contents[0].files) == 1


async def test_completed_background_process_found(
    run_run: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    # A background job that has already finished must still appear in the list so
    # the agent can notice its completion.
    message = await run_run({"action": "run", "argv": ["echo", "hello"]})
    assert not message.failed

    message = await run_run({"action": "get_list"})

    assert not message.failed
    assert "Found 1 tracked process(es)." in message.contents[0].text
    assert "SUCCESS" in message.contents[0].text
