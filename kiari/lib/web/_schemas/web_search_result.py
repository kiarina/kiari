from pydantic import BaseModel


class WebSearchResult(BaseModel, frozen=True):
    title: str
    url: str
    content: str
