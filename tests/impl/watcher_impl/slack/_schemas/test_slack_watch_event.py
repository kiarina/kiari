import json

from kiari.impl.watcher_impl.slack import SlackWatchEvent, SlackWatchPayload


def test_slack_watch_event() -> None:
    event = SlackWatchEvent.create(
        watcher_name="slack",
        team_id="T123",
        channel_id="C123",
        user_id="U123",
        ts="123.456",
        thread_ts="123.000",
        text="hello",
        attachments=["/tmp/a.txt"],
    )

    assert json.loads(event.text) == {
        "type": "slack_message",
        "team_id": "T123",
        "channel_id": "C123",
        "user_id": "U123",
        "ts": "123.456",
        "thread_ts": "123.000",
        "text": "hello",
    }
    assert event.payload == SlackWatchPayload(
        team_id="T123",
        channel_id="C123",
        user_id="U123",
        ts="123.456",
        thread_ts="123.000",
        text="hello",
    )
    assert event.message_text == "hello"
    assert event.team_id == "T123"
    assert event.channel_id == "C123"
    assert event.user_id == "U123"
    assert event.ts == "123.456"
    assert event.thread_ts == "123.000"
    assert event.attachments == ["/tmp/a.txt"]
    assert event.metadata == {}
