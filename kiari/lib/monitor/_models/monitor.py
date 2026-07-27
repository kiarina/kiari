from kiarina.utils.mime import MIMEBlob

from .._operations.calc_physical_size import calc_physical_size
from .._operations.calc_scale_factor import calc_scale_factor
from .._operations.calc_scale_ratio import calc_scale_ratio
from .._operations.capture_monitor import capture_monitor
from .._operations.get_offset_vector import get_offset_vector
from .._operations.get_screenshot import get_screenshot
from .._schemas.multiple_monitor_capture import MultipleMonitorCapture
from .._views.monitor_info import MonitorInfo


class Monitor:
    """
    Monitor management class

    >>> monitor = Monitor()
    >>> for index in monitor.monitor_indexes:
    ...     screenshot = monitor.get_screenshot(index)
    ...     monitor_info = monitor.get_monitor_info(index)
    >>> monitor.refresh()
    """

    def __init__(self) -> None:
        self._multiple_monitor_capture: MultipleMonitorCapture | None = None

    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def multiple_monitor_capture(self) -> MultipleMonitorCapture:
        if self._multiple_monitor_capture is None:
            self._multiple_monitor_capture = capture_monitor()

        return self._multiple_monitor_capture

    @property
    def scale_factor(self) -> float:
        return calc_scale_factor(self.multiple_monitor_capture)

    @property
    def monitor_count(self) -> int:
        return self.multiple_monitor_capture.monitor_count

    @property
    def monitor_indexes(self) -> list[int]:
        return list(range(1, self.monitor_count + 1))

    # --------------------------------------------------
    # Methods
    # --------------------------------------------------

    def refresh(self) -> None:
        self._multiple_monitor_capture = capture_monitor()

    def get_monitor_info(self, monitor_index: int) -> MonitorInfo:
        capture = self.multiple_monitor_capture
        snapshot = capture.get_monitor_snapshot(monitor_index)

        return MonitorInfo(
            index=monitor_index,
            bounds=snapshot.bounds,
            physical_size=calc_physical_size(capture, monitor_index),
            scale_ratio=calc_scale_ratio(capture, monitor_index),
            offset_vector=get_offset_vector(capture, monitor_index),
        )

    def get_screenshot(self, monitor_index: int) -> MIMEBlob:
        return get_screenshot(self.multiple_monitor_capture, monitor_index)
