from kiarina.agi.event_builder import parse_event_specifier
from kiarina.agi.history import History
from kiarina.agi.history_builder import build_history
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolSpecifier, tool_registry

from kiari.core.file_info_source import resolve_file_info_specifiers
from kiari.core.profile import RunOptions
from kiari.lib.history_repository import history_repository_registry


async def setup_history(
    run_options: RunOptions,
    run_context: RunContext,
) -> History:
    if run_options.no_load:
        return await _build_default_history(run_options, run_context)

    if history := await _load_history(run_options, run_context):
        return _resume_history(history, run_options, run_context)
    else:
        return await _build_default_history(run_options, run_context)


async def _build_default_history(
    run_options: RunOptions,
    run_context: RunContext,
) -> History:
    history = await build_history(
        {
            "events": [
                parse_event_specifier(event_specifier) for event_specifier in run_options.events
            ],
            "file_infos": await resolve_file_info_specifiers(run_options.file_infos),
            "tool_infos": run_options.tool_infos,
        },
        run_context=run_context,
    )

    _merge_missing_tool_infos(history, run_options, run_context)

    return history


async def _load_history(
    run_options: RunOptions,
    run_context: RunContext,
) -> History | None:
    history_repository = history_repository_registry.resolve(run_options.history_repository)

    return await history_repository.load(run_context)


def _resume_history(
    history: History,
    run_options: RunOptions,
    run_context: RunContext,
) -> History:
    if not run_options.allow_active_missing_tools:
        _disable_missing_active_tool_infos(history, run_options)

    _merge_missing_tool_infos(history, run_options, run_context)

    return history


def _disable_missing_active_tool_infos(
    history: History,
    run_options: RunOptions,
) -> None:
    tool_names = {_get_tool_name(tool_specifier) for tool_specifier in run_options.tools}

    for tool_info in history.tool_infos:
        if tool_info.state == "active" and tool_info.name not in tool_names:
            tool_info.state = "disabled"


def _merge_missing_tool_infos(
    history: History,
    run_options: RunOptions,
    run_context: RunContext,
) -> None:
    for tool_specifier in run_options.tools:
        tool_name = _get_tool_name(tool_specifier)

        if not history.get_tool_info(tool_name):
            tool = tool_registry.resolve(tool_specifier)
            tool_info = tool.to_tool_info(run_context.language)
            tool_info.state = run_options.default_tool_state
            history.add_tool_info(tool_info)


def _get_tool_name(specifier: ToolSpecifier) -> str:
    return specifier.split("?", 1)[0] if "?" in specifier else specifier
