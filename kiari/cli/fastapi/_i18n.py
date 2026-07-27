from kiarina.i18n import I18n


class FastAPII18n(I18n, scope="kiari.cli.fastapi"):
    command_help: str = "Run kiari as a FastAPI application."
    path_help: str = "Agent API endpoint path."
    host_help: str = "Host address for the uvicorn server."
    port_help: str = "Port for the uvicorn server."
    workers_help: str = "Number of worker processes. When omitted, run with automatic reload."
    handler_help: str = (
        "FastAPIHandler name or config string. Example: 'vanilla' or 'vanilla?key=value'."
    )
    authenticator_help: str = (
        "Authenticator name or config string. Example: 'none' or 'bearer?api_key=secret'."
    )
