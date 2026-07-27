from typing import Any

import httpx

from kiari.lib.web import BaseWeb, WebSearchResult

from .._settings import KiapiWebSettings


class KiapiWeb(BaseWeb):
    def __init__(self, settings: KiapiWebSettings) -> None:
        super().__init__()
        self.settings: KiapiWebSettings = settings

    async def search(self, query: str) -> list[WebSearchResult]:
        async with httpx.AsyncClient(
            base_url=self.settings.kiapi_base_url,
            timeout=self.settings.timeout,
        ) as client:
            response = await client.post(
                "/v1/web/search",
                json={"query": query},
            )
            response.raise_for_status()

        payload = response.json()
        return [self._create_search_result(result) for result in payload.get("results", [])]

    async def fetch(self, url: str) -> str:
        async with httpx.AsyncClient(
            base_url=self.settings.kiapi_base_url,
            timeout=self.settings.timeout,
        ) as client:
            response = await client.get(
                "/v1/web/fetch",
                params={"url": url},
                headers={"Accept": "text/markdown"},
            )
            response.raise_for_status()

        return response.text

    @staticmethod
    def _create_search_result(result: dict[str, Any]) -> WebSearchResult:
        return WebSearchResult(
            title=str(result.get("title") or ""),
            url=str(result.get("url") or ""),
            content=str(result.get("content") or ""),
        )
