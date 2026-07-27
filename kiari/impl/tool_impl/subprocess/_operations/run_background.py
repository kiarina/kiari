import shlex

from kiarina.agi.tool import ToolContext
from kiarina.i18n import get_i18n

from kiari.lib.subprocess import get_subprocess_manager

from .._i18n import SubprocessI18n
from .._schemas.subprocess_schema import SubprocessSchema


async def run_background(ctx: ToolContext, args: SubprocessSchema) -> str:
    t = get_i18n(SubprocessI18n, ctx.run_context.language)

    manager = get_subprocess_manager()

    run_id: str | None = None

    async for event in manager.run(
        argv=args.argv,
        cwd=args.cwd,
        env=args.env,
        input_data=args.input_data,
        wait_time=0.0,
    ):
        run_id = event.run_id

        if event.type == "background":
            break

    if run_id is None:  # pragma: no cover
        raise AssertionError("Unreachable code")

    return t.run_background_result.format(
        run_id=run_id,
        argv=shlex.join(args.argv),
    )
