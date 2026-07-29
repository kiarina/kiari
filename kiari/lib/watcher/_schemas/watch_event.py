from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field, PrivateAttr

from kiari.core.file_info_source import FileInfoSource

from .._types.watcher_name import WatcherName


class WatchEvent(BaseModel):
    watcher_name: WatcherName
    text: str = ""
    attachments: list[FileInfoSource] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    _acknowledge_callback: Callable[[], Awaitable[None]] | None = PrivateAttr(default=None)
    _release_callback: Callable[[], Awaitable[None]] | None = PrivateAttr(default=None)

    def set_acknowledgement_callbacks(
        self,
        *,
        acknowledge: Callable[[], Awaitable[None]],
        release: Callable[[], Awaitable[None]],
    ) -> None:
        self._acknowledge_callback = acknowledge
        self._release_callback = release

    async def acknowledge(self) -> None:
        if self._acknowledge_callback:
            await self._acknowledge_callback()

    async def release(self) -> None:
        if self._release_callback:
            await self._release_callback()
