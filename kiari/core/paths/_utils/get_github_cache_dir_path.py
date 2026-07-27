from pathlib import Path

from kiarina.utils.app import user_directory


def get_github_cache_dir_path() -> Path:
    return user_directory.get_user_cache_dir() / "github_files"
