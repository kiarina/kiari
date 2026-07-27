from chrome_bridge_sdk import (
    BrowserDialog,
    BrowserDialogSnapshot,
    Download,
    DownloadFileResult,
    RecordedResult,
    Recording,
    Snapshot,
)
from kiarina.agi.content import Content
from kiarina.agi.history import History
from kiarina.agi.message import ToolCall
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolContext

from kiari.impl.tool_impl.chrome._helpers.format_result import format_result


def _context(run_context: RunContext) -> ToolContext:
    return ToolContext(
        tool_call=ToolCall(name="chrome", args={"action": "snapshot"}),
        history=History(),
        cost_recorder=None,
        run_context=run_context,
    )


def _snapshot() -> Snapshot:
    return Snapshot(
        generation=3,
        url="https://example.com/",
        title="Example",
        snapshot='- button "Continue" [ref=s3e1]',
        browser_id="browser-1",
    )


async def test_browser_dialog_is_returned_with_exact_response_arguments(
    run_context: RunContext,
) -> None:
    value = BrowserDialogSnapshot(
        generation=4,
        url="https://example.com/form",
        title="Example form",
        dialog=BrowserDialog(
            type="prompt",
            message="Enter a label",
            default_prompt="Draft",
            ref="s4d1",
            actions=("accept", "dismiss"),
        ),
        browser_id="browser-1",
    )

    result = await format_result(_context(run_context), "snapshot", value)

    assert isinstance(result, str)
    assert "Browser dialog: prompt" in result
    assert "Message: Enter a label" in result
    assert "Default prompt: Draft" in result
    assert "Dialog ref: s4d1" in result
    assert "Actions: accept, dismiss" in result
    assert "dialog_respond" in result


def _assert_snapshot_content(result: str | Content) -> None:
    assert isinstance(result, Content)
    assert result.text is not None
    assert "URL: https://example.com/" in result.text
    assert "Generation: 3" in result.text
    assert "ref=s3e1" not in result.text
    assert len(result.files) == 1

    file_info = result.files[0]
    assert file_info.type == "text"
    assert file_info.name == "Chrome accessibility snapshot"
    assert file_info.unique_key == "chrome-snapshot:browser-1"
    assert file_info.content_only
    assert file_info.raw_text == '- button "Continue" [ref=s3e1]'


async def test_snapshot_is_returned_as_deduplicated_file_info(
    run_context: RunContext,
) -> None:
    result = await format_result(_context(run_context), "snapshot", _snapshot())

    _assert_snapshot_content(result)


async def test_recorded_snapshot_is_returned_as_deduplicated_file_info(
    run_context: RunContext,
) -> None:
    value = RecordedResult(
        operation=_snapshot(),
        recording=Recording(
            requested_filename="action.webm",
            filename="action.webm",
            mime_type="video/webm",
            duration_ms=100,
            width=800,
            height=600,
            frame_count=3,
            dropped_frame_count=0,
            size_bytes=1000,
            browser_id="browser-1",
        ),
    )

    result = await format_result(_context(run_context), "click", value)

    _assert_snapshot_content(result)
    assert isinstance(result, Content)
    assert "Recording:" in (result.text or "")


async def test_download_snapshot_is_returned_as_deduplicated_file_info(
    run_context: RunContext,
) -> None:
    value = DownloadFileResult(
        download=Download(
            suggested_filename="report.pdf",
            state="completed",
            received_bytes=100,
            total_bytes=100,
            browser_id="browser-1",
        ),
        snapshot=_snapshot(),
    )

    result = await format_result(_context(run_context), "download_file", value)

    _assert_snapshot_content(result)
    assert isinstance(result, Content)
    assert "Download:" in (result.text or "")


async def test_dialog_continuation_artifacts_are_included_with_snapshot(
    run_context: RunContext,
) -> None:
    value = Snapshot(
        generation=3,
        url="https://example.com/",
        title="Example",
        snapshot='- button "Continue" [ref=s3e1]',
        browser_id="browser-1",
        recording=Recording(
            requested_filename="action.webm",
            filename="action.webm",
            mime_type="video/webm",
            duration_ms=100,
            width=800,
            height=600,
            frame_count=3,
            dropped_frame_count=0,
            size_bytes=1000,
            browser_id="browser-1",
        ),
        download=Download(
            suggested_filename="report.pdf",
            state="completed",
            received_bytes=100,
            total_bytes=100,
            browser_id="browser-1",
        ),
    )

    result = await format_result(_context(run_context), "dialog_respond", value)

    _assert_snapshot_content(result)
    assert isinstance(result, Content)
    assert "Recording:" in (result.text or "")
    assert "Download:" in (result.text or "")
