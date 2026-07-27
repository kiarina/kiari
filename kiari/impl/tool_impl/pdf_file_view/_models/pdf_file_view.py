from kiarina.agi.content import Content
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import PdfFileViewI18n
from .._schemas.pdf_file_view_schema import PdfFileViewSchema


@tool(tool_schema=PdfFileViewSchema)
async def PdfFileView(
    ctx: ToolContext,
    uri_or_file_path: str,
    start_page: int = 1,
    end_page: int = -1,
) -> Content:
    t = get_i18n(PdfFileViewI18n, ctx.run_context.language)

    file_info = await load_file_info(
        {
            "uri_or_file_path": uri_or_file_path,
            "start_page": start_page,
            "end_page": end_page,
        },
        run_context=ctx.run_context,
    )

    if file_info is None:
        return Content(text=t.not_found_error.format(uri_or_file_path=uri_or_file_path))

    if file_info.type != "pdf":
        return Content(text=t.not_pdf_error.format(uri_or_file_path=uri_or_file_path))

    return Content(text=t.result, files=[file_info])
