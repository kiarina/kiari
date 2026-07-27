from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from .._types.schedule_type import ScheduleType


@dataclass(frozen=True)
class Scheduler:
    schedule_type: ScheduleType
    get_next_time: Callable[[datetime], datetime]
