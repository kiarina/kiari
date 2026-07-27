import logging

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from .._i18n import TextFileEditI18n
from .._schemas.text_file_edit_schema import TextFileEditSchema
from .._utils.build_result import build_result
from .._utils.replace_str import ReplaceError, ReplaceResult, replace_str
from .._utils.resolve_path import resolve_path

logger = logging.getLogger(__name__)


async def str_replace(ctx: ToolContext, args: TextFileEditSchema) -> ToolMessage:
    t = get_i18n(TextFileEditI18n, ctx.run_context.language)

    file_path = resolve_path(args.file_path)

    content = await kfa.read_text(file_path)

    if content is None:
        logger.debug("File not readable")
        raise ToolError(t.file_not_readable_error.format(file_path=file_path))

    if not args.search:
        logger.debug("Empty search pattern")
        raise ToolError(t.empty_search_pattern_error)

    result = replace_str(content, args.search, args.replace, args.replace_all)

    if isinstance(result, ReplaceError):
        if result.occurrences > 1:
            logger.debug("Multiple matches found")
            raise ToolError(t.multiple_matches_error.format(count=result.occurrences))
        else:
            logger.debug("Search pattern not found")
            raise ToolError(t.pattern_not_found_error)

    assert isinstance(result, ReplaceResult)  # pragma: no cover

    logger.debug("Replacement successful")

    new_content = result.new_content

    await kfa.write_text(file_path, new_content)

    total_lines = len(new_content.splitlines())
    context_start = max(1, result.start_line - 3)
    context_end = min(total_lines, result.end_line + 3)

    file_info = await load_file_info(
        {
            "uri_or_file_path": file_path,
            "start_line": context_start,
            "end_line": context_end,
        },
        run_context=ctx.run_context,
    )
    assert file_info is not None  # pragma: no cover

    return build_result(
        ctx,
        file_path=file_path,
        old_content=content,
        new_content=new_content,
        file_info=file_info,
        result_text=t.str_replaced.format(file_path=file_path),
    )
