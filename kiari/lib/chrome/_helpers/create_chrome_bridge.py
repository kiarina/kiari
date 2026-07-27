from chrome_bridge_sdk import ChromeBridge  # type: ignore[import-untyped]

from .._settings import settings_manager


def create_chrome_bridge() -> ChromeBridge:
    settings = settings_manager.settings
    return ChromeBridge(
        host=settings.host,
        port=settings.port,
        startup_timeout=settings.startup_timeout,
        session_idle_ttl=settings.session_idle_ttl,
        session_max_lifetime=settings.session_max_lifetime,
    )
