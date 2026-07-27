import os
from pathlib import Path

from .._constants import STREAMLIT_STARTUP_FILE_ENV_VAR
from .._schemas.streamlit_startup_options import StreamlitStartupOptions


def load_streamlit_startup_options() -> StreamlitStartupOptions:
    file_path = os.environ.get(STREAMLIT_STARTUP_FILE_ENV_VAR)

    if not file_path:
        raise RuntimeError(f"{STREAMLIT_STARTUP_FILE_ENV_VAR} is not set")

    path = Path(file_path)

    if not path.is_file():
        raise RuntimeError(f"Streamlit startup file does not exist: {path}")

    try:
        return StreamlitStartupOptions.model_validate_json(path.read_text())
    except Exception as e:
        raise RuntimeError(f"Invalid Streamlit startup file: {path}") from e
