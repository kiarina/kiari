from dataclasses import dataclass

from PIL import Image

from .monitor_snapshot import MonitorSnapshot


@dataclass
class MultipleMonitorCapture:
    """
    Multiple monitor capture information
    """

    monitor_snapshots: list[MonitorSnapshot]
    """
    List of monitor snapshots

    0 index represents the entire screen,
    subsequent indices represent individual monitors.
    """

    full_desktop_screenshot: Image.Image
    """Screenshot image of all monitors"""

    @property
    def monitor_count(self) -> int:
        # Exclude the first monitor representing the entire screen
        return len(self.monitor_snapshots) - 1

    def get_monitor_snapshot(self, monitor_index: int) -> MonitorSnapshot:
        if monitor_index >= len(self.monitor_snapshots):
            raise IndexError("Monitor index is out of range.")

        return self.monitor_snapshots[monitor_index]
