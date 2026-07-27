from pydantic import BaseModel

from .._types.change_type import ChangeType


class FileChange(BaseModel, frozen=True):
    change_type: ChangeType
    file_path: str
