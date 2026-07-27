from pydantic import BaseModel, Field


class TextFileViewSchema(BaseModel):
    """
    View a text file.

    Example:
    {
        "file_path": "/path/to/file.txt",
        "start_line": 10,
        "end_line": 20
    }
    """

    file_path: str = Field(description="File path")

    start_line: int = Field(
        default=1,
        description="Start line of the viewing range (starting from 1, negative numbers specify from the end, -1 is the last line)",
    )

    end_line: int = Field(
        default=-1,
        description="End line of the viewing range (starting from 1, negative numbers specify from the end, -1 is the last line)",
    )
