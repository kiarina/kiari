import asyncio

from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from kiari.lib.gui import gui

from .._i18n import GuiI18n
from .._schemas.gui_schema import GuiSchema


async def mouse_move(ctx: ToolContext, args: GuiSchema) -> str:
    t = get_i18n(GuiI18n, ctx.run_context.language)

    if args.x == -1 or args.y == -1:
        raise ToolError(t.mouse_move_requires_coordinates_error)

    gui.mouse.move(args.monitor_index, args.x, args.y, args.duration)

    await asyncio.sleep(args.duration + 0.3)

    return t.mouse_move_result.format(
        monitor_index=args.monitor_index,
        x=args.x,
        y=args.y,
        duration=args.duration,
    )
