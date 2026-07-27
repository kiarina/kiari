import pytest
from pydantic import ValidationError

from kiari.lib.web import WebSearchResult


def test_web_search_result_is_frozen() -> None:
    result = WebSearchResult(
        title="Example",
        url="https://example.com",
        content="Example content",
    )

    assert result.model_dump() == {
        "title": "Example",
        "url": "https://example.com",
        "content": "Example content",
    }

    with pytest.raises(ValidationError):
        result.title = "Updated"
