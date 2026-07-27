import logging
import shlex

from kiarina.agi.tool import ToolContext, ToolError
from kiarina.i18n import get_i18n

from kiari.lib.subprocess import get_subprocess_manager

from .._i18n import SubprocessI18n
from .._schemas.subprocess_schema import SubprocessSchema

logger = logging.getLogger(__name__)


async def cancel(ctx: ToolContext, args: SubprocessSchema) -> str:
    t = get_i18n(SubprocessI18n, ctx.run_context.language)

    manager = get_subprocess_manager()
    session = manager.get_session(args.run_id)

    if not session:
        logger.debug("Session not found")
        raise ToolError(t.run_id_not_found_error.format(run_id=args.run_id))

    if session.completed:
        logger.debug("Session already completed")
        raise ToolError(
            t.already_completed_error.format(run_id=args.run_id, status=session.status.value)
        )

    try:
        # If graceful_shutdown_timeout is 0, force immediate termination
        force = args.graceful_shutdown_timeout == 0
        timeout = args.graceful_shutdown_timeout if not force else 0

        await manager.cancel_run(
            args.run_id,
            options={
                "force": force,
                "timeout": timeout,
            },
        )

        shutdown_method = (
            t.immediate_forced_termination
            if force
            else t.graceful_shutdown.format(timeout=args.graceful_shutdown_timeout)
        )

        result_text = t.cancel_result.format(
            run_id=args.run_id,
            argv=shlex.join(session.argv),
            shutdown_method=shutdown_method,
            status=session.status.value,
            returncode=session.returncode,
        )

    except Exception as e:
        logger.error("Error cancelling run", exc_info=e)
        raise ToolError(t.cancel_error.format(error=str(e))) from e

    logger.debug("Run cancelled successfully")

    return result_text
