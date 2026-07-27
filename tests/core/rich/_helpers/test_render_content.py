from kiarina.agi.content import Content
from rich.console import Console

from kiari.core.rich._helpers.render_content import render_content


def test_render_content(console: Console, text_file_info, image_file_info) -> None:
    console.print(
        render_content(
            Content(
                text="hello",
                files=[text_file_info, image_file_info],
                cache_control={"type": "ephemeral"},
                tag="test_tag",
                description="test description",
                template="<{tag}{attributes} test>\n{inner_xml}\n</{tag}>",
                file_tags={"text": "text_file", "image": "image_file"},
            )
        )
    )

    output = console.export_text()

    assert "hello" in output
