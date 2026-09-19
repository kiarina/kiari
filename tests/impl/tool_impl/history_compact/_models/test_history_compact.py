from collections.abc import Awaitable, Callable
from typing import Any

import pytest
from kiarina.agi.event import (
    AIMessageEvent,
    CustomEvent,
    HumanMessageEvent,
    ToolMessageEvent,
)
from kiarina.agi.file_info import TextFileInfo
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool

from kiari.impl.tool_impl.history_compact import HistoryCompact


@pytest.fixture
def tool() -> BaseTool:
    tool = HistoryCompact()
    tool.name = "history_compact"
    return tool


@pytest.fixture
def run_compact(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any], History, ToolCall], Awaitable[ToolMessage]]:
    async def _run(
        args: dict[str, Any],
        history: History,
        tool_call: ToolCall,
    ) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                tool_call,
                history=history,
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]
        assert len(messages) == 1
        return messages[0]

    return _run


def _history_for_call(
    tool_call: ToolCall,
    *,
    file_infos: list[TextFileInfo] | None = None,
) -> History:
    previous_call = ToolCall(id="previous-call", name="other", args={"long": "value"})
    return History(
        events=[
            HumanMessageEvent.create("original request"),
            AIMessageEvent.create(tool_calls=[previous_call]),
            ToolMessageEvent.create(
                "long result",
                tool_name="other",
                tool_call_id=previous_call.id,
            ),
            CustomEvent.create(type="old_custom_event"),
            HumanMessageEvent.create("compact the history"),
            AIMessageEvent.create(tool_calls=[tool_call]),
        ],
        file_infos=file_infos or [],
    )


async def test_compacts_history_to_request_call_and_result(
    run_compact: Callable[[dict[str, Any], History, ToolCall], Awaitable[ToolMessage]],
    text_file_info: TextFileInfo,
) -> None:
    args = {
        "context": "Goal <one> and current state",
        "narrative": "Tried A & selected B",
        "referenced_file_paths": ["/tmp/a.py", "/tmp/a.py", "/tmp/b.md"],
    }
    tool_call = ToolCall(id="compact-call", name="history_compact", args=args.copy())
    history = _history_for_call(tool_call, file_infos=[text_file_info])

    message = await run_compact(args, history, tool_call)
    history.add_message(message)

    assert [event.type for event in history.events] == [
        "human_message",
        "ai_message",
        "tool_message",
    ]
    assert history.events[0].message.to_text() == "compact the history"
    assert history.events[1].message.tool_calls[0].args == {}
    assert message.tool_call_args == {}
    assert '<compacted_history removed_events="4">' in message.contents[0].text
    assert "Goal &lt;one&gt; and current state" in message.contents[0].text
    assert "Tried A &amp; selected B" in message.contents[0].text
    assert message.contents[0].text.count("/tmp/a.py") == 1
    assert "/tmp/b.md" in message.contents[0].text
    assert history.file_infos == [text_file_info]


async def test_rejects_parallel_tool_calls_without_mutating_history(
    run_compact: Callable[[dict[str, Any], History, ToolCall], Awaitable[ToolMessage]],
) -> None:
    args = {"context": "Current context"}
    tool_call = ToolCall(id="compact-call", name="history_compact", args=args.copy())
    history = _history_for_call(tool_call)
    history.events[-1].message.tool_calls.append(ToolCall(id="other-call", name="other", args={}))
    original_events = history.events.copy()

    message = await run_compact(args, history, tool_call)

    assert message.failed
    assert history.events == original_events
    assert tool_call.args == args


async def test_rejects_events_after_current_call_without_mutating_history(
    run_compact: Callable[[dict[str, Any], History, ToolCall], Awaitable[ToolMessage]],
) -> None:
    args = {"narrative": "Relevant history"}
    tool_call = ToolCall(id="compact-call", name="history_compact", args=args.copy())
    history = _history_for_call(tool_call)
    history.events.append(CustomEvent.create(type="later_event"))
    original_events = history.events.copy()

    message = await run_compact(args, history, tool_call)

    assert message.failed
    assert history.events == original_events
    assert tool_call.args == args


async def test_rejects_missing_human_message_without_mutating_history(
    run_compact: Callable[[dict[str, Any], History, ToolCall], Awaitable[ToolMessage]],
) -> None:
    args = {"context": "Current context"}
    tool_call = ToolCall(id="compact-call", name="history_compact", args=args.copy())
    history = History(events=[AIMessageEvent.create(tool_calls=[tool_call])])
    original_events = history.events.copy()

    message = await run_compact(args, history, tool_call)

    assert message.failed
    assert history.events == original_events
    assert tool_call.args == args


async def test_rejects_empty_context_and_narrative(
    run_compact: Callable[[dict[str, Any], History, ToolCall], Awaitable[ToolMessage]],
) -> None:
    args = {"context": " ", "narrative": "\n"}
    tool_call = ToolCall(id="compact-call", name="history_compact", args=args.copy())
    history = _history_for_call(tool_call)
    original_events = history.events.copy()

    message = await run_compact(args, history, tool_call)

    assert message.failed
    assert history.events == original_events
    assert tool_call.args == args
