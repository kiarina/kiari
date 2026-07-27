from .._schemas.multiple_monitor_capture import MultipleMonitorCapture
from .._schemas.point import Point


def get_offset_vector(capture: MultipleMonitorCapture, monitor_index: int) -> Point:
    """
    Get the offset vector to convert logical coordinates to physical coordinates

    Adjusts so that the top-left corner of the screenshot becomes (0, 0).
    """
    snapshot = capture.get_monitor_snapshot(monitor_index)
    return Point(
        x=-snapshot.bounds.left,
        y=-snapshot.bounds.top,
    )
