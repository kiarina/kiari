from typing import Self

from kiari.lib.watcher import WatcherName, WatchEvent

from .file_change import FileChange
from .file_watch_payload import FileWatchPayload


class FileWatchEvent(WatchEvent):
    @property
    def payload(self) -> FileWatchPayload:
        return FileWatchPayload.model_validate_json(self.text)

    @property
    def changes(self) -> list[FileChange]:
        return self.payload.changes

    @classmethod
    def create(cls, *, watcher_name: WatcherName, changes: list[FileChange]) -> Self:
        payload = FileWatchPayload(changes=changes)
        return cls(
            watcher_name=watcher_name,
            text=payload.model_dump_json(indent=2),
        )
