import rich_click as click
from click.testing import CliRunner

from kiari.cli import common_options


def test_set_profile() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--set"])
    assert cli_args["save_mode"] == "set"


def test_reset_profile() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--reset"])
    assert cli_args["save_mode"] == "reset"


def test_stateless() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--stateless"])
    assert cli_args["no_load"] is True
    assert cli_args["no_save"] is True


def test_openai() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--openai"])
    assert cli_args["chat_model"] == "openai"


def test_anthropic() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--anthropic"])
    assert cli_args["chat_model"] == "anthropic"


def test_google() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--google"])
    assert cli_args["chat_model"] == "google"


def test_verbose() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--verbose"])
    assert cli_args["log_level"] == "DEBUG"


def test_quiet() -> None:
    cli_args = {}

    @click.command()
    @common_options
    def command(**kwargs) -> None:
        cli_args.update(kwargs)

    runner = CliRunner()
    runner.invoke(command, ["--quiet"])
    assert cli_args["log_level"] == "WARNING"
