import asyncio
import sys
from typing import Any

import rich_click as click
from kiarina.i18n import get_i18n, get_system_language

from kiari import cli
from kiari.core.rich import console_registry
from kiari.core.runtime import setup_runtime

from ._constants.batch_option_group import BATCH_OPTION_GROUP
from ._decorators.batch_options import batch_options
from ._i18n import BatchI18n
from ._operations.run_batch import run_batch
from .batch_handler import BatchRequest

t = get_i18n(BatchI18n, get_system_language())

click.rich_click.OPTION_GROUPS["kiari batch"] = [
    BATCH_OPTION_GROUP,
    *cli.COMMON_OPTION_GROUPS,
]


# fmt: off
@click.command(panel="Run Commands", help=t.command_help, epilog=t.texts_help)
# Per-invocation input. These values are extracted into extra_args and are not saved to RunSpec/Profile.
@click.argument("texts", nargs=-1, type=str, metavar="[TEXT]...")
@click.option("-a", "--attachment", "attachments", multiple=True, type=str, help=t.attachments_help)
@click.option("--stdin", "stdin_target", type=click.Choice(["human", "system"]), help=t.stdin_help)
@batch_options
@cli.common_options
def batch(**kwargs: Any) -> None:
    # fmt: on
    asyncio.run(_batch(**kwargs))


async def _batch(**kwargs: Any) -> None:
    _apply_stdin_input(kwargs)

    cli_args = cli.build_cli_args(
        extra_args_keys=["texts", "attachments", "stdin_text"],
        markdown_content_key="markdown_text",
        **kwargs,
    )

    profile_name, run_spec, run_options = cli.setup_profile(
        cli_args.profile_name,
        cli_args.save_mode,
        cli_args.run_spec,
    )

    if renderable := cli.render_bootstrap_message(
        cli_args.exec_file, profile_name, run_spec, run_options
    ):
        console_registry.get().print(renderable)

    await setup_runtime(profile_name, run_options)
    request = _build_batch_request(cli_args.extra_args)
    await cli.run(run_batch, profile_name, run_options, request)


def _apply_stdin_input(kwargs: dict[str, Any]) -> None:
    stdin_target = kwargs.pop("stdin_target", None)

    if stdin_target is None:
        return

    stdin_text = sys.stdin.read().strip()

    if stdin_target == "human":
        kwargs["stdin_text"] = stdin_text

    elif stdin_target == "system":
        system_messages = tuple(kwargs.get("system_messages", ()))
        kwargs["system_messages"] = (stdin_text, *system_messages)

    else:  # pragma: no cover
        raise click.UsageError(f"Unsupported stdin target: {stdin_target}")


def _build_batch_request(extra_args: cli.ExtraArgs) -> BatchRequest:
    text = ""

    if markdown_content := extra_args.get("markdown_text"):
        text = str(markdown_content).strip()

    if stdin_text := extra_args.get("stdin_text"):
        text = (text + "\n\n" + str(stdin_text).strip()).strip()

    if texts := extra_args.get("texts", []):
        text = (text + "\n\n" + " ".join(texts)).strip()

    if not text:
        raise click.UsageError("No input text provided.")

    attachments = extra_args.get("attachments", [])

    return BatchRequest(
        text=text,
        attachments=attachments,
    )
