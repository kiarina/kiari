from pydantic import BaseModel, Field


class ChangeDirectorySchema(BaseModel):
    """
    Changes the current directory to the specified path
    """

    dir_path: str = Field(description="Path to the target directory")
