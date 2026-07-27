from pathlib import Path

from kiarina.utils.app import user_directory


def get_config_file_path() -> Path:
    return user_directory.get_user_config_dir() / "config.yaml"
