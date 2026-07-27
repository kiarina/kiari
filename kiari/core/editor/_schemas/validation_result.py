from dataclasses import dataclass

from rich.console import RenderableType


@dataclass(frozen=True)
class ValidationResult:
    """Result returned by a validator passed to ``edit_text_with_validation``.

    Attributes:
        valid: Whether the edited text passed validation.
        message: Optional renderable to print when validation fails (e.g.
            an error description). Ignored when ``valid`` is ``True``.
    """

    valid: bool
    message: RenderableType | None = None
