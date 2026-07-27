from pathlib import Path

from .get_profile_dir_path import get_profile_dir_path


def get_profile_run_spec_file_path(profile_name: str) -> Path:
    return get_profile_dir_path(profile_name) / "run_spec.yaml"
