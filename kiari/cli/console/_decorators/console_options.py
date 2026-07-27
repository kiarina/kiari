import functools
from collections.abc import Callable
from typing import Any, Literal

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from .._i18n import ConsoleI18n

t = get_i18n(ConsoleI18n, get_system_language())


def console_options[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    # fmt: off
    @click.option("--console-handler", type=str, help=t.console_handler_help)
    @click.option("--editing-mode", type=click.Choice(["vi", "emacs"]), callback=_set_editing_mode_option, help=t.editing_mode_help)
    @click.option("--vi", is_flag=True, default=None, is_eager=True, expose_value=False, callback=_set_vi, help=t.vi_help)
    @click.option("--emacs", is_flag=True, default=None, is_eager=True, expose_value=False, callback=_set_emacs, help=t.emacs_help)
    @click.option("--stt/--no-stt", default=None, help=t.stt_help)
    @click.option("--stt-auto-send-after", type=float, help=t.stt_auto_send_after_help)
    @click.option("--audio-source", type=str, help=t.audio_source_help)
    @click.option("--vad-model", type=str, help=t.vad_model_help)
    @click.option("--asr-model", type=str, help=t.asr_model_help)
    @click.option("--tts/--no-tts", default=None, help=t.tts_help)
    @click.option("--tts-model", type=str, help=t.tts_model_help)
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # fmt: on
        return func(*args, **kwargs)

    return wrapper


def _set_vi(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if value:
        _set_editing_mode(ctx, "vi")

    return value


def _set_emacs(ctx: click.Context, _: click.Parameter, value: Any) -> Any:
    if value:
        _set_editing_mode(ctx, "emacs")

    return value


def _set_editing_mode_option(
    ctx: click.Context,
    _: click.Parameter,
    value: Literal["vi", "emacs"] | None,
) -> Literal["vi", "emacs"] | None:
    if value is not None:
        _set_editing_mode(ctx, value)

    return value


def _set_editing_mode(ctx: click.Context, editing_mode: Literal["vi", "emacs"]) -> None:
    existing = ctx.params.get("editing_mode")

    if existing is not None and existing != editing_mode:
        raise click.UsageError("Cannot specify both --vi and --emacs.")

    ctx.params["editing_mode"] = editing_mode
