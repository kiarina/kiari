import asyncio

from kiarina.agi.tool import ToolContext
from kiarina.i18n import get_i18n

from kiari.lib.gui import gui

from .._i18n import GuiI18n
from .._schemas.gui_schema import GuiSchema


async def mouse_click(ctx: ToolContext, args: GuiSchema) -> str:
    t = get_i18n(GuiI18n, ctx.run_context.language)

    if args.x != -1 and args.y != -1:
        gui.mouse.move(args.monitor_index, args.x, args.y, args.duration)
        await asyncio.sleep(args.duration + 0.3)

    gui.mouse.click(args.button)

    await asyncio.sleep(2.0)

    action_name = t.left_click if args.button == "left" else t.right_click

    return t.mouse_click_result.format(action_name=action_name)
