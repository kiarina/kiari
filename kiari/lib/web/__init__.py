from ._instances.web_registry import web_registry
from ._models.base_web import BaseWeb
from ._schemas.web_search_result import WebSearchResult
from ._settings import WebSettings, settings_manager
from ._types.web import Web
from ._types.web_name import WebName
from ._types.web_specifier import WebSpecifier

__all__ = [
    # ._instances
    "web_registry",
    # ._models
    "BaseWeb",
    # ._schemas
    "WebSearchResult",
    # ._settings
    "WebSettings",
    "settings_manager",
    # ._types
    "Web",
    "WebName",
    "WebSpecifier",
]
