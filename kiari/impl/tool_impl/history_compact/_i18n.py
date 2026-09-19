from kiarina.i18n import I18n


class HistoryCompactI18n(I18n, scope="kiari.impl.tool_impl.history_compact"):
    current_call_not_found_error: str = (
        "Error: The current history_compact tool call was not found in History"
    )
    current_call_not_last_error: str = (
        "Error: History contains events after the current history_compact tool call"
    )
    parallel_tool_calls_error: str = (
        "Error: history_compact must be the only tool call in its AI message"
    )
    human_message_not_found_error: str = (
        "Error: No HumanMessage was found before the current history_compact tool call"
    )
