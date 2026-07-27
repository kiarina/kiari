import logging
import os

from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from .._i18n import TextFileEditI18n
from .._schemas.text_file_edit_schema import TextFileEditSchema
from .._utils.resolve_path import resolve_path
from .._utils.write_file import write_file

logger = logging.getLogger(__name__)


async def create(ctx: ToolContext, args: TextFileEditSchema) -> ToolMessage:
    t = get_i18n(TextFileEditI18n, ctx.run_context.language)

    file_path = resolve_path(args.file_path)

    if os.path.exists(file_path):
        logger.debug("File already exists")
        raise ToolError(t.file_already_exists_error.format(file_path=file_path))

    logger.debug("File created")

    return await write_file(
        ctx,
        file_path=file_path,
        old_content="",
        content=args.content,
        result_text=t.file_created.format(file_path=file_path),
    )
