from pydantic import BaseModel, Field


class VideoPredictSchema(BaseModel):
    """
    Generate a video from a text prompt.

    Examples:
    {
        "prompt": "A short video of a cat playing with a ball"
    }

    {
        "prompt": "Animate this illustration",
        "first_image_file_path": "/path/to/first-frame.png"
    }
    """

    prompt: str = Field(description="Text prompt describing the video to generate")
    first_image_file_path: str | None = Field(
        default=None,
        description="Optional local image file path to use as the first frame",
    )
