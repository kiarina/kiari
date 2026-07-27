from typing import Any

from .._schemas.web_search_result import WebSearchResult
from .._types.web import Web
from .._types.web_name import WebName


class BaseWeb(Web):
    def __init__(self, **kwargs: Any) -> None:
        self.init_kwargs: dict[str, Any] = kwargs
        self._name: WebName | None = None

    @property
    def name(self) -> WebName:
        if not self._name:  # pragma: no cover
            raise AssertionError("Web name not set")

        return self._name

    @name.setter
    def name(self, value: WebName) -> None:
        self._name = value

    async def search(self, query: str) -> list[WebSearchResult]:
        raise NotImplementedError

    async def fetch(self, url: str) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        return self.__class__.__name__
