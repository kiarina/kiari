import json

from kiari.impl.watcher_impl.pubsub import PubsubWatchEvent, PubsubWatchPayload


def test_pubsub_watch_event() -> None:
    event = PubsubWatchEvent.create(
        watcher_name="pubsub",
        data="hello",
        message_id="message-1",
        publish_time="2026-05-22 00:00:00+00:00",
        attributes={"key": "value"},
    )

    assert json.loads(event.text) == {
        "type": "pubsub_message",
        "message_id": "message-1",
        "publish_time": "2026-05-22 00:00:00+00:00",
        "data": "hello",
        "attributes": {"key": "value"},
    }
    assert event.data == "hello"
    assert event.payload == PubsubWatchPayload(
        message_id="message-1",
        publish_time="2026-05-22 00:00:00+00:00",
        data="hello",
        attributes={"key": "value"},
    )
    assert event.message_id == "message-1"
    assert event.publish_time == "2026-05-22 00:00:00+00:00"
    assert event.attributes == {"key": "value"}
    assert event.metadata == {}
