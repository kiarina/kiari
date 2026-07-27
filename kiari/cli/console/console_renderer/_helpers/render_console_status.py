from pathlib import Path

from rich.console import Group, RenderableType
from rich.markup import escape
from rich.text import Text

from kiari.cli.console.console_handler._schemas.console_session import ConsoleSession
from kiari.core.profile import ProfileName, RunOptions


def render_console_status(
    session: ConsoleSession,
    *,
    profile_name: ProfileName,
    run_options: RunOptions,
) -> RenderableType:
    lines: list[RenderableType] = [
        Text(),
        _render_line(
            "App",
            [
                _format_item("profile", profile_name),
                _format_item(
                    "run_spec",
                    _format_run_spec_link(profile_name),
                    value_markup=True,
                ),
                _format_item(
                    "config",
                    _format_config_links(profile_name),
                    value_markup=True,
                ),
            ],
        ),
        _render_line(
            "Console",
            [
                _format_item("tts", session.tts_enabled, flag=True),
                _format_item("tts_model", _format_tts_model(run_options)),
                _format_item("stt", session.stt_enabled, flag=True),
                _format_item("audio_source", _format_audio_source(run_options)),
                _format_item("vad_model", _format_vad_model(run_options)),
                _format_item("asr_model", _format_asr_model(run_options)),
            ],
        ),
        _render_line(
            "RunContext",
            [
                _format_item("org", session.run_context.organization_id),
                _format_item("user", session.run_context.user_id),
                _format_item("agent", session.run_context.agent_id),
                _format_item("node", session.run_context.node_id),
                _format_item("tz", session.run_context.time_zone),
                _format_item("lang", session.run_context.language),
                _format_item("currency", session.run_context.currency),
            ],
        ),
        _render_line(
            "Flow",
            [
                _format_item("agent", _format_agent(run_options)),
                _format_item("workflow", _format_workflow(run_options)),
                _format_item("prompt", _format_prompt(run_options)),
                _format_item("chat_model", _format_chat_model(session)),
            ],
        ),
        _render_line(
            "History",
            [
                _format_item("history_repository", _format_history_repository(run_options)),
                _format_item("no_load", run_options.no_load, flag=True),
                _format_item("no_save", run_options.no_save, flag=True),
            ],
        ),
        _render_line(
            "Input",
            [
                _format_item(
                    "messages",
                    _format_messages(session),
                ),
                _format_item(
                    "custom_events",
                    _format_custom_events(session),
                ),
                _format_item(
                    "file_infos",
                    _format_file_infos(session),
                ),
                _format_item(
                    "pending_tool_calls",
                    _format_pending_tool_calls(session),
                ),
                _format_item(
                    "metadata",
                    _format_metadata(session),
                ),
            ],
        ),
        _render_line(
            "Output",
            [
                _format_item(
                    "tool_choice",
                    _format_tool_choice(session),
                ),
                _format_item(
                    "tool_infos",
                    _format_tool_infos(session),
                    value_markup=True,
                ),
            ],
        ),
        _render_line(
            "Tool",
            [
                _format_item(
                    "tools",
                    _format_tools(session),
                    value_markup=True,
                ),
            ],
        ),
        _render_line(
            "Hook",
            [
                _format_item(
                    "pre_hooks",
                    _format_pre_hooks(run_options),
                    value_markup=True,
                ),
                _format_item(
                    "post_hooks",
                    _format_post_hooks(run_options),
                    value_markup=True,
                ),
            ],
        ),
    ]

    lines.append(
        _render_line(
            "Condition",
            [
                _format_item(
                    "max_iterations",
                    _format_max_iterations(session),
                ),
                _format_item("until_end", session.agent_options.get("until_end"), flag=True),
                _format_item(
                    "until_tool_calls",
                    _format_until_tool_calls(session),
                    value_markup=True,
                ),
                _format_item(
                    "until_tool_runs",
                    _format_until_tool_runs(session),
                    value_markup=True,
                ),
            ],
        )
    )

    return Group(*lines)


def _render_line(label: str, parts: list[str]) -> RenderableType:
    label_text = f"{label:>10}:"

    return Text.from_markup(
        " ".join([f"[bold]{label_text}[/bold]", *parts]),
        style="blue",
    )


def _format_item(
    label: str,
    value: object,
    *,
    value_markup: bool = False,
    flag: bool = False,
) -> str:
    if flag:
        return f"{label}=[cyan]{'yes' if value else 'no'}[/cyan]"

    if value is None or value == "":
        value = "-"

    if value_markup:
        value_text = str(value)
    else:
        value_text = f"[cyan]{escape(str(value))}[/cyan]"

    return f"{label}={value_text}"


# --------------------------------------------------
# App
# --------------------------------------------------


def _format_run_spec_link(profile_name: ProfileName) -> str:
    from kiari.core.paths import get_profile_run_spec_file_path

    return _format_file_link("profile", get_profile_run_spec_file_path(profile_name))


def _format_config_links(profile_name: ProfileName) -> str:
    from kiari.core.paths import get_config_file_path, get_profile_config_file_path

    return ",".join(
        [
            _format_file_link("global", get_config_file_path()),
            _format_file_link("profile", get_profile_config_file_path(profile_name)),
        ]
    )


def _format_file_link(label: str, file_path: Path) -> str:
    uri = Path(file_path).absolute().as_uri()
    return f"[link={escape(uri)}][cyan]{escape(label)}[/cyan][/link]"


# --------------------------------------------------
# History
# --------------------------------------------------


def _format_history_repository(run_options: RunOptions) -> str:
    if run_options.history_repository:
        return run_options.history_repository

    from kiari.lib.history_repository import settings_manager

    return settings_manager.settings.default


# --------------------------------------------------
# Console
# --------------------------------------------------


def _format_tts_model(run_options: RunOptions) -> str:
    if run_options.tts_model:
        return _get_name(run_options.tts_model)

    from kiarina.agi.tts_model import settings_manager

    return _get_name(settings_manager.settings.default)


def _format_audio_source(run_options: RunOptions) -> str:
    if run_options.audio_source:
        return _get_name(run_options.audio_source)

    from kiarina.agi.audio_source import settings_manager

    return settings_manager.settings.default


def _format_vad_model(run_options: RunOptions) -> str:
    if run_options.vad_model:
        return _get_name(run_options.vad_model)

    from kiarina.agi.vad_model import settings_manager

    return _get_name(settings_manager.settings.default)


def _format_asr_model(run_options: RunOptions) -> str:
    if run_options.asr_model:
        return _get_name(run_options.asr_model)

    from kiarina.agi.asr_model import settings_manager

    return _get_name(settings_manager.settings.default)


# --------------------------------------------------
# Flow
# --------------------------------------------------


def _format_agent(run_options: RunOptions) -> str:
    if run_options.agent:
        return run_options.agent

    from kiarina.agi.agent import settings_manager

    return settings_manager.settings.default


def _format_workflow(run_options: RunOptions) -> str:
    if run_options.workflow:
        return run_options.workflow

    from kiarina.agi.workflow import settings_manager

    return settings_manager.settings.default


def _format_prompt(run_options: RunOptions) -> str:
    if run_options.prompt:
        return run_options.prompt

    from kiarina.agi.prompt import settings_manager

    return settings_manager.settings.default


def _format_chat_model(session: ConsoleSession) -> str:
    if session.chat_options and session.chat_options.get("chat_model"):
        return _get_name(session.chat_options.get("chat_model"))

    from kiarina.agi.chat_model import settings_manager

    return settings_manager.settings.default


# --------------------------------------------------
# Input
# --------------------------------------------------


def _format_messages(session: ConsoleSession) -> int:
    return len(
        [
            event
            for event in session.history.events
            if event.type in ("human_message", "ai_message", "tool_message")
        ]
    )


def _format_custom_events(session: ConsoleSession) -> int:
    return len([event for event in session.history.events if event.type == "custom"])


def _format_file_infos(session: ConsoleSession) -> str:
    file_info_count = len(session.history.file_infos)
    staged_count = len(session.attachments)

    if staged_count:
        return f"{file_info_count}+{staged_count}"

    return str(file_info_count)


def _format_pending_tool_calls(session: ConsoleSession) -> int:
    return len(session.history.get_pending_tool_calls())


def _format_metadata(session: ConsoleSession) -> int:
    return len(session.history.metadata)


# --------------------------------------------------
# Output
# --------------------------------------------------


def _format_tool_choice(session: ConsoleSession) -> str:
    if tool_choice := session.chat_options.get("tool_choice"):
        return tool_choice

    return "auto"


def _format_tool_infos(session: ConsoleSession) -> str:
    parts = [
        _format_tool_info_group(
            "active",
            [
                tool_info.name
                for tool_info in session.history.tool_infos
                if tool_info.state == "active"
            ],
        ),
        _format_tool_info_group(
            "inactive",
            [
                tool_info.name
                for tool_info in session.history.tool_infos
                if tool_info.state == "inactive"
            ],
        ),
        _format_tool_info_group(
            "disabled",
            [
                tool_info.name
                for tool_info in session.history.tool_infos
                if tool_info.state == "disabled"
            ],
        ),
    ]

    return ",".join(parts)


def _format_tool_info_group(state: str, names: list[str]) -> str:
    return f"{state}:{_format_names(names)}"


# --------------------------------------------------
# Tool
# --------------------------------------------------


def _format_tools(session: ConsoleSession) -> str:
    return _format_names(_get_tool_names(session))


def _get_tool_names(session: ConsoleSession) -> list[str]:
    if session.tool_options and session.tool_options.get("tools"):
        return [_get_name(tool) for tool in session.tool_options.get("tools") or []]

    return []


# --------------------------------------------------
# Hook
# --------------------------------------------------


def _format_pre_hooks(run_options: RunOptions) -> str:
    return _format_names(_get_pre_hook_names(run_options))


def _format_post_hooks(run_options: RunOptions) -> str:
    return _format_names(_get_post_hook_names(run_options))


def _get_pre_hook_names(run_options: RunOptions) -> list[str]:
    return [_get_hook_name(hook) for hook in run_options.pre_hooks]


def _get_post_hook_names(run_options: RunOptions) -> list[str]:
    return [_get_hook_name(hook) for hook in run_options.post_hooks]


def _get_hook_name(value: str) -> str:
    specifier, separator, binding_target = value.partition("@")
    hook_name = specifier.split("?", 1)[0]

    if not separator:
        return hook_name

    return f"{hook_name}@{binding_target}"


# --------------------------------------------------
# Condition
# --------------------------------------------------


def _format_max_iterations(session: ConsoleSession) -> int:
    if max_iterations := session.agent_options.get("max_iterations"):
        return max_iterations

    from kiarina.agi.agent import settings_manager

    return settings_manager.settings.max_iterations


def _format_until_tool_calls(session: ConsoleSession) -> str:
    return _format_names(session.agent_options.get("until_tool_calls") or [])


def _format_until_tool_runs(session: ConsoleSession) -> str:
    return _format_names(session.agent_options.get("until_tool_runs") or [])


# --------------------------------------------------
# Utilities
# --------------------------------------------------


def _get_name(value: object) -> str:
    if isinstance(value, str):
        return value.split("?", 1)[0]

    if name := getattr(value, "name", None):
        return str(name)

    return str(value)


def _format_names(values: list[str]) -> str:
    if not values:
        return "[cyan]-[/cyan]"

    return ",".join([f"[cyan]{escape(value)}[/cyan]" for value in values])
