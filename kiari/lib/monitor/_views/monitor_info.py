from dataclasses import dataclass

from .._schemas.point import Point
from .._schemas.rect import Rect
from .._schemas.size import Size


@dataclass
class MonitorInfo:
    index: int
    bounds: Rect
    physical_size: Size
    scale_ratio: float
    offset_vector: Point
