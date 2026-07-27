from kiarina.agi.content import Content
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import ImageFileViewI18n
from .._schemas.image_file_view_schema import ImageFileViewSchema


@tool(tool_schema=ImageFileViewSchema)
async def ImageFileView(
    ctx: ToolContext,
    uri_or_file_path: str,
) -> Content:
    t = get_i18n(ImageFileViewI18n, ctx.run_context.language)

    file_info = await load_file_info(
        uri_or_file_path,
        run_context=ctx.run_context,
    )

    if file_info is None:
        return Content(text=t.not_found_error.format(uri_or_file_path=uri_or_file_path))

    if file_info.type != "image":
        return Content(text=t.not_image_error.format(uri_or_file_path=uri_or_file_path))

    return Content(text=t.result, files=[file_info])
