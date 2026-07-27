from rich.console import Console
from rich.text import Text

from kiari.core.rich import render_status_block


def test_render_status_block(console: Console) -> None:
    console.print(
        render_status_block(
            title="Test Status",
            lines=["This is a test status block.", "It should render correctly."],
            status="success",
        )
    )

    output = console.export_text()

    assert "Test Status" in output
    assert "This is a test status block." in output


def test_rich_text(console: Console) -> None:
    console.print(
        render_status_block(
            title="Renderable Status",
            lines=[Text("Renderable line", style="bold")],
            status="info",
        )
    )

    output = console.export_text()

    assert "Renderable Status" in output
    assert "Renderable line" in output
