from pathlib import Path

from kiarina.utils.app import user_directory


def get_github_trusted_sources_file_path() -> Path:
    return user_directory.get_user_data_dir() / "trusted_sources.yaml"
