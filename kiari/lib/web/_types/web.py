from typing import Protocol, runtime_checkable

from .._schemas.web_search_result import WebSearchResult
from .web_name import WebName


@runtime_checkable
class Web(Protocol):
    name: WebName

    async def search(self, query: str) -> list[WebSearchResult]: ...

    async def fetch(self, url: str) -> str: ...
