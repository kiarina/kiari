from typing import Self

from kiari.lib.watcher import WatcherName, WatchEvent

from .pubsub_watch_payload import PubsubWatchPayload


class PubsubWatchEvent(WatchEvent):
    @property
    def payload(self) -> PubsubWatchPayload:
        return PubsubWatchPayload.model_validate_json(self.text)

    @property
    def data(self) -> str:
        return self.payload.data

    @property
    def message_id(self) -> str:
        return self.payload.message_id

    @property
    def publish_time(self) -> str:
        return self.payload.publish_time

    @property
    def attributes(self) -> dict[str, str]:
        return self.payload.attributes

    @classmethod
    def create(
        cls,
        *,
        watcher_name: WatcherName,
        data: str,
        message_id: str,
        publish_time: str,
        attributes: dict[str, str],
    ) -> Self:
        payload = PubsubWatchPayload(
            message_id=message_id,
            publish_time=publish_time,
            data=data,
            attributes=attributes,
        )
        return cls(
            watcher_name=watcher_name,
            text=payload.model_dump_json(indent=2),
        )
