from typing import Any

from .._models.mock_web import MockWeb
from .._settings import MockWebSettings, settings_manager


def create_mock_web(**kwargs: Any) -> MockWeb:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = MockWebSettings.model_validate({**settings.model_dump(), **kwargs})

    return MockWeb(settings)
