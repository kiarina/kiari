from typing import Any, Self

from pydantic import BaseModel, Field, model_validator


class RequestBody(BaseModel):
    text: str = ""
    files: list[str] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)
    run_kwargs: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_input(self) -> Self:
        if not self.text and not self.files and not self.events:
            raise ValueError("At least one of text, files, or events must be provided")

        return self
