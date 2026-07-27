import asyncio
import logging
from typing import Final

from kiarina.agi.content import Content
from kiarina.agi.file_factory import create_file
from kiarina.agi.file_info import FileInfo
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import ToolContext, tool
from kiarina.agi.video_generation_model import (
    create_video,
    delete_video,
    get_video,
    is_video_running,
)
from kiarina.agi.video_generation_provider import (
    VideoGenerationResult,
    VideoGenerationSessionID,
)
from kiarina.i18n import get_i18n

from .._i18n import VideoPredictI18n
from .._schemas.video_predict_schema import VideoPredictSchema

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS: Final[float] = 10.0


@tool(tool_schema=VideoPredictSchema)
async def VideoPredict(
    ctx: ToolContext,
    prompt: str,
    first_image_file_path: str | None = None,
) -> Content:
    t = get_i18n(VideoPredictI18n, ctx.run_context.language)

    session_id = await create_video(
        prompt,
        first_image_file_path=first_image_file_path,
        cost_recorder=ctx.cost_recorder,
        run_context=ctx.run_context,
    )

    try:
        result = await _wait_for_video(
            session_id,
            run_context=ctx.run_context,
        )
        files = await _create_output_files(ctx, result)
        return Content(text=t.result, files=files)
    finally:
        await _delete_video_safely(
            session_id,
            run_context=ctx.run_context,
        )


async def _wait_for_video(
    session_id: VideoGenerationSessionID,
    *,
    run_context: RunContext,
    poll_interval_seconds: float = POLL_INTERVAL_SECONDS,
) -> VideoGenerationResult:
    while await is_video_running(session_id, run_context=run_context):
        await asyncio.sleep(poll_interval_seconds)

    return await get_video(session_id, run_context=run_context)


async def _create_output_files(
    ctx: ToolContext,
    result: VideoGenerationResult,
) -> list[FileInfo]:
    file_infos: list[FileInfo] = []

    outputs = [
        (ctx.tool_call.name, result.video_mime_blob),
        (f"{ctx.tool_call.name}_thumbnail", result.thumbnail_mime_blob),
        (f"{ctx.tool_call.name}_spritesheet", result.spritesheet_mime_blob),
    ]

    for file_name, mime_blob in outputs:
        if mime_blob is None:
            continue

        build_result = await create_file(
            file_name,
            mime_blob,
            run_context=ctx.run_context,
        )
        file_infos.append(build_result.file_info)

    return file_infos


async def _delete_video_safely(
    session_id: VideoGenerationSessionID,
    *,
    run_context: RunContext,
) -> None:
    try:
        await delete_video(session_id, run_context=run_context)
    except Exception:
        logger.exception("Failed to delete video generation session '%s'", session_id)
