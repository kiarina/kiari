from rich_click.utils import OptionGroupDict

SCHEDULE_OPTION_GROUP: OptionGroupDict = {
    "name": "Schedule",
    "options": [
        "--interval",
        "--cron",
        "--schedule-handler",
        "--skip-if-no-events",
    ],
}
