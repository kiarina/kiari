import asyncio
from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from .._schemas.watch_event import WatchEvent
from .watcher_name import WatcherName


@runtime_checkable
class Watcher(Protocol):
    name: WatcherName

    def watch(self, stop_event: asyncio.Event) -> AsyncIterator[WatchEvent]: ...
