from kiarina.agi.file_info import FileID
from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import TextFilePurgeI18n
from .._schemas.text_file_purge_schema import TextFilePurgeSchema


@tool(tool_schema=TextFilePurgeSchema)
def TextFilePurge(ctx: ToolContext, ids: list[str]) -> str:
    t = get_i18n(TextFilePurgeI18n, ctx.run_context.language)

    unique_ids = list(dict.fromkeys(ids))
    file_infos_by_id = {file_info.id: file_info for file_info in ctx.history.file_infos}

    purged: list[FileID] = []
    not_found: list[FileID] = []
    not_text: list[FileID] = []

    for file_id in unique_ids:
        file_info = file_infos_by_id.get(file_id)

        if file_info is None:
            not_found.append(file_id)
        elif file_info.type != "text":
            not_text.append(file_id)
        else:
            ctx.history.remove_file_info(file_id)
            purged.append(file_id)

    lines = [t.result]

    if purged:
        lines.append(t.purged.format(ids=", ".join(purged)))
    if not_found:
        lines.append(t.not_found.format(ids=", ".join(not_found)))
    if not_text:
        lines.append(t.not_text.format(ids=", ".join(not_text)))

    return "\n".join(lines)
