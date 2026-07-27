import logging

import kiarina.utils.file.asyncio as kfa
from kiarina.agi.file_info_loader import load_file_info
from kiarina.agi.message import ToolMessage
from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from .._i18n import TextFileEditI18n
from .._schemas.text_file_edit_schema import TextFileEditSchema
from .._utils.build_result import build_result
from .._utils.resolve_path import resolve_path

logger = logging.getLogger(__name__)


async def line_replace(ctx: ToolContext, args: TextFileEditSchema) -> ToolMessage:
    t = get_i18n(TextFileEditI18n, ctx.run_context.language)

    file_path = resolve_path(args.file_path)

    content = await kfa.read_text(file_path)

    if content is None:
        logger.debug("File not readable")
        raise ToolError(t.file_not_readable_error.format(file_path=file_path))

    file_lines = content.split("\n")

    if args.start_line == 0 and args.end_line == 0:
        # Insert at the beginning
        new_content = args.replace + "\n" + content
        action_type = "insert_head"

    elif args.start_line == -1 and args.end_line == -1:
        # Append at the end
        new_content = content + "\n" + args.replace
        action_type = "insert_tail"

    else:
        # Normal line replacement
        max_line = len(file_lines)

        # Check start line
        if args.start_line <= 0 and args.start_line != -1:
            logger.debug("Invalid start line")
            raise ToolError(t.invalid_start_line_error.format(start_line=args.start_line))

        if args.start_line > max_line:
            raise ToolError(
                t.start_line_exceeds_max_error.format(start_line=args.start_line, max_line=max_line)
            )

        # Check end line
        if args.end_line <= 0 and args.end_line != -1:
            raise ToolError(t.invalid_end_line_error.format(end_line=args.end_line))

        if args.end_line > max_line:
            raise ToolError(
                t.end_line_exceeds_max_error.format(end_line=args.end_line, max_line=max_line)
            )

        # Check if start line is greater than end line
        if args.start_line > args.end_line:
            raise ToolError(
                t.start_line_greater_than_end_line_error.format(
                    start_line=args.start_line, end_line=args.end_line
                )
            )

        # Replace lines (treat multiple lines as a single block)
        start_idx = args.start_line - 1
        end_idx = args.end_line
        file_lines[start_idx:end_idx] = args.replace.split("\n")

        new_content = "\n".join(file_lines)
        action_type = "replace"

    await kfa.write_text(file_path, new_content)

    # Calculate the line range to show
    total_lines = len(new_content.splitlines())
    replace_lines_count = len(args.replace.splitlines())

    if action_type == "insert_head":
        logger.debug("Insert head")
        context_start = 1
        context_end = min(total_lines, replace_lines_count + 3)

    elif action_type == "insert_tail":
        logger.debug("Insert tail")
        context_start = max(1, total_lines - replace_lines_count + 1 - 3)
        context_end = total_lines

    else:  # replace
        logger.debug("Line replace")
        context_start = max(1, args.start_line - 3)
        replaced_end_line = args.start_line + replace_lines_count - 1
        context_end = min(total_lines, replaced_end_line + 3)

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
        result_text=t.line_replaced.format(file_path=file_path),
    )
