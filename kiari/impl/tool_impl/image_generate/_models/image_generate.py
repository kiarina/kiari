from kiarina.agi.content import Content
from kiarina.agi.file_factory import create_file
from kiarina.agi.image_generation_model import generate_image
from kiarina.agi.tool import ToolContext, tool
from kiarina.i18n import get_i18n

from .._i18n import ImageGenerateI18n
from .._schemas.image_generate_schema import ImageGenerateSchema


@tool(tool_schema=ImageGenerateSchema)
async def ImageGenerate(
    ctx: ToolContext,
    prompt: str,
) -> Content:
    t = get_i18n(ImageGenerateI18n, ctx.run_context.language)

    result = await generate_image(
        prompt,
        cost_recorder=ctx.cost_recorder,
        run_context=ctx.run_context,
    )

    build_result = await create_file(
        ctx.tool_call.name,
        result.mime_blob,
        run_context=ctx.run_context,
    )

    return Content(text=t.result, files=[build_result.file_info])
