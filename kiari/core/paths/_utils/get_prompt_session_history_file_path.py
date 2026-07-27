from pathlib import Path

from kiarina.utils.app import user_directory


def get_prompt_session_history_file_path() -> Path:
    return user_directory.get_user_data_dir() / "prompt_session_history.txt"
