from collections.abc import Callable
from typing import Literal

import questionary
from kiarina.agi.run_context import RunContext
from kiarina.i18n import get_i18n

from kiari.core.rich import console_registry
from kiari.core.terminal import create_prompt_toolkit_io

from .._i18n import EditorI18n
from .._schemas.validation_result import ValidationResult
from .edit_text import edit_text


async def edit_text_with_validation(
    initial: str,
    *,
    validator: Callable[[str], ValidationResult],
    extension: str = ".txt",
    editing_mode: Literal["vi", "emacs"] | None = None,
    max_inline_lines: int = 200,
    max_inline_chars: int = 5000,
) -> str | None:
    text = initial

    while True:
        edited = await edit_text(
            text,
            extension=extension,
            editing_mode=editing_mode,
            max_inline_lines=max_inline_lines,
            max_inline_chars=max_inline_chars,
        )

        if edited is None:
            return None

        result = validator(edited)

        if result.valid:
            return edited

        if result.message is not None:
            console_registry.get().print(result.message)

        t = get_i18n(EditorI18n, RunContext().language)

        choice = await questionary.select(
            t.validation_failed_prompt,
            choices=[
                questionary.Choice(title=t.choice_continue, value="continue"),
                questionary.Choice(title=t.choice_reset, value="reset"),
                questionary.Choice(title=t.choice_abort, value="abort"),
            ],
            use_jk_keys=False,
            **create_prompt_toolkit_io(),
        ).ask_async()

        if choice == "continue":
            text = edited
            continue

        if choice == "reset":
            text = initial
            continue

        return None
