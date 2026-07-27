from kiarina.agi.content import Content
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import VideoFileViewI18n
from .._schemas.video_file_view_schema import VideoFileViewSchema


@tool(tool_schema=VideoFileViewSchema)
async def VideoFileView(
    ctx: ToolContext,
    uri_or_file_path: str,
    start_time: float = 0.0,
    end_time: float = -1.0,
) -> Content:
    t = get_i18n(VideoFileViewI18n, ctx.run_context.language)

    file_info = await load_file_info(
        {
            "uri_or_file_path": uri_or_file_path,
            "start_time": start_time,
            "end_time": end_time,
        },
        run_context=ctx.run_context,
    )

    if file_info is None:
        return Content(text=t.not_found_error.format(uri_or_file_path=uri_or_file_path))

    if file_info.type != "video":
        return Content(text=t.not_video_error.format(uri_or_file_path=uri_or_file_path))

    return Content(text=t.result, files=[file_info])
