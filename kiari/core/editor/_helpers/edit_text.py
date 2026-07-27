import asyncio
from typing import Any, Literal, cast

import click
from prompt_toolkit.enums import EditingMode

from kiari.core.terminal import prompt_session_registry


async def edit_text(
    initial: str,
    *,
    extension: str = ".txt",
    editing_mode: Literal["vi", "emacs"] | None = None,
    max_inline_lines: int = 200,
    max_inline_chars: int = 5000,
) -> str | None:
    if _is_inline_editable(
        initial,
        max_lines=max_inline_lines,
        max_chars=max_inline_chars,
    ):
        return await _edit_with_prompt_toolkit(initial, editing_mode=editing_mode)

    return await _edit_with_external_editor(initial, extension=extension)


def _is_inline_editable(text: str, *, max_lines: int, max_chars: int) -> bool:
    return len(text) < max_chars and text.count("\n") + 1 < max_lines


async def _edit_with_prompt_toolkit(
    initial: str,
    *,
    editing_mode: Literal["vi", "emacs"] | None,
) -> str | None:
    kwargs: dict[str, Any] = {}

    if editing_mode is not None:
        kwargs["editing_mode"] = EditingMode.VI if editing_mode == "vi" else EditingMode.EMACS

    try:
        return await prompt_session_registry.get("no_history").prompt_async(
            multiline=True,
            bottom_toolbar="[Meta+Enter] submit  [Ctrl-C] cancel",
            default=initial,
            **kwargs,
        )

    except (KeyboardInterrupt, EOFError):
        return None


async def _edit_with_external_editor(
    initial: str,
    *,
    extension: str,
) -> str | None:
    return cast(
        str | None,
        await asyncio.to_thread(
            click.edit,
            text=initial,
            extension=extension,
            require_save=True,
        ),
    )
