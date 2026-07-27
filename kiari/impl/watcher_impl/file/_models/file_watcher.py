import asyncio
import fnmatch
from collections.abc import AsyncIterator
from pathlib import Path
from typing import cast

from watchfiles import Change, awatch

from kiari.lib.watcher import BaseWatcher

from .._schemas.file_change import FileChange
from .._schemas.file_watch_event import FileWatchEvent
from .._settings import FileWatcherSettings
from .._types.change_type import ChangeType


class FileWatcher(BaseWatcher):
    def __init__(self, settings: FileWatcherSettings) -> None:
        super().__init__()
        self.settings: FileWatcherSettings = settings

    async def watch(self, stop_event: asyncio.Event) -> AsyncIterator[FileWatchEvent]:
        async for changes in awatch(
            *self.settings.paths,
            debounce=int(self.settings.debounce * 1000),
            stop_event=stop_event,
        ):
            if stop_event.is_set():
                break

            filtered_changes = self._filter_changes(changes)

            if not filtered_changes:
                continue

            yield FileWatchEvent.create(
                watcher_name=self.name,
                changes=self._build_file_changes(filtered_changes),
            )

    def _filter_changes(
        self,
        changes: set[tuple[Change, str]],
    ) -> list[tuple[Change, Path]]:
        filtered: list[tuple[Change, Path]] = []

        for change_type, path_str in changes:
            path = Path(path_str)

            if self.settings.change_types:
                change_type_name = change_type.name.lower()
                if change_type_name not in self.settings.change_types:
                    continue

            if self.settings.include_patterns:
                if not any(
                    fnmatch.fnmatch(str(path), pattern)
                    for pattern in self.settings.include_patterns
                ):
                    continue

            if self.settings.exclude_patterns:
                if any(
                    fnmatch.fnmatch(str(path), pattern)
                    for pattern in self.settings.exclude_patterns
                ):
                    continue

            filtered.append((change_type, path))

        return filtered

    def _build_file_changes_text(self, changes: list[tuple[Change, Path]]) -> str:
        return FileWatchEvent.create(
            watcher_name=self.name,
            changes=self._build_file_changes(changes),
        ).text

    def _build_file_changes(self, changes: list[tuple[Change, Path]]) -> list[FileChange]:
        return [
            FileChange(
                change_type=cast(ChangeType, change_type.name.lower()),
                file_path=str(path),
            )
            for change_type, path in sorted(
                changes, key=lambda item: (item[0].name.lower(), str(item[1]))
            )
        ]
