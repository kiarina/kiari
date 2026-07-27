from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from kiari.core.file_info_source import FileInfoSource

from .._types.watcher_name import WatcherName


class WatchEvent(BaseModel):
    watcher_name: WatcherName
    text: str = ""
    attachments: list[FileInfoSource] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
