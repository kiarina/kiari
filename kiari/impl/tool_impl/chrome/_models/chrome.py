from collections.abc import Awaitable, Callable
from typing import Literal

from kiarina.agi.content import Content
from kiarina.agi.tool import ToolContext, tool

from .._helpers.format_result import format_result
from .._operations.operations import (
    click,
    console_logs,
    dialog_respond,
    download_file,
    drag,
    go_back,
    go_forward,
    hover,
    instances,
    navigate,
    press_key,
    record_video,
    screenshot,
    select_option,
    snapshot,
    tab_activate,
    tab_close,
    tab_open,
    tab_select,
    tabs,
    type_text,
    upload_file,
    wait,
    wait_for,
)
from .._schemas.chrome_schema import ChromeSchema
from .._types.action import Action

Operation = Callable[[ToolContext, ChromeSchema], Awaitable[object]]

_OPERATIONS: dict[Action, Operation] = {
    "instances": instances,
    "tabs": tabs,
    "tab_open": tab_open,
    "tab_close": tab_close,
    "tab_select": tab_select,
    "tab_activate": tab_activate,
    "snapshot": snapshot,
    "dialog_respond": dialog_respond,
    "click": click,
    "hover": hover,
    "drag": drag,
    "upload_file": upload_file,
    "type": type_text,
    "select_option": select_option,
    "press_key": press_key,
    "navigate": navigate,
    "go_back": go_back,
    "go_forward": go_forward,
    "wait": wait,
    "wait_for": wait_for,
    "download_file": download_file,
    "record_video": record_video,
    "screenshot": screenshot,
    "console_logs": console_logs,
}


@tool(tool_schema=ChromeSchema)
async def Chrome(
    ctx: ToolContext,
    action: Action,
    browser_id: str | None = None,
    tab_id: int | None = None,
    url: str | None = None,
    active: bool = True,
    element: str | None = None,
    ref: str | None = None,
    text: str | None = None,
    submit: bool = False,
    values: list[str] | None = None,
    paths: list[str] | None = None,
    start_element: str | None = None,
    start_ref: str | None = None,
    end_element: str | None = None,
    end_ref: str | None = None,
    key: str | None = None,
    time: float | None = None,
    state: Literal["visible", "hidden"] = "visible",
    timeout: float = 10,
    filename: str | None = None,
    duration: float | None = None,
    video_filename: str | None = None,
    dialog_ref: str | None = None,
    dialog_action: Literal["accept", "dismiss"] | None = None,
    prompt_text: str | None = None,
) -> str | Content:
    args = ChromeSchema(
        action=action,
        browser_id=browser_id,
        tab_id=tab_id,
        url=url,
        active=active,
        element=element,
        ref=ref,
        text=text,
        submit=submit,
        values=values or [],
        paths=paths or [],
        start_element=start_element,
        start_ref=start_ref,
        end_element=end_element,
        end_ref=end_ref,
        key=key,
        time=time,
        state=state,
        timeout=timeout,
        filename=filename,
        duration=duration,
        video_filename=video_filename,
        dialog_ref=dialog_ref,
        dialog_action=dialog_action,
        prompt_text=prompt_text,
    )
    value = await _OPERATIONS[action](ctx, args)
    return await format_result(ctx, action, value)
