from dataclasses import dataclass

from kiarina.agi.event import AIMessageEvent
from kiarina.agi.tool import ToolContext, ToolError

from .._i18n import HistoryCompactI18n


@dataclass(frozen=True)
class CompactHistoryResult:
    removed_event_count: int


def compact_history(
    ctx: ToolContext,
    t: HistoryCompactI18n,
) -> CompactHistoryResult:
    events = ctx.history.events

    ai_event_index: int | None = None
    current_ai_event: AIMessageEvent | None = None

    for index, event in enumerate(events):
        if event.type != "ai_message":
            continue

        if any(tool_call.id == ctx.tool_call.id for tool_call in event.message.tool_calls):
            ai_event_index = index
            current_ai_event = event
            break

    if ai_event_index is None or current_ai_event is None:
        raise ToolError(t.current_call_not_found_error)

    if ai_event_index != len(events) - 1:
        raise ToolError(t.current_call_not_last_error)

    if (
        len(current_ai_event.message.tool_calls) != 1
        or current_ai_event.message.tool_calls[0].id != ctx.tool_call.id
        or current_ai_event.message.tool_calls[0].name != ctx.tool_call.name
    ):
        raise ToolError(t.parallel_tool_calls_error)

    human_event_index: int | None = None

    for index in range(ai_event_index - 1, -1, -1):
        if events[index].type == "human_message":
            human_event_index = index
            break

    if human_event_index is None:
        raise ToolError(t.human_message_not_found_error)

    current_tool_call = current_ai_event.message.tool_calls[0]
    current_tool_call.args.clear()

    if current_tool_call is not ctx.tool_call:
        ctx.tool_call.args.clear()

    removed_event_count = len(events) - 2
    ctx.history.events = [events[human_event_index], current_ai_event]

    return CompactHistoryResult(removed_event_count=removed_event_count)
