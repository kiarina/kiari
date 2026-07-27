from dataclasses import dataclass

from .rect import Rect


@dataclass
class MonitorSnapshot:
    """
    Monitor snapshot information
    """

    index: int
    """Monitor index"""

    bounds: Rect
    """Monitor bounds"""
