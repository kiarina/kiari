import json
from collections.abc import Awaitable, Callable
from typing import Any

from kiarina.agi.message import ToolMessage

from kiari.impl.web_impl.mock import MockWeb, settings_manager as mock_web_settings_manager
from kiari.lib.web import web_registry


async def test_search(
    run_web: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    web = web_registry.resolve()
    assert isinstance(web, MockWeb)

    message = await run_web({"action": "search", "query": "example query"})

    assert not message.failed
    assert message.tool_name == "web"
    assert json.loads(message.contents[0].text) == [
        {
            "title": "Example",
            "url": "https://example.com",
            "content": "Example content",
        },
        {
            "title": "日本語",
            "url": "https://example.com/ja",
            "content": "日本語の検索結果",
        },
    ]
    assert "日本語" in message.contents[0].text
    assert "\\u65e5" not in message.contents[0].text


async def test_search_empty_results(
    run_web: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    mock_web_settings_manager.set_cli_args("search_results", [])

    message = await run_web({"action": "search", "query": "no results"})

    assert not message.failed
    assert message.contents[0].text == "[]"


async def test_search_requires_query(
    run_web: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_web({"action": "search"})

    assert message.failed
    assert "search action requires query" in message.contents[0].text


async def test_fetch(
    run_web: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    web = web_registry.resolve()
    assert isinstance(web, MockWeb)

    message = await run_web({"action": "fetch", "url": "https://example.com"})

    assert not message.failed
    assert message.tool_name == "web"
    assert message.contents[0].text == "# Example\n\nFetched content."


async def test_fetch_requires_url(
    run_web: Callable[[dict[str, Any]], Awaitable[ToolMessage]],
) -> None:
    message = await run_web({"action": "fetch"})

    assert message.failed
    assert "fetch action requires url" in message.contents[0].text
