from datetime import datetime, timedelta

from croniter import croniter

from .._schemas.scheduler import Scheduler
from .._utils.parse_duration import parse_duration


def create_scheduler(
    *,
    interval: str | None,
    cron: str | None,
    current_time: datetime,
) -> Scheduler:
    if interval and cron:
        raise ValueError("Schedule mode accepts either --interval or --cron, not both.")

    if interval:
        interval_seconds = parse_duration(interval)

        def get_next_time(current_time: datetime) -> datetime:
            return current_time + timedelta(seconds=interval_seconds)

        return Scheduler("interval", get_next_time)

    if cron:
        cron_iterator = croniter(cron, current_time)

        def get_next_time(current_time: datetime) -> datetime:
            return cron_iterator.get_next(datetime)

        return Scheduler("cron", get_next_time)

    raise ValueError("Schedule mode requires --interval or --cron.")
