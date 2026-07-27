from pydantic import BaseModel, Field


class PdfFileViewSchema(BaseModel):
    """
    View a PDF file.

    To view a specific range of pages, specify start_page and end_page.

    Example 1. To view the entire PDF file:
    {
        "uri_or_file_path": "/path/to/file.pdf"
    }

    Example 2. To view a specific range of pages in the PDF file:
    {
        "uri_or_file_path": "/path/to/file.pdf",
        "start_page": 2,
        "end_page": 5
    }
    """

    uri_or_file_path: str = Field(description="URI or local file path of the file to view")

    start_page: int = Field(
        default=1,
        description="Start page of the viewing range (starting from 1, negative numbers specify from the end. -1 is the last page)",
    )

    end_page: int = Field(
        default=-1,
        description="End page of the viewing range (starting from 1, negative numbers specify from the end. -1 is the last page)",
    )
