from PIL import Image

from .._schemas.multiple_monitor_capture import MultipleMonitorCapture
from .calc_scale_factor import calc_scale_factor
from .get_offset_vector import get_offset_vector


def get_image(capture: MultipleMonitorCapture, monitor_index: int) -> Image.Image:
    """
    Get the screenshot image of the specified monitor
    """
    if monitor_index == 0:
        return capture.full_desktop_screenshot

    bounds = capture.get_monitor_snapshot(monitor_index).bounds
    offset_vector = get_offset_vector(capture, 0)  # Overall offset
    scale_factor = calc_scale_factor(capture)

    crop_box = (
        int((bounds.left + offset_vector.x) * scale_factor),
        int((bounds.top + offset_vector.y) * scale_factor),
        int((bounds.right + offset_vector.x) * scale_factor),
        int((bounds.bottom + offset_vector.y) * scale_factor),
    )

    return capture.full_desktop_screenshot.crop(crop_box)
