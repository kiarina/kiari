from rich.console import Console, Group
from rich.text import Text

from kiari.core.rich import join_renderables


def test_none() -> None:
    assert join_renderables([]) is None
    assert join_renderables([None]) is None


def test_group(console: Console) -> None:
    renderable = join_renderables(
        [
            Text("hello"),
            None,
            Text("world"),
        ]
    )

    assert isinstance(renderable, Group)

    console.print(renderable)
    output = console.export_text()

    assert output == "hello\nworld\n"


def test_separator(console: Console) -> None:
    renderable = join_renderables(
        [
            Text("hello"),
            None,
            Text("world"),
        ],
        separator=Text(),
    )

    assert isinstance(renderable, Group)

    console.print(renderable)
    output = console.export_text()

    assert output == "hello\n\nworld\n"


def test_markup() -> None:
    renderable = join_renderables(["[bold]hello[/bold]"], markup=True)

    assert isinstance(renderable, Group)
    assert isinstance(renderable.renderables[0], Text)
