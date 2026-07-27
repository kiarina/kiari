from collections.abc import Awaitable, Callable, Iterator
from typing import Any

import pytest
from kiarina.agi.event import ToolMessageEvent
from kiarina.agi.image_generation_model import settings_manager
from kiarina.agi.message import ToolCall, ToolMessage
from kiarina.agi.run_context import RunContext
from kiarina.agi.tool import BaseTool, run_tool

from kiari.impl.tool_impl.image_generate import ImageGenerate


@pytest.fixture
def tool() -> BaseTool:
    tool = ImageGenerate()
    tool.name = "image_generate"
    return tool


@pytest.fixture(autouse=True)
def use_mock_image_generation_model() -> Iterator[None]:
    cli_args = settings_manager.cli_args.copy()
    settings_manager.set_cli_args("default", "mock")
    yield
    settings_manager.cli_args = cli_args


@pytest.fixture
def run_image_generate(
    tool: BaseTool,
    run_context: RunContext,
) -> Callable[[dict[str, Any]], Awaitable[ToolMessage]]:
    async def _run(args: dict[str, Any]) -> ToolMessage:
        events = [
            event
            async for event in run_tool(
                ToolCall(name="image_generate", args=args),
                tool_options={"tools": [tool]},
                run_context=run_context,
            )
        ]

        messages = [event.message for event in events if isinstance(event, ToolMessageEvent)]

        assert len(messages) == 1
        return messages[0]

    return _run


async def test_generate_image(
    run_image_generate: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_image_generate({"prompt": "An illustration of a cat reading a book"})

    assert not message.failed
    assert message.tool_name == "image_generate"

    content = message.contents[0]
    assert content.text == "Generated the image successfully."
    assert len(content.files) == 1
    assert content.files[0].type == "image"


async def test_generation_failure(
    monkeypatch: pytest.MonkeyPatch,
    run_image_generate: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    async def fail_generate_image(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("image generation failed")

    monkeypatch.setattr(
        "kiari.impl.tool_impl.image_generate._models.image_generate.generate_image",
        fail_generate_image,
    )

    message = await run_image_generate({"prompt": "A failing image"})

    assert message.failed
    assert "image generation failed" in message.contents[0].text
