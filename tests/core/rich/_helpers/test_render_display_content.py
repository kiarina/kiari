import pytest
from kiarina.agi.display_content import FileDisplayContent, TextDisplayContent
from rich.console import Console

from kiari.core.rich._helpers.render_display_content import render_display_content


def test_text_markdown(console: Console) -> None:
    console.print(
        render_display_content(
            TextDisplayContent(
                mime_type="text/markdown",
                text="## title\n\nhello\nworld",
                start_line=2,
            )
        )
    )

    output = console.export_text()

    assert "title" in output


@pytest.mark.parametrize(
    "mime_type, text",
    [
        pytest.param(
            "application/json",
            '{"key": "value"}',
            id="1. json",
        ),
        pytest.param(
            "text/css",
            "body { color: red; }",
            id="2. css",
        ),
        pytest.param(
            "text/html",
            "<html><body>hello</body></html>",
            id="3. html",
        ),
        pytest.param(
            "text/javascript",
            "console.log('hello');",
            id="4. javascript",
        ),
        pytest.param(
            "text/x-python",
            "print('hello')",
            id="5. python",
        ),
        pytest.param(
            "text/plain",
            "just plain text",
            id="6. plain text",
        ),
    ],
)
def test_text_other(console: Console, mime_type, text) -> None:
    console.print(
        render_display_content(
            TextDisplayContent(
                mime_type=mime_type,
                text=text,
            )
        )
    )

    output = console.export_text()

    assert text in output


def test_file(console: Console) -> None:
    console.print(
        render_display_content(
            FileDisplayContent(
                uri_or_file_path="/path/to/file.txt",
                mime_type="text/plain",
                display_name="file.txt",
            )
        )
    )

    output = console.export_text()

    assert "file.txt" in output
