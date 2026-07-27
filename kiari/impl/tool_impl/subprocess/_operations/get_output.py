import logging
import shlex

from kiarina.agi.content import Content
from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from kiari.lib.subprocess import SubprocessStatus, get_subprocess_manager

from .._i18n import SubprocessI18n
from .._schemas.subprocess_schema import SubprocessSchema
from .._utils.create_output_file import create_output_file

logger = logging.getLogger(__name__)


async def get_output(ctx: ToolContext, args: SubprocessSchema) -> Content:
    t = get_i18n(SubprocessI18n, ctx.run_context.language)

    manager = get_subprocess_manager()

    session = manager.get_session(args.run_id)

    if not session:
        raise ToolError(t.run_id_not_found_error.format(run_id=args.run_id))

    file_info = await create_output_file(
        ctx,
        raw_text=session.get_output(),
        display_name=f"Process Output (run_id:{args.run_id})",
        start_line=args.start_line,
        end_line=args.end_line,
    )

    result_text = t.get_output_result.format(
        run_id=args.run_id,
        argv=shlex.join(session.argv),
        status=session.status.value,
        duration=session.duration,
        returncode=session.returncode,
        completed=t.yes if session.completed else t.no,
    )

    if session.completed:
        if session.status == SubprocessStatus.SUCCESS:
            result_text += t.process_completed_successfully
            logger.debug("Process completed successfully")
        elif session.status == SubprocessStatus.CANCELLED:
            result_text += t.process_cancelled
            logger.debug("Process was cancelled")
        elif session.status == SubprocessStatus.FAILURE:
            result_text += t.process_failed.format(returncode=session.returncode)
            logger.debug("Process failed")
    else:
        result_text += t.process_running
        logger.debug("Process is still running")

    return Content(text=result_text, files=[file_info])
