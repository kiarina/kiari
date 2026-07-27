import os
from pathlib import Path

from .._constants import FASTAPI_STARTUP_FILE_ENV_VAR
from .._schemas.fastapi_startup_options import FastAPIStartupOptions


def load_fastapi_startup_options() -> FastAPIStartupOptions:
    file_path = os.environ.get(FASTAPI_STARTUP_FILE_ENV_VAR)

    if not file_path:
        raise RuntimeError(f"{FASTAPI_STARTUP_FILE_ENV_VAR} is not set")

    path = Path(file_path)

    if not path.is_file():
        raise RuntimeError(f"FastAPI startup file does not exist: {path}")

    try:
        return FastAPIStartupOptions.model_validate_json(path.read_text())
    except Exception as e:
        raise RuntimeError(f"Invalid FastAPI startup file: {path}") from e
