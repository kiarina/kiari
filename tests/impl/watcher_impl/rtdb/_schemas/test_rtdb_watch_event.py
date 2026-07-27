import json

from kiari.impl.watcher_impl.rtdb import RTDBWatchEvent, RTDBWatchPayload


def test_rtdb_watch_event() -> None:
    event = RTDBWatchEvent.create(
        watcher_name="rtdb",
        event_type="put",
        path="/events/1",
        data={"message": "hello"},
    )

    assert json.loads(event.text) == {
        "type": "rtdb_event",
        "event_type": "put",
        "path": "/events/1",
        "data": {"message": "hello"},
    }
    assert event.payload == RTDBWatchPayload(
        event_type="put",
        path="/events/1",
        data={"message": "hello"},
    )
    assert event.event_type == "put"
    assert event.path == "/events/1"
    assert event.data == {"message": "hello"}
    assert event.metadata == {}
