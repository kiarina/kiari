import json
from dataclasses import asdict, is_dataclass
from typing import Any

from chrome_bridge_sdk import (  # type: ignore[import-untyped]
    BrowserDialogSnapshot,
    ConsoleEntry,
    DownloadFileResult,
    KeyPress,
    RecordedResult,
    Screenshot,
    Snapshot,
    WaitResult,
)
from kiarina.agi.content import Content
from kiarina.agi.file_factory import create_file
from kiarina.agi.tool import ToolContext

from .._types.action import Action


def _json(value: Any) -> str:
    if is_dataclass(value) and not isinstance(value, type):
        value = asdict(value)
    return json.dumps(value, ensure_ascii=False, indent=2)


def _snapshot_metadata(value: Snapshot) -> str:
    browser = f"\nBrowser ID: {value.browser_id}" if value.browser_id else ""
    return f"URL: {value.url}\nTitle: {value.title}\nGeneration: {value.generation}{browser}"


def _snapshot_artifacts(value: Snapshot) -> list[str]:
    artifacts = []
    if value.recording is not None:
        artifacts.append(f"Recording:\n{_json(value.recording)}")
    if value.download is not None:
        artifacts.append(f"Download:\n{_json(value.download)}")
    return artifacts


async def _snapshot_content(
    ctx: ToolContext,
    value: Snapshot,
    *,
    text_suffix: str | None = None,
) -> Content:
    browser_key = value.browser_id or "default"
    result = await create_file(
        ctx.tool_call.name,
        mime_type="text/plain",
        raw_text=value.snapshot,
        file_info_spec_overrides={
            "name": "Chrome accessibility snapshot",
            "unique_key": f"chrome-snapshot:{browser_key}",
            "content_only": True,
        },
        run_context=ctx.run_context,
    )
    text = f"{_snapshot_metadata(value)}\n\nThe accessibility snapshot is attached."
    suffixes = _snapshot_artifacts(value)
    if text_suffix:
        suffixes.append(text_suffix)
    if suffixes:
        text = f"{text}\n\n" + "\n\n".join(suffixes)
    return Content(text=text, files=[result.file_info])


def _dialog_result(value: BrowserDialogSnapshot) -> str:
    browser = f"\nBrowser ID: {value.browser_id}" if value.browser_id else ""
    prompt = (
        f"\nDefault prompt: {value.dialog.default_prompt}" if value.dialog.default_prompt else ""
    )
    return (
        f"URL: {value.url}\nTitle: {value.title}\nGeneration: {value.generation}{browser}\n\n"
        f"Browser dialog: {value.dialog.type}\n"
        f"Message: {value.dialog.message}{prompt}\n"
        f"Dialog ref: {value.dialog.ref}\n"
        f"Actions: {', '.join(value.dialog.actions)}\n\n"
        "Use dialog_respond with this exact dialog_ref. For beforeunload, accept leaves "
        "and dismiss stays."
    )


def _text_result(value: object) -> str:
    if isinstance(value, KeyPress):
        return f"Pressed key {value.key}."
    if isinstance(value, WaitResult):
        return f"Waited for {value.time:g} seconds."
    if isinstance(value, RecordedResult):
        return (
            f"Operation:\n{_text_result(value.operation)}\n\nRecording:\n{_json(value.recording)}"
        )
    return _json(value)


async def format_result(ctx: ToolContext, action: Action, value: object) -> str | Content:
    if isinstance(value, Screenshot):
        result = await create_file(
            ctx.tool_call.name,
            mime_type=value.mime_type,
            raw_data=value.image_bytes,
            file_info_spec_overrides={"name": "Chrome screenshot"},
            run_context=ctx.run_context,
        )
        return Content(
            text=f"Chrome screenshot: {value.width}x{value.height} {value.mime_type}",
            files=[result.file_info],
        )

    if isinstance(value, BrowserDialogSnapshot):
        return _dialog_result(value)

    if isinstance(value, Snapshot):
        return await _snapshot_content(ctx, value)

    if isinstance(value, DownloadFileResult):
        return await _snapshot_content(
            ctx,
            value.snapshot,
            text_suffix=f"Download:\n{_json(value.download)}",
        )

    if isinstance(value, RecordedResult) and isinstance(value.operation, Snapshot):
        return await _snapshot_content(
            ctx,
            value.operation,
            text_suffix=f"Recording:\n{_json(value.recording)}",
        )

    if action == "console_logs":
        entries = value if isinstance(value, list) else []
        if not entries:
            return "No console logs."
        return "\n".join(
            json.dumps(asdict(entry), ensure_ascii=False)
            for entry in entries
            if isinstance(entry, ConsoleEntry)
        )

    if isinstance(value, list):
        return _json(
            [
                asdict(item) if is_dataclass(item) and not isinstance(item, type) else item
                for item in value
            ]
        )

    return _text_result(value)
