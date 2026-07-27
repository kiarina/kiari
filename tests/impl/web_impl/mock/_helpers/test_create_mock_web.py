from kiari.impl.web_impl.mock import MockWeb, create_mock_web


def test_create_mock_web() -> None:
    web = create_mock_web(
        search_results=[
            {
                "title": "Example",
                "url": "https://example.com",
                "content": "Example content",
            }
        ],
        fetch_markdown="# Example",
    )

    assert isinstance(web, MockWeb)
    assert web.settings.search_results[0].title == "Example"
    assert web.settings.fetch_markdown == "# Example"
