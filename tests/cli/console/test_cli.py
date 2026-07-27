from pathlib import Path

import pytest
from click.testing import CliRunner

import kiari.cli.console.cli
from kiari.cli.console.cli import (
    console,
)


@pytest.fixture(autouse=True)
def setup(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_run(*args, **kwargs) -> None:
        pass

    monkeypatch.setattr(kiari.cli.console.cli.cli, "run", fake_run)


def test_console() -> None:
    result = CliRunner().invoke(console)
    assert result.exit_code == 0


def test_stdin_target_human() -> None:
    result = CliRunner().invoke(
        console,
        [
            "--stdin",
            "human",
        ],
        "hello",
    )

    assert result.exit_code == 0


def test_stdin_target_system() -> None:
    result = CliRunner().invoke(
        console,
        [
            "--stdin",
            "system",
        ],
        "hello",
    )

    assert result.exit_code == 0


def test_console_request(tmp_path: Path) -> None:
    exec_file = tmp_path / "input.md"

    exec_file.write_text("---\nchat_model: mock\n---\nfirst")

    result = CliRunner().invoke(
        console,
        [
            "--stdin",
            "human",
            "--exec",
            str(exec_file),
            "third",
        ],
        "second",
    )

    assert result.exit_code == 0
