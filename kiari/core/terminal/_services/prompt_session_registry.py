from pathlib import Path
from typing import Any

from kiarina.utils.object_registry import ObjectRegistry
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from kiari.core.paths import get_prompt_session_history_file_path

from .._utils.create_prompt_toolkit_io import create_prompt_toolkit_io


def _factory(name: str, config: dict[str, Any]) -> PromptSession[str]:
    config = config.copy()

    if history_file_path := config.pop("history_file_path", None):
        _ensure_history_file_exists(history_file_path)
        config["history"] = FileHistory(str(history_file_path))

    return PromptSession(**{**config, **create_prompt_toolkit_io()})


def _ensure_history_file_exists(file_path: str) -> None:
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


prompt_session_registry = ObjectRegistry[PromptSession[str], dict[str, Any]](
    expected_type=PromptSession,
    object_label="PromptSession",
    get_default=lambda: "default",
    get_presets=lambda: {
        "default": {
            "history_file_path": str(get_prompt_session_history_file_path()),
        },
        "no_history": {},
    },
    factory=_factory,
)
