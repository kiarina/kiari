from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings_manager import SettingsManager


class SubprocessSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="KIARI_SUBPROCESS_",
        extra="ignore",
    )

    wait_time: float = 60.0
    """Foreground wait time for commands (seconds)"""

    encoding: str = "utf-8"
    """Encoding used for command execution input/output"""

    max_buffer_size: int = 10 * 1024 * 1024  # 10MB
    """Maximum size of the buffer for holding standard output (bytes)"""

    cleanup_completed_sessions_after: int = 3600  # 1 hour
    """Time until completed sessions are cleaned up (seconds)"""

    cleanup_loop_interval: int = 300  # 5 minutes
    """Execution interval of the cleanup loop (seconds)"""


settings_manager = SettingsManager(SubprocessSettings)
