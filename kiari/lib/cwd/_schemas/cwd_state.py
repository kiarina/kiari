import os

from pydantic import BaseModel, Field


class CWDState(BaseModel):
    current_directory: str = Field(default_factory=os.getcwd)
