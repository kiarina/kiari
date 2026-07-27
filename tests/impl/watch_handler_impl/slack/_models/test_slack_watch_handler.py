from typing import Any

import pytest
from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.event import AIMessageEvent, ToolMessageEvent
from kiarina.agi.history import History
from kiarina.agi.run_context import RunContext

from kiari.cli.watch.watch_handler import WatchSession
from kiari.core.profile import RunOptions
from kiari.impl.watch_handler_impl.slack import (
    SlackWatchHandler,
    SlackWatchHandlerSettings,
)
from kiari.impl.watcher_impl.slack import SlackWatchEvent
from kiari.lib.watcher import WatchEvent


class FakeSlackClient:
    def __init__(self) -> None:
        self.messages: list[dict[str, Any]] = []
        self.files: list[dict[str, Any]] = []

    async def chat_postMessage(self, **kwargs: Any) -> None:
        self.messages.append(kwargs)

    async def files_upload_v2(self, **kwargs: Any) -> None:
        self.files.append(kwargs)


@pytest.fixture
def handler() -> SlackWatchHandler:
    handler = SlackWatchHandler(
        "default",
        RunOptions(no_save=True),
        channel_id="CDEFAULT",
        thread_ts="TDEFAULT",
    )
    handler.name = "slack"
    return handler


@pytest.fixture
def watch_event() -> WatchEvent:
    return SlackWatchEvent.create(
        watcher_name="slack",
        team_id="T123",
        channel_id="C123",
        user_id="U123",
        ts="123.456",
        thread_ts="123.000",
        text="hello",
    )


def create_session(watch_event: WatchEvent) -> WatchSession:
    return WatchSession(
        watch_event=watch_event,
        history=History(),
        chat_options=None,
        prompt_options=None,
        workflow_options=None,
        tool_options=None,
        agent_options=None,
        cost_recorder=cost_recorder_registry.resolve("null"),
        run_context=RunContext(),
    )


def test_slack_watch_handler() -> None:
    handler = SlackWatchHandler(
        "default",
        RunOptions(),
        settings=SlackWatchHandlerSettings(channel_id="C1"),
        thread_ts="T1",
    )

    assert handler.settings.channel_id == "C1"
    assert handler.settings.thread_ts == "T1"


def test_get_slack_destination(handler: SlackWatchHandler, watch_event: WatchEvent) -> None:
    assert handler._get_slack_destination(watch_event) == ("T123", "C123", "123.000")

    assert handler._get_slack_destination(WatchEvent(watcher_name="file")) == (
        None,
        "CDEFAULT",
        "TDEFAULT",
    )


def test_create_run_context(handler: SlackWatchHandler, watch_event: WatchEvent) -> None:
    run_context = handler._create_run_context(watch_event)

    assert run_context.organization_id == "T123"
    assert run_context.user_id == "C123"
    assert run_context.agent_id == "C123-123.000"


async def test_create_session_uses_slack_message_text(
    handler: SlackWatchHandler, watch_event: WatchEvent
) -> None:
    session = await handler._create_session(watch_event)

    assert session.history.events[-1].to_text() == "hello"


def test_split_text(handler: SlackWatchHandler) -> None:
    assert handler._split_text("hello", 10) == ["hello"]
    assert handler._split_text("hello\nworld", 7) == ["hello", "world"]


async def test_send_ai_message(
    monkeypatch: pytest.MonkeyPatch,
    handler: SlackWatchHandler,
    watch_event: WatchEvent,
) -> None:
    client = FakeSlackClient()

    async def create_client(team_id: str | None) -> FakeSlackClient:
        return client

    monkeypatch.setattr(handler, "_create_client", create_client)

    await handler._send_ai_message(create_session(watch_event), AIMessageEvent.create("**hi**"))

    assert client.messages == [{"channel": "C123", "text": "*hi*", "thread_ts": "123.000"}]


async def test_send_tool_message(
    monkeypatch: pytest.MonkeyPatch,
    handler: SlackWatchHandler,
    watch_event: WatchEvent,
) -> None:
    client = FakeSlackClient()

    async def create_client(team_id: str | None) -> FakeSlackClient:
        return client

    monkeypatch.setattr(handler, "_create_client", create_client)

    await handler._send_tool_message(
        create_session(watch_event),
        ToolMessageEvent.create(
            "tool result",
            tool_name="tool",
            tool_call_id="call-1",
        ),
    )

    assert client.messages == [{"channel": "C123", "text": "tool result", "thread_ts": "123.000"}]


async def test_on_event_error(
    monkeypatch: pytest.MonkeyPatch,
    handler: SlackWatchHandler,
    watch_event: WatchEvent,
) -> None:
    client = FakeSlackClient()

    async def create_client(team_id: str | None) -> FakeSlackClient:
        return client

    monkeypatch.setattr(handler, "_create_client", create_client)

    await handler._on_event_error(create_session(watch_event), ValueError("boom"))

    assert client.messages[0]["channel"] == "C123"
    assert "boom" in client.messages[0]["text"]
