import pytest

from kiari.cli import run
from kiari.core.profile import ProfileName, RunOptions


async def test_run() -> None:

    async def runner(
        profile_name: ProfileName,
        run_options: RunOptions,
        arg1: str,
    ) -> None:
        assert profile_name == "default"
        assert run_options.log_level == "WARNING"
        assert arg1 == "value1"

        raise ValueError("Test error")

    with pytest.raises(ValueError, match="Test error"):
        await run(runner, "default", RunOptions(log_level="WARNING"), arg1="value1")
