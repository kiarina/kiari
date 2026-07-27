import asyncio

from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from kiari.lib.gui import gui

from .._i18n import GuiI18n
from .._schemas.gui_schema import GuiSchema


async def keyboard_hotkey(ctx: ToolContext, args: GuiSchema) -> str:
    t = get_i18n(GuiI18n, ctx.run_context.language)

    if not args.keys:
        raise ToolError(t.keyboard_hotkey_requires_keys_error)

    gui.keyboard.hotkey(*args.keys)

    await asyncio.sleep(1.0)

    return t.keyboard_hotkey_result.format(keys=args.keys)
