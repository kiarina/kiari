from .._constants.max_scaling_targets import MAX_SCALING_TARGETS
from .._schemas.multiple_monitor_capture import MultipleMonitorCapture
from .calc_physical_size import calc_physical_size


def calc_scale_ratio(capture: MultipleMonitorCapture, monitor_index: int) -> float:
    """
    Calculate scale ratio to fit the monitor to the nearest target resolution.

    Select the target resolution with the closest aspect ratio from the list,
    and calculate the ratio between the physical size of the screen and the target resolution.
    Target resolution refers to the resolution at which the LLM does not perform automatic scaling.
    """
    screenshot = capture.get_monitor_snapshot(monitor_index)

    aspect_ratio = screenshot.bounds.size.aspect_ratio
    physical_size = calc_physical_size(capture, monitor_index)

    # Get the target resolution with the closest aspect ratio
    target_resolution = min(
        MAX_SCALING_TARGETS.values(),
        key=lambda x: abs(x.aspect_ratio - aspect_ratio),
    )

    if aspect_ratio > target_resolution.aspect_ratio:
        # For landscape orientation, fit to width
        return target_resolution.width / physical_size.width
    else:
        # For portrait orientation, fit to height
        return target_resolution.height / physical_size.height
