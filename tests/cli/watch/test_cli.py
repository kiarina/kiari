import pytest
from click.testing import CliRunner

import kiari.cli.watch.cli as watch_cli
from kiari.cli.watch.cli import watch


def test_watch(monkeypatch: pytest.MonkeyPatch) -> None:
    async def noop(*args, **kwargs):
        pass

    monkeypatch.setattr(watch_cli, "setup_runtime", noop)
    monkeypatch.setattr(watch_cli.cli, "run", noop)

    result = CliRunner().invoke(
        watch,
        [
            "--profile",
            "test",
            "--chat-model",
            "mock",
            "--watch-handler",
            "vanilla",
            "--watch-max-concurrent",
            "2",
            "file?paths=src",
        ],
    )

    assert result.exit_code == 0
