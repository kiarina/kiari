from dataclasses import dataclass

from .point import Point
from .size import Size


@dataclass
class Rect:
    """
    Rectangle data class
    """

    origin: Point
    """Top-left point of the rectangle"""

    size: Size
    """Size of the rectangle"""

    @property
    def width(self) -> int:
        """
        Width of the rectangle
        """
        return self.size.width

    @property
    def height(self) -> int:
        """
        Height of the rectangle
        """
        return self.size.height

    @property
    def left(self) -> int:
        """
        Left edge coordinate
        """
        return self.origin.x

    @property
    def top(self) -> int:
        """
        Top edge coordinate
        """
        return self.origin.y

    @property
    def right(self) -> int:
        """
        Right edge coordinate
        """
        return self.left + self.width

    @property
    def bottom(self) -> int:
        """
        Bottom edge coordinate
        """
        return self.top + self.height
