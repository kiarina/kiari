import re

import pytest
from click.testing import CliRunner


def _strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


@pytest.fixture(autouse=True)
def avoid_configure_app():
    import kiarina.utils.app as app_module

    patch = pytest.MonkeyPatch()
    patch.setattr(
        app_module,
        "configure",
        lambda *, app_author, app_name: None,
    )

    yield

    patch.undo()


def _resolve(args: list[str]) -> tuple[str | None, list[str]]:
    import click

    from kiari.cli.cli import kiari

    ctx = click.Context(kiari)
    command_name, _, command_args = kiari.resolve_command(ctx, list(args))
    return command_name, command_args


def test_resolve_command_subcommand() -> None:
    assert _resolve(["batch", "hello"]) == ("batch", ["hello"])


def test_resolve_command_profile_shortcuts() -> None:
    assert _resolve(["-l"]) == ("profile", ["list"])
    assert _resolve(["--list", "--query", "dev"]) == (
        "profile",
        ["list", "--query", "dev"],
    )
    assert _resolve(["-n", "dev"]) == ("profile", ["new", "dev"])
    assert _resolve(["--new", "dev", "--description", "Dev"]) == (
        "profile",
        ["new", "dev", "--description", "Dev"],
    )
    assert _resolve(["-u", "dev"]) == ("profile", ["use", "dev"])


def test_resolve_command_admin_shortcuts() -> None:
    assert _resolve(["-w"]) == ("admin", ["wipe-data"])
    assert _resolve(["--wipe-data"]) == ("admin", ["wipe-data"])
    assert _resolve(["-c"]) == ("admin", ["clear-cache"])
    assert _resolve(["--clear-cache"]) == ("admin", ["clear-cache"])


def test_resolve_command_batch_when_batch_texts_are_present() -> None:
    assert _resolve(["hello"]) == ("batch", ["hello"])
    assert _resolve(["--chat-model", "gpt-5.4", "hello"]) == (
        "batch",
        ["--chat-model", "gpt-5.4", "hello"],
    )


def test_resolve_command_console_when_batch_texts_are_missing() -> None:
    assert _resolve(["--chat-model", "gpt-5.4"]) == (
        "console",
        ["--chat-model", "gpt-5.4"],
    )


def test_kiari_help() -> None:
    from kiari.cli.cli import kiari

    result = CliRunner().invoke(kiari, ["-h"])

    assert result.exit_code == 0
    assert "Usage: kiari" in _strip_ansi(result.output)
