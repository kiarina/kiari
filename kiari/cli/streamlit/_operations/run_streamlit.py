import os
import subprocess
import sys
import tempfile
from importlib.resources import files
from pathlib import Path

from kiari.core.profile import ProfileName, RunOptions
from kiari.streamlit import StreamlitStartupOptions
from kiari.streamlit._constants import STREAMLIT_STARTUP_FILE_ENV_VAR


def run_streamlit(profile_name: ProfileName, run_options: RunOptions) -> None:
    startup_options = StreamlitStartupOptions(
        profile_name=profile_name,
        run_options=run_options,
    )
    previous_startup_file = os.environ.get(STREAMLIT_STARTUP_FILE_ENV_VAR)

    with tempfile.TemporaryDirectory(prefix="kiari-streamlit-") as temporary_dir:
        startup_file = Path(temporary_dir) / "startup.json"
        file_descriptor = os.open(startup_file, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)

        with os.fdopen(file_descriptor, "w") as file:
            file.write(startup_options.model_dump_json())

        app_path = files("kiari.streamlit").joinpath("app.py")
        env = {**os.environ, STREAMLIT_STARTUP_FILE_ENV_VAR: str(startup_file)}
        command = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(app_path),
            "--server.address",
            run_options.streamlit_host,
            "--server.port",
            str(run_options.streamlit_port),
            "--server.headless",
            str(run_options.streamlit_headless).lower(),
        ]

        try:
            subprocess.run(command, env=env, check=True)
        finally:
            if previous_startup_file is None:
                os.environ.pop(STREAMLIT_STARTUP_FILE_ENV_VAR, None)
            else:
                os.environ[STREAMLIT_STARTUP_FILE_ENV_VAR] = previous_startup_file
