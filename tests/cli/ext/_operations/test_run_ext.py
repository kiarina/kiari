from collections.abc import Sequence

import pytest

from kiari.cli.ext._operations.run_ext import run_ext
from kiari.cli.ext.extension_command import (
    BaseExtensionCommand,
    ExtensionCommandContext,
    extension_command_registry,
)
from kiari.core.profile import RunOptions


@pytest.fixture(autouse=True)
def cleanup():
    yield
    extension_command_registry.clear()


async def test_run_ext() -> None:
    calls = []

    class ExampleExtensionCommand(BaseExtensionCommand):
        async def run(
            self,
            context: ExtensionCommandContext,
            args: Sequence[str],
        ) -> None:
            calls.append((context, list(args)))

    extension_command_registry.register("example", ExampleExtensionCommand)

    run_options = RunOptions(chat_model="mock")

    await run_ext(
        profile_name="test",
        run_options=run_options,
        command_name="example",
        args=["--flag", "hello"],
    )

    assert len(calls) == 1
    context, args = calls[0]
    assert context.profile_name == "test"
    assert context.run_options == run_options
    assert args == ["--flag", "hello"]
