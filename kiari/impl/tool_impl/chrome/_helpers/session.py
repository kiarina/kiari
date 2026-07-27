from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from chrome_bridge_sdk import (  # type: ignore[import-untyped]
    ChromeBridgeError,
    ChromeBridgeSession,
)
from kiarina.agi.tool import ToolError

from kiari.lib.chrome import create_chrome_bridge, settings_manager


@asynccontextmanager
async def chrome_session() -> AsyncIterator[ChromeBridgeSession]:
    try:
        bridge = create_chrome_bridge()
        async with bridge.session(
            wait_timeout=settings_manager.settings.session_wait_timeout
        ) as session:
            yield session
    except ChromeBridgeError as error:
        raise ToolError(
            "Chrome Bridge request failed: "
            f"{error} (code={error.code}, retryable={error.retryable}, "
            f"outcome_unknown={error.outcome_unknown})"
        ) from error
