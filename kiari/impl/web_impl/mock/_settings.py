from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager

from kiari.lib.web import WebSearchResult


class MockWebSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI2_WEB_IMPL_MOCK_",
        extra="ignore",
    )

    search_results: list[WebSearchResult] = Field(default_factory=list)
    fetch_markdown: str = ""


settings_manager = SettingsManager(MockWebSettings)
