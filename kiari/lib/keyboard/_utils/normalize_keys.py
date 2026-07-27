from collections.abc import Sequence

from .normalize_key import normalize_key


def normalize_keys(keys: Sequence[str]) -> Sequence[str]:
    """
    Normalize multiple keys
    """
    return [normalize_key(key) for key in keys]
