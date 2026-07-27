import pytest

from kiari.cli.console.console_text import parse_console_text


@pytest.mark.parametrize(
    ("text", "command_specifier", "command_args", "content"),
    [
        ("hello", None, [], "hello"),
        ("  hello  ", None, [], "hello"),
        ("/", None, [], "/"),
        ("/help", "help", [], ""),
        ("/help topic", "help", ["topic"], ""),
        ('/run --name "hello world"', "run", ["--name", "hello world"], ""),
        (
            '/run --name foo \\\n--message "hello world"\ncontent line 1\ncontent line 2',
            "run",
            ["--name", "foo", "--message", "hello world"],
            "content line 1\ncontent line 2",
        ),
        (
            "/run\ncontent line 1\ncontent line 2",
            "run",
            [],
            "content line 1\ncontent line 2",
        ),
    ],
)
def test_parse_console_text(
    text: str,
    command_specifier: str | None,
    command_args: list[str],
    content: str,
) -> None:
    console_text = parse_console_text(text)

    assert console_text.command_specifier == command_specifier
    assert console_text.command_args == command_args
    assert console_text.content == content
