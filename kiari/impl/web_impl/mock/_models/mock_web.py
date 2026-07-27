from kiari.lib.web import BaseWeb, WebSearchResult

from .._settings import MockWebSettings


class MockWeb(BaseWeb):
    def __init__(self, settings: MockWebSettings) -> None:
        super().__init__()
        self.settings: MockWebSettings = settings

    async def search(self, query: str) -> list[WebSearchResult]:
        return [result.model_copy(deep=True) for result in self.settings.search_results]

    async def fetch(self, url: str) -> str:
        return self.settings.fetch_markdown
