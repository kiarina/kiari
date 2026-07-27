from pydantic import BaseModel, Field

from kiari.core.file_info_source import FileInfoSource


class StreamlitRequest(BaseModel):
    text: str = ""
    attachments: list[FileInfoSource] = Field(default_factory=list)
