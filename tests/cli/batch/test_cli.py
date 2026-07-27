import re
from io import StringIO

import pytest
import rich_click as click
from click.testing import CliRunner

import kiari.cli.batch.cli as batch_cli
from kiari.cli.batch.cli import (
    _apply_stdin_input,
    _build_batch_request,
    batch,
)


def test_batch(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(batch_cli.cli, "run", lambda *args, **kwargs: None)

    CliRunner().invoke(
        batch,
        [
            "--profile",
            "test",
            "--chat-model",
            "mock",
            "--output-text",
            "-a",
            "note.md",
            "hello",
            "world",
        ],
    )


def test_apply_stdin_input(monkeypatch: pytest.MonkeyPatch) -> None:
    _apply_stdin_input({})

    monkeypatch.setattr("sys.stdin", StringIO("stdin text\n"))
    kwargs = {
        "stdin_target": "human",
        "texts": ("arg", "text"),
    }
    _apply_stdin_input(kwargs)
    assert kwargs == {"stdin_text": "stdin text", "texts": ("arg", "text")}

    monkeypatch.setattr("sys.stdin", StringIO("stdin text\n"))
    kwargs = {
        "stdin_target": "system",
        "system_messages": ("system message",),
    }
    _apply_stdin_input(kwargs)
    assert kwargs == {"system_messages": ("stdin text", "system message")}


def test_build_batch_request() -> None:
    with pytest.raises(click.UsageError, match=re.escape("No input text provided.")):
        _build_batch_request({})

    request = _build_batch_request(
        {
            "markdown_text": "markdown text\n",
            "stdin_text": "stdin text\n",
            "texts": ["arg", "text"],
            "attachments": ["note.md"],
        }
    )

    assert request.text == "markdown text\n\nstdin text\n\narg text"
    assert request.attachments == ["note.md"]
