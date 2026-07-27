from typing import Self

from kiari.core.file_info_source import FileInfoSource
from kiari.lib.watcher import WatcherName, WatchEvent

from .slack_watch_payload import SlackWatchPayload


class SlackWatchEvent(WatchEvent):
    @property
    def payload(self) -> SlackWatchPayload:
        return SlackWatchPayload.model_validate_json(self.text)

    @property
    def message_text(self) -> str:
        return self.payload.text

    @property
    def team_id(self) -> str:
        return self.payload.team_id

    @property
    def channel_id(self) -> str:
        return self.payload.channel_id

    @property
    def user_id(self) -> str:
        return self.payload.user_id

    @property
    def ts(self) -> str:
        return self.payload.ts

    @property
    def thread_ts(self) -> str:
        return self.payload.thread_ts

    @classmethod
    def create(
        cls,
        *,
        watcher_name: WatcherName,
        team_id: str,
        channel_id: str,
        user_id: str,
        ts: str,
        text: str,
        thread_ts: str = "",
        attachments: list[FileInfoSource] | None = None,
    ) -> Self:
        payload = SlackWatchPayload(
            team_id=team_id,
            channel_id=channel_id,
            user_id=user_id,
            ts=ts,
            thread_ts=thread_ts,
            text=text,
        )
        return cls(
            watcher_name=watcher_name,
            text=payload.model_dump_json(indent=2),
            attachments=attachments or [],
        )
