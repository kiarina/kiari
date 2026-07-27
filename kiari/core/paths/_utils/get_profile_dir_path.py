from pathlib import Path

from .get_profiles_dir_path import get_profiles_dir_path


def get_profile_dir_path(profile_name: str) -> Path:
    return get_profiles_dir_path() / profile_name
