from kiari.core.profile import RunOptions
from kiari.core.runtime import create_run_context


def test_create_run_context_uses_runner_id() -> None:
    run_context = create_run_context(RunOptions(runner_id="runner-1"))

    assert run_context.runner_id == "runner-1"


def test_create_run_context_generates_runner_id() -> None:
    run_options = RunOptions()

    assert create_run_context(run_options).runner_id != create_run_context(run_options).runner_id
