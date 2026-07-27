from rich_click.utils import OptionGroupDict

FASTAPI_OPTION_GROUP: OptionGroupDict = {
    "name": "FastAPI",
    "options": [
        "--fastapi-path",
        "--fastapi-host",
        "--fastapi-port",
        "--fastapi-workers",
        "--fastapi-handler",
        "--fastapi-authenticator",
    ],
}
