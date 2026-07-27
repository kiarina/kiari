from io import BytesIO

from kiarina.utils.mime import MIMEBlob

from .._schemas.multiple_monitor_capture import MultipleMonitorCapture
from .calc_scale_ratio import calc_scale_ratio
from .get_image import get_image


def get_screenshot(capture: MultipleMonitorCapture, monitor_index: int) -> MIMEBlob:
    """
    Get a resized monitor screenshot for LLM
    """
    image = get_image(capture, monitor_index)
    scale_ratio = calc_scale_ratio(capture, monitor_index)

    resized_image = image.resize((int(image.width * scale_ratio), int(image.height * scale_ratio)))

    with BytesIO() as output:
        resized_image.save(output, format="JPEG")
        return MIMEBlob(mime_type="image/jpeg", raw_data=output.getvalue())
