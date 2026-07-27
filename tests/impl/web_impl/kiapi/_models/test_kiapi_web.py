from collections.abc import Awaitable
from typing import TypeVar

import httpx
import pytest

from kiari.impl.web_impl.kiapi import create_kiapi_web
from kiari.lib.web import WebSearchResult

T = TypeVar("T")


async def _call_or_skip[T](request: Awaitable[T]) -> T:
    try:
        return await request
    except httpx.RequestError as error:
        pytest.skip(f"kiapi Web backend is not reachable: {error}")
    except httpx.HTTPStatusError as error:
        if error.response.is_server_error:
            pytest.skip(
                f"kiapi Web backend is not available: status code {error.response.status_code}"
            )
        raise


async def test_search() -> None:
    web = create_kiapi_web()

    results = await _call_or_skip(web.search("Python programming language"))

    assert results
    assert all(isinstance(result, WebSearchResult) for result in results)
    assert all(result.url for result in results)


async def test_fetch() -> None:
    web = create_kiapi_web()

    markdown = await _call_or_skip(web.fetch("https://example.com/"))

    assert "Example Domain" in markdown


async def test_search_validation_error() -> None:
    web = create_kiapi_web()

    with pytest.raises(httpx.HTTPStatusError) as error_info:
        await web.search("")

    assert error_info.value.response.status_code == 422


async def test_fetch_validation_error() -> None:
    web = create_kiapi_web()

    with pytest.raises(httpx.HTTPStatusError) as error_info:
        await web.fetch("not-a-url")

    assert error_info.value.response.status_code == 422
