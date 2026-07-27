from typing import Literal

from pydantic import BaseModel, Field

from .file_change import FileChange


class FileWatchPayload(BaseModel):
    type: Literal["file_changes"] = "file_changes"
    changes: list[FileChange] = Field(default_factory=list)
