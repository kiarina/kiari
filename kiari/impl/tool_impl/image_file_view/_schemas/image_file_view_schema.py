from pydantic import BaseModel, Field


class ImageFileViewSchema(BaseModel):
    """
    View an image file.

    Example. To view an image file:
    {
        "uri_or_file_path": "/path/to/file.png"
    }
    """

    uri_or_file_path: str = Field(description="URI or local file path of the file to view")
