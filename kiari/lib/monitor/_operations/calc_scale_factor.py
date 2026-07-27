from .._schemas.multiple_monitor_capture import MultipleMonitorCapture


def calc_scale_factor(capture: MultipleMonitorCapture) -> float:
    """
    Calculate ratio of physical size to logical size (physical pixels / logical pixels)

    For Retina displays, this will be 2.0.
    """
    entire_monitor = capture.monitor_snapshots[0]
    return capture.full_desktop_screenshot.size[0] / entire_monitor.bounds.width
