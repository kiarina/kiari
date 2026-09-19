from xml.sax.saxutils import escape

from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import HistoryCompactI18n
from .._operations.compact_history import compact_history
from .._schemas.history_compact_schema import HistoryCompactSchema


@tool(tool_schema=HistoryCompactSchema)
def HistoryCompact(
    ctx: ToolContext,
    context: str = "",
    narrative: str = "",
    referenced_file_paths: list[str] | None = None,
) -> str:
    t = get_i18n(HistoryCompactI18n, ctx.run_context.language)
    result = compact_history(ctx, t)

    sections: list[str] = []

    if context.strip():
        sections.append(f"<context>\n{escape(context.strip())}\n</context>")

    if narrative.strip():
        sections.append(f"<narrative>\n{escape(narrative.strip())}\n</narrative>")

    unique_paths = list(dict.fromkeys(referenced_file_paths or []))
    if unique_paths:
        paths = "\n".join(f"- {escape(path)}" for path in unique_paths)
        sections.append(f"<referenced_file_paths>\n{paths}\n</referenced_file_paths>")

    body = "\n\n".join(sections)
    return (
        f'<compacted_history removed_events="{result.removed_event_count}">\n'
        f"{body}\n"
        "</compacted_history>"
    )
