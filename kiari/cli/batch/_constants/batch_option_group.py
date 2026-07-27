from rich_click.utils import OptionGroupDict

BATCH_OPTION_GROUP: OptionGroupDict = {
    "name": "Batch",
    "options": [
        "--attachment",
        "--stdin",
        "--batch-handler",
        "--output-text",
    ],
}
