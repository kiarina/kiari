from kiari.impl.watch_handler_impl.slack._utils.convert_markdown_to_mrkdwn import (
    convert_markdown_to_mrkdwn,
)


def test_convert_markdown_to_mrkdwn() -> None:
    text = convert_markdown_to_mrkdwn(
        "**bold**\n- item\n[OpenAI](https://openai.com)\n```python\nprint('hi')\n```"
    )

    assert "*bold*" in text
    assert "• item" in text
    assert "<https://openai.com|OpenAI>" in text
    assert "```print('hi')```" in text
