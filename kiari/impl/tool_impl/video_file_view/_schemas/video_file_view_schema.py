from pydantic import BaseModel, Field


class VideoFileViewSchema(BaseModel):
    """
    View a video file.

    To view a specific time range, specify start_time and end_time.

    Example 1. To view the entire video file:
    {
        "uri_or_file_path": "/path/to/file.mp4"
    }

    Example 2. To view a specific time range of the video file:
    {
        "uri_or_file_path": "/path/to/file.mp4",
        "start_time": 10.0,
        "end_time": 30.0
    }
    """

    uri_or_file_path: str = Field(description="URI or local file path of the file to view")

    start_time: float = Field(
        default=0.0,
        description="Start time of the viewing range (in seconds, negative numbers specify from the end, -1.0 is the last time)",
    )

    end_time: float = Field(
        default=-1.0,
        description="End time of the viewing range (in seconds, negative numbers specify from the end, -1.0 is the last time)",
    )
