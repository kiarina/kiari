import asyncio
from collections.abc import AsyncIterator
from typing import Any

from .._schemas.watch_event import WatchEvent
from .._types.watcher import Watcher
from .._types.watcher_name import WatcherName


class BaseWatcher(Watcher):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: WatcherName | None = None

    @property
    def name(self) -> WatcherName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Watcher name not set")

        return self._name

    @name.setter
    def name(self, value: WatcherName) -> None:
        self._name = value

    def watch(self, stop_event: asyncio.Event) -> AsyncIterator[WatchEvent]:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__
