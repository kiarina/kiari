import logging
import shlex

from kiarina.agi.content import Content
from kiarina.agi.file_info import FileInfo
from kiarina.agi.tool import ToolContext
from kiarina.i18n import get_i18n

from kiari.lib.subprocess import get_subprocess_manager

from .._i18n import SubprocessI18n
from .._schemas.subprocess_schema import SubprocessSchema
from .._utils.create_output_file import create_output_file

logger = logging.getLogger(__name__)

_OUTPUT_TAIL_LINES = 10
"""Number of trailing output lines to attach per process"""


async def get_list(ctx: ToolContext, args: SubprocessSchema) -> Content:
    t = get_i18n(SubprocessI18n, ctx.run_context.language)

    manager = get_subprocess_manager()

    # List every tracked session (running plus recently completed ones that have
    # not been cleaned up yet), so the agent can notice background jobs that have
    # finished. Show running processes first, then completed ones.
    sessions = sorted(
        manager.sessions.items(),
        key=lambda item: (item[1].completed, item[1].created_at),
    )

    file_infos: list[FileInfo] = []

    for run_id, session in sessions:
        output_lines = session.get_output().splitlines()
        display_output = "\n".join(output_lines[-_OUTPUT_TAIL_LINES:])

        file_infos.append(
            await create_output_file(
                ctx,
                raw_text=display_output,
                display_name=f"Process (run_id:{run_id})",
            )
        )

    if sessions:
        result_text = t.processes_found.format(count=len(sessions))

        for run_id, session in sessions:
            result_text += t.process_info.format(
                run_id=run_id,
                argv=shlex.join(session.argv),
                duration=session.duration,
                status=session.status.value,
                returncode=session.returncode,
            )

        logger.debug(f"Found {len(sessions)} tracked processes.")
    else:
        result_text = t.no_processes
        logger.debug("No tracked processes found.")

    return Content(text=result_text, files=file_infos)
