import asyncio

from kiarina.agi.tool import ToolContext
from kiarina.i18n import get_i18n

from .._i18n import GuiI18n
from .._schemas.gui_schema import GuiSchema


async def screenshot(ctx: ToolContext, args: GuiSchema) -> str:
    t = get_i18n(GuiI18n, ctx.run_context.language)

    await asyncio.sleep(0.5)

    return t.screenshot_result
