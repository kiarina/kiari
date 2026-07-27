from pydantic import BaseModel, Field


class ImageGenerateSchema(BaseModel):
    """
    Generate an image from a text prompt.

    Example:
    {
        "prompt": "An illustration of a cat reading a book"
    }
    """

    prompt: str = Field(description="Text prompt describing the image to generate")
