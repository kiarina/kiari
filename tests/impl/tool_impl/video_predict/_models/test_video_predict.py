from collections.abc import AsyncIterator, Awaitable, Callable
from pathlib import Path
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, ToolContext, run_tool
from kiarina.agi.video_generation_model import (
    create_video,
    delete_video,
    settings_manager as video_model_settings,
)
from kiarina.agi.video_generation_provider import VideoGenerationResult
from kiarina.agi.video_generation_provider_impl.mock import (
    SessionStore,
    settings_manager as mock_provider_settings,
)
from kiarina.utils.mime import MIMEBlob

from kiari.impl.tool_impl.video_predict import VideoPredict
from kiari.impl.tool_impl.video_predict._models.video_predict import (
    _create_output_files,
    _wait_for_video,
)


@pytest.fixture(autouse=True)
async def use_mock_video_generation_model(
    video_file_path: str,
) -> AsyncIterator[None]:
    original_video_model_cli_args = video_model_settings.cli_args.copy()
    original_mock_provider_cli_args = mock_provider_settings.cli_args.copy()
    session_store = SessionStore.get_instance()

    await session_store.clear()
    video_model_settings.set_cli_args("default", "mock")
    mock_provider_settings.set_cli_args(
        "result_video_file_path",
        video_file_path,
    )
    mock_provider_settings.set_cli_args("delay_seconds", 0.0)

    yield

    await session_store.clear()
    video_model_settings.cli_args = original_video_model_cli_args
    mock_provider_settings.cli_args = original_mock_provider_cli_args


@pytest.fixture
def tool() -> BaseTool:
    tool = VideoPredict()
    tool.name = "video_predict"
    return tool


@pytest.fixture
def run_video_predict(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any]], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any]) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="video_predict", args=args),
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]

        assert len(messages) == 1
        return messages[0]

    return _run


async def test_predict_video_with_mock_model(
    run_video_predict: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_video_predict({"prompt": "A cat playing with a ball"})

    assert not message.failed
    assert message.tool_name == "video_predict"

    content = message.contents[0]
    assert content.text == "Generated the video successfully."
    assert len(content.files) == 1
    assert content.files[0].type == "video"
    assert not SessionStore.get_instance()._sessions


async def test_predict_video_with_first_image(
    run_video_predict: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
    image_file_path: str,
) -> None:
    message = await run_video_predict(
        {
            "prompt": "Animate this illustration",
            "first_image_file_path": image_file_path,
        }
    )

    assert not message.failed
    assert message.contents[0].files[0].type == "video"
    assert not SessionStore.get_instance()._sessions


async def test_wait_for_video_with_mock_model(
    run_context: RunContext,
) -> None:
    mock_provider_settings.set_cli_args("delay_seconds", 0.02)
    session_id = await create_video(
        "A cat playing with a ball",
        run_context=run_context,
    )

    try:
        result = await _wait_for_video(
            session_id,
            run_context=run_context,
            poll_interval_seconds=0.01,
        )

        assert result.video_mime_blob.mime_type == "video/mp4"
        assert result.video_mime_blob.raw_data
    finally:
        await delete_video(session_id, run_context=run_context)


async def test_create_output_files_with_optional_files(
    run_context: RunContext,
    video_file_path: str,
    image_file_path: str,
) -> None:
    video_data = Path(video_file_path).read_bytes()
    image_data = Path(image_file_path).read_bytes()
    result = VideoGenerationResult(
        video_mime_blob=MIMEBlob(mime_type="video/mp4", raw_data=video_data),
        thumbnail_mime_blob=MIMEBlob(mime_type="image/png", raw_data=image_data),
        spritesheet_mime_blob=MIMEBlob(mime_type="image/jpeg", raw_data=image_data),
    )
    ctx = ToolContext.create(
        tool_call=ToolCall(name="video_predict", args={}),
        run_context=run_context,
    )

    files = await _create_output_files(ctx, result)

    assert [file.type for file in files] == ["video", "image", "image"]


async def test_generation_failure_deletes_video(
    run_video_predict: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    mock_provider_settings.set_cli_args("result_video_file_path", None)

    message = await run_video_predict({"prompt": "A failing video"})

    assert message.failed
    assert "No result video file path configured" in message.contents[0].text
    assert not SessionStore.get_instance()._sessions
