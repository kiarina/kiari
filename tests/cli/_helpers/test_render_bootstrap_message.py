from rich.console import Console

from kiari.cli import render_bootstrap_message
from kiari.core.profile import RunOptions


def test_none() -> None:
    renderable = render_bootstrap_message(
        exec_file=None,
        profile_name="default",
        run_spec={},
        run_options=RunOptions(log_level="WARNING"),
    )

    assert renderable is None


def test_render(console: Console) -> None:
    renderable = render_bootstrap_message(
        exec_file="args.json",
        profile_name="default",
        run_spec={"no_load": True},
        run_options=RunOptions(no_load=True),
    )

    assert renderable is not None

    console.print(renderable)


def test_no_run_options(console: Console) -> None:
    renderable = render_bootstrap_message(
        exec_file=None,
        profile_name="default",
        run_spec={},
        run_options=RunOptions(),
    )

    assert renderable is not None

    console.print(renderable)
