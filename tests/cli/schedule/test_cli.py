import re

import pytest
from click.testing import CliRunner

import kiari.cli.schedule.cli as schedule_cli
from kiari.cli.schedule.cli import schedule


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def test_schedule(monkeypatch: pytest.MonkeyPatch) -> None:
    async def noop(*args, **kwargs):
        pass

    monkeypatch.setattr(schedule_cli, "setup_runtime", noop)
    monkeypatch.setattr(schedule_cli.cli, "run", noop)

    result = CliRunner().invoke(
        schedule,
        [
            "--profile",
            "test",
            "--chat-model",
            "mock",
            "--interval",
            "5m",
            "--schedule-handler",
            "vanilla",
            "file?paths=src",
        ],
    )

    assert result.exit_code == 0


def test_schedule_requires_trigger() -> None:
    result = CliRunner().invoke(schedule, [])

    assert result.exit_code != 0
    assert "Schedule mode requires --interval or --cron." in _strip_ansi(result.output)


def test_schedule_rejects_multiple_triggers() -> None:
    result = CliRunner().invoke(
        schedule,
        [
            "--interval",
            "5m",
            "--cron",
            "0 * * * *",
        ],
    )

    assert result.exit_code != 0
    assert "either --interval or --cron" in _strip_ansi(result.output)
