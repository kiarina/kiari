from importlib import import_module
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._utils.load_audio_samples import load_audio_samples
    from ._utils.play_audio import play_audio

__all__ = [
    "load_audio_samples",
    "play_audio",
]


def __getattr__(name: str) -> object:
    if name not in __all__:
        raise AttributeError(f"module {__name__} has no attribute {name}")

    module_map = {
        "load_audio_samples": "._utils.load_audio_samples",
        "play_audio": "._utils.play_audio",
    }

    globals()[name] = getattr(import_module(module_map[name], __name__), name)
    return globals()[name]
