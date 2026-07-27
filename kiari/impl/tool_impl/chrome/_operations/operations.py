import math
from typing import Any

from kiarina.agi.tool import ToolContext, ToolError

from .._helpers.session import chrome_session
from .._schemas.chrome_schema import ChromeSchema


def _required(value: Any, name: str, action: str) -> Any:
    if value is None or value == "":
        raise ToolError(f"{action} action requires {name}")
    return value


def _in_range(value: float, name: str, action: str, minimum: float, maximum: float) -> float:
    if not math.isfinite(value) or not minimum <= value <= maximum:
        raise ToolError(f"{action} action requires {name} from {minimum:g} through {maximum:g}")
    return value


async def instances(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_instances()


async def tabs(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_tabs(browser_id=args.browser_id)


async def tab_open(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_tab_open(
            url=args.url or "about:blank", active=args.active, browser_id=args.browser_id
        )


async def tab_close(ctx: ToolContext, args: ChromeSchema) -> object:
    tab_id = _required(args.tab_id, "tab_id", args.action)
    async with chrome_session() as session:
        return await session.browser_tab_close(tab_id=tab_id, browser_id=args.browser_id)


async def tab_select(ctx: ToolContext, args: ChromeSchema) -> object:
    tab_id = _required(args.tab_id, "tab_id", args.action)
    async with chrome_session() as session:
        return await session.browser_tab_select(tab_id=tab_id, browser_id=args.browser_id)


async def tab_activate(ctx: ToolContext, args: ChromeSchema) -> object:
    tab_id = _required(args.tab_id, "tab_id", args.action)
    async with chrome_session() as session:
        return await session.browser_tab_activate(tab_id=tab_id, browser_id=args.browser_id)


async def snapshot(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_snapshot(browser_id=args.browser_id)


async def dialog_respond(ctx: ToolContext, args: ChromeSchema) -> object:
    dialog_ref = _required(args.dialog_ref, "dialog_ref", args.action)
    dialog_action = _required(args.dialog_action, "dialog_action", args.action)
    if dialog_action == "dismiss" and args.prompt_text is not None:
        raise ToolError("dialog_respond action accepts prompt_text only with accept")
    async with chrome_session() as session:
        return await session.browser_dialog_respond(
            dialog_ref=dialog_ref,
            action=dialog_action,
            prompt_text=args.prompt_text,
            browser_id=args.browser_id,
        )


async def click(ctx: ToolContext, args: ChromeSchema) -> object:
    element = _required(args.element, "element", args.action)
    ref = _required(args.ref, "ref", args.action)
    async with chrome_session() as session:
        return await session.browser_click(
            element=element,
            ref=ref,
            video_filename=args.video_filename,
            browser_id=args.browser_id,
        )


async def hover(ctx: ToolContext, args: ChromeSchema) -> object:
    element = _required(args.element, "element", args.action)
    ref = _required(args.ref, "ref", args.action)
    async with chrome_session() as session:
        return await session.browser_hover(
            element=element,
            ref=ref,
            video_filename=args.video_filename,
            browser_id=args.browser_id,
        )


async def drag(ctx: ToolContext, args: ChromeSchema) -> object:
    start_element = _required(args.start_element, "start_element", args.action)
    start_ref = _required(args.start_ref, "start_ref", args.action)
    end_element = _required(args.end_element, "end_element", args.action)
    end_ref = _required(args.end_ref, "end_ref", args.action)
    async with chrome_session() as session:
        return await session.browser_drag(
            start_element=start_element,
            start_ref=start_ref,
            end_element=end_element,
            end_ref=end_ref,
            video_filename=args.video_filename,
            browser_id=args.browser_id,
        )


async def upload_file(ctx: ToolContext, args: ChromeSchema) -> object:
    element = _required(args.element, "element", args.action)
    ref = _required(args.ref, "ref", args.action)
    if not args.paths:
        raise ToolError("upload_file action requires paths")
    if len(args.paths) > 20:
        raise ToolError("upload_file action accepts at most 20 paths")
    async with chrome_session() as session:
        return await session.browser_upload_file(
            element=element,
            ref=ref,
            paths=args.paths,
            video_filename=args.video_filename,
            browser_id=args.browser_id,
        )


async def type_text(ctx: ToolContext, args: ChromeSchema) -> object:
    element = _required(args.element, "element", args.action)
    ref = _required(args.ref, "ref", args.action)
    if args.text is None:
        raise ToolError("type action requires text")
    async with chrome_session() as session:
        return await session.browser_type(
            element=element,
            ref=ref,
            text=args.text,
            submit=args.submit,
            video_filename=args.video_filename,
            browser_id=args.browser_id,
        )


async def select_option(ctx: ToolContext, args: ChromeSchema) -> object:
    element = _required(args.element, "element", args.action)
    ref = _required(args.ref, "ref", args.action)
    if not args.values:
        raise ToolError("select_option action requires values")
    async with chrome_session() as session:
        return await session.browser_select_option(
            element=element,
            ref=ref,
            values=args.values,
            video_filename=args.video_filename,
            browser_id=args.browser_id,
        )


async def press_key(ctx: ToolContext, args: ChromeSchema) -> object:
    key = _required(args.key, "key", args.action)
    async with chrome_session() as session:
        return await session.browser_press_key(
            key=key, video_filename=args.video_filename, browser_id=args.browser_id
        )


async def navigate(ctx: ToolContext, args: ChromeSchema) -> object:
    url = _required(args.url, "url", args.action)
    async with chrome_session() as session:
        return await session.browser_navigate(
            url=url, video_filename=args.video_filename, browser_id=args.browser_id
        )


async def go_back(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_go_back(
            video_filename=args.video_filename, browser_id=args.browser_id
        )


async def go_forward(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_go_forward(
            video_filename=args.video_filename, browser_id=args.browser_id
        )


async def wait(ctx: ToolContext, args: ChromeSchema) -> object:
    time = _required(args.time, "time", args.action)
    time = _in_range(time, "time", args.action, 0, 10)
    async with chrome_session() as session:
        return await session.browser_wait(
            time=time, video_filename=args.video_filename, browser_id=args.browser_id
        )


async def wait_for(ctx: ToolContext, args: ChromeSchema) -> object:
    text = _required(args.text, "text", args.action)
    if not text.strip():
        raise ToolError("wait_for action requires non-whitespace text")
    timeout = _in_range(args.timeout, "timeout", args.action, 0, 10)
    async with chrome_session() as session:
        return await session.browser_wait_for(
            text=text,
            state=args.state,
            timeout=timeout,
            video_filename=args.video_filename,
            browser_id=args.browser_id,
        )


async def download_file(ctx: ToolContext, args: ChromeSchema) -> object:
    element = _required(args.element, "element", args.action)
    ref = _required(args.ref, "ref", args.action)
    timeout = _in_range(args.timeout, "timeout", args.action, 0.1, 60)
    async with chrome_session() as session:
        return await session.browser_download_file(
            element=element, ref=ref, timeout=timeout, browser_id=args.browser_id
        )


async def record_video(ctx: ToolContext, args: ChromeSchema) -> object:
    filename = _required(args.filename, "filename", args.action)
    duration = _required(args.duration, "duration", args.action)
    duration = _in_range(duration, "duration", args.action, 0.5, 10)
    async with chrome_session() as session:
        return await session.browser_record_video(
            filename=filename, duration=duration, browser_id=args.browser_id
        )


async def screenshot(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_screenshot(browser_id=args.browser_id)


async def console_logs(ctx: ToolContext, args: ChromeSchema) -> object:
    async with chrome_session() as session:
        return await session.browser_get_console_logs(browser_id=args.browser_id)
