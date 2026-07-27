import pytest
from kiarina.agi.cost_recorder import cost_recorder_registry
from kiarina.agi.run_context import RunContext

from kiari.cli.console.console_handler import ConsoleSession
from kiari.core.profile import RunOptions
from kiari.core.runtime import create_agi_options, setup_history


@pytest.fixture
def run_options() -> RunOptions:
    return RunOptions()


@pytest.fixture
async def session(run_context: RunContext, run_options: RunOptions) -> ConsoleSession:
    return ConsoleSession(
        history=await setup_history(run_options, run_context),
        **create_agi_options(run_options),
        cost_recorder=cost_recorder_registry.resolve("null"),
        run_context=run_context,
    )
