from typing import Self

from pydantic import BaseModel, Field, model_validator


class HistoryCompactSchema(BaseModel):
    """
    Compact prior History events into one tool result.

    Call this tool alone in its AI message. Describe the durable current state in
    context, explain important preceding events and decisions in narrative, and list
    file paths that may need to be revisited. The compact request, this tool call, and
    the resulting ToolMessage become the new conversation history. FileInfo values and
    underlying files are not deleted.
    """

    context: str = Field(
        default="",
        description=(
            "Current goal, constraints, decisions, state, unresolved issues, and next steps. "
            "Either context or narrative must contain non-whitespace text."
        ),
    )
    narrative: str = Field(
        default="",
        description=(
            "Concise causal account of relevant attempts, results, and reasons for decisions. "
            "Either context or narrative must contain non-whitespace text."
        ),
    )
    referenced_file_paths: list[str] = Field(
        default_factory=list,
        description="File paths that remain relevant after compaction.",
    )

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        if not self.context.strip() and not self.narrative.strip():
            raise ValueError("context or narrative must contain non-whitespace text")

        return self
