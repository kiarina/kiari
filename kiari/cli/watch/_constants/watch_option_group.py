from rich_click.utils import OptionGroupDict

WATCH_OPTION_GROUP: OptionGroupDict = {
    "name": "Watch",
    "options": [
        "--watch-handler",
        "--watch-max-concurrent",
        "--watch-queue-size",
        "--watch-queue-put-timeout",
    ],
}
