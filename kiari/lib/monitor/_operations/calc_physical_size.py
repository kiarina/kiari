from .._schemas.multiple_monitor_capture import MultipleMonitorCapture
from .._schemas.size import Size
from .calc_scale_factor import calc_scale_factor


def calc_physical_size(capture: MultipleMonitorCapture, monitor_index: int) -> Size:
    """
    Calculate physical size of the specified monitor.

    Physical size refers to the size in the screenshot image.
    """
    scale_factor = calc_scale_factor(capture)
    snapshot = capture.get_monitor_snapshot(monitor_index).bounds
    return Size(
        int(snapshot.width * scale_factor),
        int(snapshot.height * scale_factor),
    )
