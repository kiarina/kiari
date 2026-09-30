from kiarina.agi.run_context import RunContext

from kiari.core.profile import RunOptions


def create_run_context(run_options: RunOptions) -> RunContext:
    if run_options.runner_id is None:
        return RunContext()

    return RunContext(runner_id=run_options.runner_id)
