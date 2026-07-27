from typing import Any, Self

from kiari.lib.watcher import WatcherName, WatchEvent

from .rtdb_watch_payload import RTDBWatchPayload


class RTDBWatchEvent(WatchEvent):
    @property
    def payload(self) -> RTDBWatchPayload:
        return RTDBWatchPayload.model_validate_json(self.text)

    @property
    def event_type(self) -> str:
        return self.payload.event_type

    @property
    def path(self) -> str:
        return self.payload.path

    @property
    def data(self) -> Any:
        return self.payload.data

    @classmethod
    def create(
        cls,
        *,
        watcher_name: WatcherName,
        event_type: str,
        path: str,
        data: Any,
    ) -> Self:
        payload = RTDBWatchPayload(
            event_type=event_type,
            path=path,
            data=data,
        )
        return cls(
            watcher_name=watcher_name,
            text=payload.model_dump_json(indent=2),
        )
