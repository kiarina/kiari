import asyncio
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Literal

from kiarina.agi import asr_model, tts_model
from kiarina.agi.agent import run_agent
from kiarina.agi.audio_source import AudioChunk, audio_source_registry
from kiarina.agi.vad_model import vad_model_registry
from kiarina.agi.voice_detector import Voice, create_voice_detector
from kiarina.i18n import get_i18n, get_system_language
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.enums import EditingMode

from kiari.core.profile import ProfileName, RunOptions
from kiari.core.rich import console_registry
from kiari.core.terminal import (
    has_interactive_tty,
    prompt_session_registry,
    stop_asyncio_on_enter,
    stop_threading_on_enter,
)
from kiari.lib.audio_utils import play_audio

from .._i18n import ConsoleI18n
from .._services.console_completer import ConsoleCompleter
from ..console_handler import ConsoleRequest, ConsoleSession, console_handler_registry
from ..console_state import ConsoleState
from ..console_text import parse_console_text
from ..slash_command import slash_command_registry

InputMode = Literal["keyboard", "voice"]


async def run_console(
    profile_name: ProfileName,
    run_options: RunOptions,
    request: ConsoleRequest | None = None,
) -> None:
    if not has_interactive_tty():
        t = get_i18n(ConsoleI18n, run_options.language or get_system_language())
        console_registry.get().print(t.no_interactive_terminal_error, style="red")
        return

    handler = console_handler_registry.resolve(
        run_options.console_handler,
        profile_name=profile_name,
        run_options=run_options,
    )

    async with handler.handle_session() as session:
        state: ConsoleState = "user" if request is None else "agent"
        input_mode: InputMode = "voice" if session.stt_enabled else "keyboard"

        while True:
            match state:
                case "user":
                    if renderable := handler.render_ui(session):
                        console_registry.get().print(renderable)

                    try:
                        if input_mode == "keyboard":
                            state = await _read_keyboard_input(run_options, session)

                        elif input_mode == "voice":
                            state = await _read_voice_input(run_options, session)

                            if not session.text:
                                input_mode = "keyboard"

                        else:  # pragma: no cover
                            raise AssertionError(f"Unknown input mode: {input_mode}")

                    except KeyboardInterrupt:
                        state = "end"

                case "command":
                    console_text = parse_console_text(session.text)

                    if console_text.command_specifier:
                        command_name = console_text.command_specifier.split("?", 1)[0]
                        registered_commands = set(slash_command_registry.list_names()) | set(
                            slash_command_registry.list_aliases()
                        )

                        if command_name not in registered_commands:
                            t = get_i18n(
                                ConsoleI18n,
                                run_options.language or get_system_language(),
                            )
                            console_registry.get().print(
                                t.unknown_command_help.format(command_name=command_name),
                                style="red",
                            )
                            session.text = ""
                            state = "user"
                            continue

                        command = slash_command_registry.resolve(
                            console_text.command_specifier,
                            profile_name=profile_name,
                            run_options=run_options,
                        )
                        session.text = ""
                        state = await command.run(
                            session,
                            console_text.command_args,
                            console_text.content,
                        )

                        if command.name == "stt":
                            input_mode = "voice" if session.stt_enabled else "keyboard"

                    else:
                        state = "agent"

                case "agent":
                    if not request:
                        console_text = parse_console_text(session.text)

                        request = ConsoleRequest(
                            text=console_text.content,
                            attachments=session.attachments,
                        )

                    async with handler.handle_request(session, request):
                        with stop_asyncio_on_enter() as stop_event:
                            async for event in run_agent(
                                **session.as_run_agent_kwargs(),
                                stop_event=stop_event,
                            ):
                                await handler.on_agent_event(session, event)
                                session.last_event = event

                    await _text_to_speech(run_options, session)

                    if session.stt_enabled:
                        input_mode = "voice"

                    request = None
                    state = "user"

                case "end":
                    break

                case _:  # pragma: no cover
                    raise AssertionError(f"Invalid console state: {state}")


async def _read_keyboard_input(run_options: RunOptions, session: ConsoleSession) -> ConsoleState:
    value = str(
        await prompt_session_registry.get().prompt_async(
            "> ",
            multiline=True,
            auto_suggest=AutoSuggestFromHistory(),
            completer=ConsoleCompleter(),
            editing_mode=EditingMode.VI if run_options.editing_mode == "vi" else EditingMode.EMACS,
            default=session.text,
        )
    )

    session.text = value.strip()
    return "command" if session.text else "agent"


async def _read_voice_input(run_options: RunOptions, session: ConsoleSession) -> ConsoleState:
    texts: list[str] = []

    console_registry.get().print("[dim]Listening. Press Enter to send.[/dim]")

    with stop_asyncio_on_enter() as stop_event:
        while not stop_event.is_set():
            async for speech in _detect_voice_input(
                audio_source_specifier=run_options.audio_source,
                vad_model_specifier=run_options.vad_model,
                stop_event=stop_event,
                idle_timeout=run_options.stt_auto_send_after,
            ):
                text = await asr_model.speech_to_text(
                    speech.samples,
                    speech.sample_rate,
                    asr_options={"asr_model": run_options.asr_model},
                    cost_recorder=session.cost_recorder,
                    run_context=session.run_context,
                )

                if text := text.strip():
                    texts.append(text)
                    console_registry.get().print(f"[dim]STT:[/dim] {text}")

            if texts or run_options.stt_auto_send_after is None:
                break

    session.text = "\n\n".join(texts).strip()
    return "agent" if session.text else "user"


async def _detect_voice_input(
    *,
    audio_source_specifier: str | None,
    vad_model_specifier: str | None,
    stop_event: asyncio.Event,
    idle_timeout: float | None,
) -> AsyncIterator[Voice]:
    audio_source = audio_source_registry.resolve(audio_source_specifier)
    vad_model = vad_model_registry.resolve(vad_model_specifier)
    voice_detector = create_voice_detector(vad_model)

    idle_stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    idle_deadline: float | None = None

    async with audio_source.open(None):
        audio_iter = aiter(audio_source.read(stop_event, idle_stop_event))

        while not stop_event.is_set():
            audio_task: asyncio.Future[AudioChunk] | None = None

            try:
                if idle_deadline is None:
                    chunk = await anext(audio_iter)

                else:
                    timeout = idle_deadline - loop.time()

                    if timeout <= 0:
                        idle_stop_event.set()
                        break

                    audio_task = asyncio.ensure_future(anext(audio_iter))
                    chunk = await asyncio.wait_for(
                        asyncio.shield(audio_task),
                        timeout=timeout,
                    )

            except TimeoutError:
                idle_stop_event.set()

                if audio_task is not None:
                    with suppress(StopAsyncIteration, asyncio.CancelledError):
                        await audio_task

                break

            except StopAsyncIteration:
                break

            result = await voice_detector.detect(chunk.samples, chunk.sample_rate, chunk.timestamp)

            if idle_deadline is not None and idle_timeout is not None and result.is_voice:
                idle_deadline = loop.time() + idle_timeout

            if result.voice is not None:
                yield result.voice

                if idle_timeout is not None:
                    idle_deadline = loop.time() + idle_timeout

    if voice := voice_detector.flush():
        yield voice


async def _text_to_speech(run_options: RunOptions, session: ConsoleSession) -> None:
    if (
        not session.tts_enabled
        or not session.last_event
        or session.last_event.type != "ai_message"
        or session.last_event.message.tool_calls
    ):
        return

    text = session.last_event.to_text().strip()

    if not text:
        return

    audio_file_path = await tts_model.text_to_speech(
        text,
        tts_options={"tts_model": run_options.tts_model},
        cost_recorder=session.cost_recorder,
        run_context=session.run_context,
    )

    console_registry.get().print("[dim]Press Enter to stop audio playback.[/dim]")

    with stop_threading_on_enter() as stop_event:
        await play_audio(audio_file_path, blocking=True, stop_event=stop_event)
