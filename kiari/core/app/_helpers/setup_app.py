from contextlib import suppress
from pathlib import Path

from kiarina.utils.app import AppAlreadyConfiguredError, configure, settings_manager as app_settings


def setup_app() -> None:
    with suppress(AppAlreadyConfiguredError):
        configure(app_author="kiarina", app_name="kiari")

    root = Path.home() / ".kiari"
    app_settings.set_cli_args("user_cache_dir", str(root / "cache"))
    app_settings.set_cli_args("user_config_dir", str(root / "config"))
    app_settings.set_cli_args("user_data_dir", str(root / "data"))
