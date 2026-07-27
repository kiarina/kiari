from collections.abc import Awaitable, Callable

from kiarina.agi.content import Content
from kiarina.agi.file_factory import create_file
from kiarina.agi.file_info import FileInfo
from kiarina.agi.tool import ToolContext, tool

from kiari.lib.gui import gui

from .._operations.keyboard_hotkey import keyboard_hotkey
from .._operations.keyboard_press import keyboard_press
from .._operations.keyboard_write import keyboard_write
from .._operations.mouse_click import mouse_click
from .._operations.mouse_down import mouse_down
from .._operations.mouse_move import mouse_move
from .._operations.mouse_up import mouse_up
from .._operations.screenshot import screenshot
from .._schemas.gui_schema import GuiSchema
from .._types.action import Action

_OPERATIONS: dict[Action, Callable[[ToolContext, GuiSchema], Awaitable[str]]] = {
    "keyboard_press": keyboard_press,
    "keyboard_hotkey": keyboard_hotkey,
    "keyboard_write": keyboard_write,
    "mouse_click": mouse_click,
    "mouse_down": mouse_down,
    "mouse_move": mouse_move,
    "mouse_up": mouse_up,
    "screenshot": screenshot,
}


@tool(tool_schema=GuiSchema)
async def Gui(
    ctx: ToolContext,
    action: Action,
    # Keyboard related
    key: str = "",
    keys: list[str] | None = None,
    text: str = "",
    # Mouse related
    button: str = "left",
    monitor_index: int = 1,
    x: int = -1,
    y: int = -1,
    duration: float = 0.0,
) -> Content:
    args = GuiSchema(
        action=action,
        key=key,
        keys=keys or [],
        text=text,
        button=button,
        monitor_index=monitor_index,
        x=x,
        y=y,
        duration=duration,
    )

    output = await _OPERATIONS[action](ctx, args)

    file_infos: list[FileInfo] = []

    gui.monitor.refresh()

    for monitor_idx in gui.monitor.monitor_indexes:
        mime_blob = gui.monitor.get_screenshot(monitor_idx)

        result = await create_file(
            ctx.tool_call.name,
            mime_blob,
            file_info_spec_overrides={"name": f"Monitor {monitor_idx} Screenshot"},
            run_context=ctx.run_context,
        )

        file_infos.append(result.file_info)

    return Content(text=output, files=file_infos)
