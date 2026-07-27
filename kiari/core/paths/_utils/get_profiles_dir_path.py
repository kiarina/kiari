from pathlib import Path

from kiarina.utils.app import user_directory


def get_profiles_dir_path() -> Path:
    return user_directory.get_user_config_dir() / "profiles"
