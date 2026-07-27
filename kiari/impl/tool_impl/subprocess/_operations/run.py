import shlex
import sys

from kiarina.agi.content import Content
from kiarina.agi.tool import ToolContext
from kiarina.i18n import get_i18n

from kiari.lib.subprocess import get_subprocess_manager

from .._i18n import SubprocessI18n
from .._schemas.subprocess_schema import SubprocessSchema
from .._utils.create_output_file import create_output_file


async def run(ctx: ToolContext, args: SubprocessSchema) -> Content:
    t = get_i18n(SubprocessI18n, ctx.run_context.language)

    manager = get_subprocess_manager()

    outputs: list[str] = []
    run_id: str | None = None
    completed = False

    async for event in manager.run(
        argv=args.argv,
        cwd=args.cwd,
        env=args.env,
        input_data=args.input_data,
        wait_time=args.wait_time,
    ):
        run_id = event.run_id

        if event.type == "background":
            break
        elif event.type == "finish":
            completed = True
        elif event.type == "stream":
            outputs.append(event.output)
            print(event.output, end="", flush=True, file=sys.stderr)

    if run_id is None:  # pragma: no cover
        raise AssertionError("Unreachable code")

    file_info = await create_output_file(
        ctx,
        raw_text="".join(outputs),
        display_name=f"Run Output (run_id:{run_id})",
    )

    result_text = t.run_result.format(
        run_id=run_id,
        argv=shlex.join(args.argv),
        wait_time=args.wait_time,
    )

    if completed:
        result_text += t.run_execution_completed
    else:
        result_text += t.run_running_background.format(run_id=run_id)

    return Content(text=result_text, files=[file_info])
