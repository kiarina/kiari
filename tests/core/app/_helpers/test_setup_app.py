from pathlib import Path

from kiarina.utils.app import settings_manager as app_settings, user_directory

from kiari.core.app._helpers.setup_app import setup_app


def test_setup_app_groups_user_directories_under_kiari_home(monkeypatch, tmp_path: Path) -> None:
    previous_cli_args = app_settings.cli_args
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path))

    try:
        setup_app()

        root = tmp_path / ".kiari"
        assert user_directory.get_user_config_dir() == root / "config"
        assert user_directory.get_user_data_dir() == root / "data"
        assert user_directory.get_user_cache_dir() == root / "cache"
    finally:
        app_settings.cli_args = previous_cli_args
