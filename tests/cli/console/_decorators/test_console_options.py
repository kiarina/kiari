import rich_click as click
from click.testing import CliRunner

from kiari.cli.console._decorators.console_options import console_options


def test_vi() -> None:
    cli_args = {}

    @click.command()
    @console_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--vi"])
    assert cli_args["editing_mode"] == "vi"


def test_emacs() -> None:
    cli_args = {}

    @click.command()
    @console_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--emacs"])
    assert cli_args["editing_mode"] == "emacs"


def test_editing_mode() -> None:
    cli_args = {}

    @click.command()
    @console_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--editing-mode", "emacs"])
    assert cli_args["editing_mode"] == "emacs"
