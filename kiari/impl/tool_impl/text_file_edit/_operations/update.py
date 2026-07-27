import logging
import os

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from .._i18n import TextFileEditI18n
from .._schemas.text_file_edit_schema import TextFileEditSchema
from .._utils.resolve_path import resolve_path
from .._utils.write_file import write_file

logger = logging.getLogger(__name__)


async def update(ctx: ToolContext, args: TextFileEditSchema) -> ToolMessage:
    t = get_i18n(TextFileEditI18n, ctx.run_context.language)

    file_path = resolve_path(args.file_path)

    if not os.path.exists(file_path):
        logger.debug("File does not exist")
        raise ToolError(t.file_not_exists_error.format(file_path=file_path))

    old_content = await kfa.read_text(file_path, default="")

    logger.debug("File updated")

    return await write_file(
        ctx,
        file_path=file_path,
        old_content=old_content,
        content=args.content,
        result_text=t.file_updated.format(file_path=file_path),
    )
