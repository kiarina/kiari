from kiari.impl.web_impl.mock import MockWeb, MockWebSettings
from kiari.lib.web import WebSearchResult


async def test_mock_web() -> None:
    configured_result = WebSearchResult(
        title="Example",
        url="https://example.com",
        content="Example content",
    )
    web = MockWeb(
        MockWebSettings(
            search_results=[configured_result],
            fetch_markdown="# Example",
        )
    )

    results = await web.search("ignored query")

    assert results == [configured_result]
    assert results is not web.settings.search_results
    assert results[0] is not web.settings.search_results[0]
    assert await web.fetch("https://ignored.example") == "# Example"
