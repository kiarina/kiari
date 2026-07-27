from typing import Any

from .._models.kiapi_web import KiapiWeb
from .._settings import KiapiWebSettings, settings_manager


def create_kiapi_web(**kwargs: Any) -> KiapiWeb:
    settings = settings_manager.get_settings()

    if kwargs:
        settings = KiapiWebSettings.model_validate({**settings.model_dump(), **kwargs})

    return KiapiWeb(settings)
